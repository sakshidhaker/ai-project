"""
STUDENT CODE MAP
============================================================
FILE: backend/api/chat_api.py
PURPOSE: Receive one chat message and return one RAG-powered Qwen answer.

FLOW:
    browser -> /api/chat -> search_knowledge() -> get_context() -> Qwen -> JSON -> browser

CONNECTIONS:
    frontend/app.js -> this route
    rag.py -> knowledge retrieval
    ai.py -> prompt + local generation

EDIT HERE:
    Change the input limit or response fields here.
============================================================
"""

# Blueprint creates this group of API routes; jsonify creates the browser-friendly JSON response.
from flask import Blueprint, jsonify, request

# This generates the final AI answer after RAG context is prepared.
from backend.ai import generate_chat_response

# This decorator blocks users who are not signed in.
from backend.auth import login_required

# This setting keeps a chat message reasonably small for a laptop demo.
from backend.config import MAX_CHAT_MESSAGE_LENGTH

# AppError contains a readable stage/message/suggestion for expected backend failures.
from backend.exceptions import AppError

# RAG retrieves relevant knowledge and turns the chunks into prompt context.
from backend.rag import get_context, search_knowledge

chat_api = Blueprint("chat_api", __name__, url_prefix="/api")


@chat_api.post("/chat")
@login_required
def chat(user):
    """
    PURPOSE: Run the normal Chat pipeline for one logged-in user.
    CONNECTION: app.js -> /api/chat -> this function -> rag.py -> ai.py.
    INPUT: form field named "message".
    RETURNS: JSON containing the answer and retrieved source filenames.
    """
    message = str(request.form.get("message", "")).strip()
    if not message:
        return jsonify({"success": False, "message": "Please enter a message."}), 400
    if len(message) > MAX_CHAT_MESSAGE_LENGTH:
        return jsonify({"success": False, "message": "Message is too long."}), 400

    try:
        results = search_knowledge(message)
        context = get_context(results)
        reply = generate_chat_response(message, context)
        return jsonify({
            "success": True,
            "reply": reply,
            "rag_used": bool(results),
            "sources": [item["source"] for item in results],
        })
    except AppError as exc:
        return jsonify({
            "success": False,
            "stage": exc.stage,
            "message": exc.message,
            "suggestion": exc.suggestion,
        }), 500
