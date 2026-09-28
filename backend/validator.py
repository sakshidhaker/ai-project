"""
STUDENT CODE MAP
============================================================
FILE: backend/validator.py
PURPOSE:
    Perform a few small, explainable checks before a generated document becomes a file.

CHECKS:
    1. Empty output
    2. Minimum useful length
    3. Basic document structure
    4. Topic relationship
    5. Python syntax for explicit Python-programming requests

CONNECTION:
    document_api.py -> validate_generated_text() -> one retry when needed

EDIT HERE:
    Change thresholds or add one simple check. Avoid building a large repair framework.
============================================================
"""

# ast parses real Python syntax without executing the generated program.
import ast

# re gives us a small, readable way to extract words and fenced code blocks.
import re

_STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "is", "are", "what", "how", "why", "explain", "create", "make", "write",
    "about", "please", "me", "my", "this", "that", "from", "into", "using",
    "beginner", "friendly", "report", "document", "show", "tell", "can", "could",
}


def _words(text):
    """
    PURPOSE: Turn text into simple lower-case words for the topic check.
    CONNECTION: _topic_words() and _topic_matches() use this helper.
    """
    return re.findall(r"[a-zA-Z0-9]{3,}", str(text).lower())


def _topic_words(request):
    """
    PURPOSE: Remove common instruction words so topic matching focuses on meaningful words.
    CONNECTION: validate_generated_text() -> _topic_matches().
    """
    result = []
    for word in _words(request):
        if word not in _STOP_WORDS and word not in result:
            result.append(word)
    return result


def _topic_matches(request, output):
    """
    PURPOSE: Check whether at least one meaningful request word appears in the generated text.
    CONNECTION: Used by the final content validator.
    NOTE: This is a sanity check, not a claim that word matching proves factual correctness.
    """
    topics = _topic_words(request)
    if not topics:
        return True

    output_words = set(_words(output))
    for topic in topics:
        if topic in output_words:
            return True
        if len(topic) >= 5:
            prefix = topic[:5]
            if any(word.startswith(prefix) for word in output_words):
                return True
    return False


def _looks_like_python_program_request(request):
    """
    PURPOSE: Detect explicit requests for Python code without creating a general language detector.
    CONNECTION: validate_generated_text() uses this before the Python syntax check.
    """
    text = str(request).lower()
    code_words = ("function", "program", "code", "script", "game", "class", "calculator")
    return "python" in text and any(word in text for word in code_words)


def _extract_python_code(output):
    """
    PURPOSE: Find Python code that Qwen placed inside a fenced Markdown code block.
    CONNECTION: _validate_python_code() uses the returned snippets.
    RETURNS: A list of code strings. An empty list means no fenced code was found.
    """
    blocks = re.findall(r"```(?:python|py)?\s*\n?(.*?)```", str(output), flags=re.IGNORECASE | re.DOTALL)
    return [block.strip() for block in blocks if block.strip()]


def _validate_python_code(output):
    """
    PURPOSE: Parse generated Python code to catch obvious syntax failures before file creation.
    CONNECTION: validate_generated_text() -> this function.

    IMPORTANT:
        ast.parse() checks syntax only. It does not prove that the program's logic is correct.
    """
    code_blocks = _extract_python_code(output)
    if not code_blocks:
        return False, "The Python request should contain a fenced Python code block."

    for code in code_blocks:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            line = exc.lineno or "unknown"
            return False, f"The generated Python has a syntax error near line {line}."

        # Simple missing-import check for the standard-library module most common in small examples.
        imports_random = any(
            isinstance(node, ast.Import) and any(alias.name == "random" for alias in node.names)
            or isinstance(node, ast.ImportFrom) and node.module == "random"
            for node in ast.walk(tree)
        )
        uses_random = any(
            isinstance(node, ast.Name) and node.id == "random"
            for node in ast.walk(tree)
        )
        if uses_random and not imports_random:
            return False, "The Python code uses random but does not import the random module."

    return True, "Passed"


def validate_generated_text(request, output, document=False):
    """
    PURPOSE:
        Reject clearly empty, tiny, unrelated, or obviously invalid generated content.

    CONNECTION:
        document_api.py calls this after Qwen generation and again after one retry.

    RETURNS:
        (True, "Passed") or (False, readable reason)
    """
    if not isinstance(output, str) or not output.strip():
        return False, "The model returned an empty response."

    clean = output.strip()

    # For an explicit Python coding request, check the code itself before the generic length check.
    # This gives a student the useful cause (for example, SyntaxError) instead of only "too short".
    if _looks_like_python_program_request(request):
        valid, reason = _validate_python_code(clean)
        if not valid:
            return False, reason

    minimum = 100 if document else 20
    if len(clean) < minimum:
        return False, f"The generated output is too short ({len(clean)} characters)."

    if document:
        lines = [line.strip() for line in clean.splitlines() if line.strip()]
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", clean) if part.strip()]
        body_paragraphs = paragraphs[1:] if len(paragraphs) > 1 else []
        has_heading = any(line.startswith("#") for line in lines)
        has_bullet = any(line.startswith(("- ", "* ")) for line in lines)
        has_code = "```" in clean
        if len(body_paragraphs) < 2 and not has_heading and not has_bullet and not has_code:
            return False, "The document needs clearer structure such as headings, paragraphs, bullets, or code."

    if not _topic_matches(request, clean):
        return False, "The generated output does not appear related to the requested topic."

    return True, "Passed"
