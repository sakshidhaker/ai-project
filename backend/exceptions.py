"""
STUDENT CODE MAP
============================================================
FILE: backend/exceptions.py
PURPOSE: Define small custom errors that carry a stage and a student-friendly suggestion.

CONNECTIONS:
    ai.py/rag.py -> raise ModelError/RAGError
    API routes -> catch AppError and send readable JSON to the browser
============================================================
"""

class AppError(Exception):
    """
    PURPOSE: Base error for failures that the browser can explain cleanly.
    CONNECTION: ModelError and RAGError inherit from this class.
    """

    def __init__(self, message, stage="application", suggestion="Try again."):
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.suggestion = suggestion


class ModelError(AppError):
    """
    PURPOSE: Identify failures while downloading, loading, or running Qwen.
    CONNECTION: ai.py raises this; API routes return its details.
    """


class RAGError(AppError):
    """
    PURPOSE: Identify failures while loading, embedding, or searching knowledge.
    CONNECTION: rag.py raises this; API routes return its details.
    """
