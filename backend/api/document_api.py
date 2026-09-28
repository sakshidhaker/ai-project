"""
STUDENT CODE MAP
============================================================
FILE: backend/api/document_api.py
PURPOSE:
    Run the Creator request: fresh RAG -> Qwen -> validation -> one retry -> file.

IMPORTANT:
    The retry performs a NEW RAG search too. It does not reuse the first attempt's
    retrieved context.

CONNECTIONS:
    frontend/app.js
        -> POST /api/generate
        -> this function
        -> rag.py
        -> ai.py
        -> validator.py
        -> pdf_generator.py / docx_generator.py
============================================================
"""

# secrets creates a unique filename for each generated artifact.
import secrets

# Path is used for a final safety check on the generated file.
from pathlib import Path

# Blueprint defines the route; jsonify returns JSON; request reads browser form data.
from flask import Blueprint, jsonify, request

# AI builds the generation prompt, runs Qwen, and identifies Python mode.
from backend.ai import (
    build_document_prompt,
    generate_text,
    looks_like_python_program_request,
)

# The decorator requires a signed-in user.
from backend.auth import login_required

# These settings keep prompts/files within the simple project limits.
from backend.config import (
    ALLOWED_ARTIFACT_TYPES,
    GENERATED_DIR,
    MAX_PROMPT_LENGTH,
    MODEL_NAME,
)

# Separate renderers keep PDF and DOCX logic easy to teach.
from backend.docx_generator import create_docx
from backend.pdf_generator import create_pdf

# AppError converts expected failures into readable API responses.
from backend.exceptions import AppError

# RAG performs a fresh semantic search for every generation attempt.
from backend.rag import get_context, search_knowledge

# Validator checks the generated text before a downloadable file is created.
from backend.validator import validate_generated_text

document_api = Blueprint("document_api", __name__, url_prefix="/api")


def _input():
    """
    PURPOSE:
        Read and validate the Creator form values.

    CONNECTION:
        generate() calls this before RAG or Qwen work.
    """
    prompt = str(request.form.get("prompt", "")).strip()
    artifact_type = str(
        request.form.get("artifact_type", "pdf")
    ).strip().lower()

    if len(prompt) < 5:
        return None, None, "Tell the engine what to create."

    if len(prompt) > MAX_PROMPT_LENGTH:
        return None, None, (
            f"Keep the request under {MAX_PROMPT_LENGTH} characters."
        )

    if artifact_type not in ALLOWED_ARTIFACT_TYPES:
        return None, None, "Choose PDF or DOCX."

    return prompt, artifact_type, None


def _filename(artifact_type):
    """
    PURPOSE:
        Create a collision-resistant output filename.

    CONNECTION:
        generate() calls this after validation succeeds.
    """
    extension = ".pdf" if artifact_type == "pdf" else ".docx"
    return "ai_creator_" + secrets.token_hex(6) + extension


@document_api.post("/generate")
@login_required
def generate(user):
    """
    PURPOSE:
        Run one complete Creator request.

    CONNECTION:
        frontend/app.js -> /api/generate -> this function.

    FLOW:
        input -> FRESH RAG -> Qwen -> validator
        -> if needed: FRESH RAG -> Qwen -> validator
        -> PDF/DOCX
    """
    prompt, artifact_type, error = _input()

    if error:
        return jsonify({
            "success": False,
            "stage": "input",
            "message": error,
        }), 400

    stages = [{
        "stage": "input",
        "message": "Request received",
    }]

    lowered = prompt.lower()
    other_languages = (
        "c++", "cpp", "java", "javascript",
        "typescript", "rust", "golang",
    )

    is_programming_request = any(
        word in lowered
        for word in (
            "function", "program", "code", "script",
            "game", "class", "calculator", "tool",
        )
    )

    is_other_language_program = (
        any(language in lowered for language in other_languages)
        and is_programming_request
    )

    if is_other_language_program and not looks_like_python_program_request(prompt):
        return jsonify({
            "success": False,
            "stage": "scope",
            "message": (
                "This teaching edition's reliable program-generation path is Python."
            ),
            "suggestion": (
                "Ask for the program in Python, or use Chat for another language."
            ),
            "stages": stages,
        }), 422

    try:
        # ------------------------------------------------------------
        # ATTEMPT 1: always perform a NEW semantic search.
        # ------------------------------------------------------------
        first_results = search_knowledge(
            prompt,
            top_k=2 if looks_like_python_program_request(prompt) else 3,
            purpose="creator",
        )
        first_context = get_context(
            first_results,
            max_chars=2800 if looks_like_python_program_request(prompt) else 5200,
        )

        stages.append({
            "stage": "rag",
            "message": (
                f"Fresh search retrieved {len(first_results)} knowledge chunks"
            ),
        })

        generation_prompt = build_document_prompt(prompt, first_context)
        output = generate_text(
            generation_prompt,
            max_tokens=700,
            temperature=0.20 if looks_like_python_program_request(prompt) else 0.25,
        )

        stages.append({
            "stage": "qwen",
            "message": "Generated document text",
        })

        valid, reason = validate_generated_text(
            prompt,
            output,
            document=True,
        )

        # ------------------------------------------------------------
        # ATTEMPT 2: if validation fails, SEARCH AGAIN.
        # This is intentionally not a reuse of first_context.
        # ------------------------------------------------------------
        if not valid:
            second_results = search_knowledge(
                prompt,
                top_k=2 if looks_like_python_program_request(prompt) else 3,
                purpose="creator",
            )
            second_context = get_context(
                second_results,
                max_chars=2800 if looks_like_python_program_request(prompt) else 5200,
            )

            retry_prompt = build_document_prompt(
                prompt,
                second_context,
            )
            retry_prompt += (
                "\n\nVALIDATION FEEDBACK:\n"
                + reason
                + "\nFix only this problem and return the complete document."
            )

            output = generate_text(
                retry_prompt,
                max_tokens=700,
                temperature=0.10 if looks_like_python_program_request(prompt) else 0.20,
            )

            stages.append({
                "stage": "retry",
                "message": (
                    f"Fresh search retrieved {len(second_results)} chunks for the retry"
                ),
            })

            valid, reason = validate_generated_text(
                prompt,
                output,
                document=True,
            )

        if not valid:
            return jsonify({
                "success": False,
                "stage": "validation",
                "message": reason,
                "suggestion": "Try a short, specific Python request.",
                "stages": stages,
            }), 422

        stages.append({
            "stage": "validator",
            "message": "Content passed validation",
        })

        filename = _filename(artifact_type)

        if artifact_type == "pdf":
            path = create_pdf(output, filename)
        else:
            path = create_docx(output, filename)

        path = Path(path).resolve()
        root = Path(GENERATED_DIR).resolve()

        if (
            root not in path.parents
            or not path.is_file()
            or path.stat().st_size == 0
        ):
            raise RuntimeError(
                "The generated file failed the final file check."
            )

        stages.append({
            "stage": "file",
            "message": artifact_type.upper() + " created",
        })

        title = output.splitlines()[0].lstrip("# ").strip()
        if not title:
            title = "AI Creator Document"

        return jsonify({
            "success": True,
            "title": title,
            "model": MODEL_NAME,
            "artifact_type": artifact_type,
            "validation": "Passed",
            "content_preview": output[:2500],
            "artifact_url": "/api/download/" + path.name,
            "stages": stages,
            "rag_used": bool(first_results),
            "sources": [item["source"] for item in first_results],
        })

    except AppError as exc:
        return jsonify({
            "success": False,
            "stage": exc.stage,
            "message": exc.message,
            "suggestion": exc.suggestion,
            "stages": stages,
        }), 500

    except Exception as exc:
        return jsonify({
            "success": False,
            "stage": "generation",
            "message": "Something went wrong while creating the file.",
            "suggestion": str(exc),
            "stages": stages,
        }), 500
