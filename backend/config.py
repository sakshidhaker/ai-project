"""
STUDENT CODE MAP
============================================================
FILE: backend/config.py
PURPOSE: Keep the small set of shared settings used by the project.

CONNECTIONS:
    main.py -> paths/server settings
    ai.py -> Qwen settings
    rag.py -> embedding/retrieval settings
    auth.py -> account/admin settings

EDIT HERE:
    This is the main configuration file students should open first.
============================================================
"""

# os reads optional settings from environment variables without adding a configuration library.
import os

# Path gives platform-safe project folders on Linux, Windows, and macOS.
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
GENERATED_DIR = PROJECT_ROOT / "generated"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
DATABASE_PATH = DATA_DIR / "app.db"

APP_NAME = "AI Creator Engine"
APP_VERSION = "Teaching Edition"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5001"))
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-local-secret")

# ============================================================
# ADMIN LOGIN
# ============================================================
# The demo administrator is identified by email rather than an is_admin database column.
# The password is hashed before it enters SQLite; ADMIN_PASSWORD is never stored directly.
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@local.test").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# ============================================================
# ONE LOCAL QWEN MODEL
# ============================================================
# EDIT HERE: change both model values together when teaching another GGUF file.
MODEL_REPOSITORY = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
MODEL_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_NAME = "Qwen 2.5 Instruct 0.5B"
MODEL_CONTEXT_TOKENS = 4096
MAX_GENERATION_TOKENS = 768

# ============================================================
# RAG
# ============================================================
# Sentence Transformers converts knowledge text into vectors for semantic retrieval.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_TOP_K = 3
RAG_MIN_SCORE = 0.20
MAX_CONTEXT_CHARS = 5200
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

# ============================================================
# SIMPLE LIMITS
# ============================================================
MAX_NAME_LENGTH = 80
MAX_EMAIL_LENGTH = 160
MAX_CHAT_MESSAGE_LENGTH = 2000
MAX_PROMPT_LENGTH = 5000
MIN_PASSWORD_LENGTH = 8
ALLOWED_ARTIFACT_TYPES = {"pdf", "docx"}


def ensure_directories():
    """
    PURPOSE: Create the folders used by SQLite, models, generated files, and knowledge.
    CONNECTION: main.py calls this before any other startup work.
    """
    for folder in (DATA_DIR, MODELS_DIR, GENERATED_DIR, KNOWLEDGE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
