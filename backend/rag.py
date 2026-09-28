"""
STUDENT CODE MAP
============================================================
FILE: backend/rag.py
PURPOSE: Load knowledge, create embeddings, and search for the CURRENT request.

KEY RULE:
    Every search_knowledge() call creates a new query embedding and a new ranking.
    Retrieved context is temporary. Only the document-embedding index is cached.

CONNECTION:
    chat_api.py / document_api.py -> search_knowledge() -> get_context() -> ai.py

EDIT HERE:
    Add factual .txt files in knowledge/. Retrieval settings are in config.py.
============================================================
"""

# NumPy stores vectors and calculates similarity scores.
import numpy as np

# Project settings keep paths and retrieval values in one simple file.
from backend.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    KNOWLEDGE_DIR,
    MAX_CONTEXT_CHARS,
    RAG_MIN_SCORE,
    RAG_TOP_K,
)

# RAGError gives the browser a readable retrieval error.
from backend.exceptions import RAGError

_chunks = []
_embeddings = None
_embedding_model = None
_knowledge_file_signature = None

# Prompt/recipe files stay in the project for students but are not RAG facts.
_NON_RAG_FILES = {
    "43_python_generation_prompts.txt",
    "36_project_recipes.txt",
}

# Creator Python requests search these sources instead of unrelated project notes.
_PYTHON_SOURCES = {
    "05_python_fundamentals.txt",
    "06_python_functions.txt",
    "07_python_data_structures.txt",
    "08_python_files_json.txt",
    "09_python_errors_debugging.txt",
    "10_python_oop.txt",
    "11_python_modules_packages.txt",
    "12_python_standard_library.txt",
    "41_python_code_generation_patterns.txt",
    "42_python_games_and_small_programs.txt",
    "44_python_debugging_and_code_quality.txt",
}


def load_knowledge():
    """
    PURPOSE: Read current factual .txt files from knowledge/.
    CONNECTION: _build_index() calls this before embedding the documents.
    EDIT HERE: Add factual material as a new .txt file.
    """
    documents = []

    if not KNOWLEDGE_DIR.exists():
        return documents

    for path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        if path.name in _NON_RAG_FILES:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            documents.append({"source": path.name, "text": text})

    return documents


def _get_knowledge_signature():
    """
    PURPOSE: Detect added, removed, or changed knowledge files.
    CONNECTION: _build_index() checks this before searching.
    WHY: A changed .txt file is automatically reflected on the next request.
    """
    if not KNOWLEDGE_DIR.exists():
        return ()

    signature = []

    for path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        if path.name in _NON_RAG_FILES:
            continue

        stat = path.stat()
        signature.append((path.name, stat.st_mtime_ns, stat.st_size))

    return tuple(signature)


def split_documents(documents):
    """
    PURPOSE: Split long knowledge files into overlapping chunks.
    CONNECTION: load_knowledge() -> split_documents() -> _build_index().
    WHY: Smaller chunks give semantic search useful pieces instead of whole files.
    """
    chunks = []

    for document in documents:
        text = document["text"]
        start = 0

        while start < len(text):
            end = start + CHUNK_SIZE
            piece = text[start:end].strip()

            if piece:
                chunks.append({
                    "source": document["source"],
                    "text": piece,
                })

            if end >= len(text):
                break

            start = end - CHUNK_OVERLAP

    return chunks


def _get_embedding_model():
    """
    PURPOSE: Load the Sentence Transformer model once.
    CONNECTION: Used for document embeddings and each new query embedding.
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        # SentenceTransformer converts text into vectors for semantic similarity.
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RAGError(
            "sentence-transformers is not installed.",
            "rag",
            "Run: pip install -r requirements.txt",
        ) from exc

    try:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    except Exception as exc:
        raise RAGError(
            f"The embedding model could not be loaded: {exc}",
            "rag",
            "Check internet access and try again.",
        ) from exc

    return _embedding_model


def _build_index(force=False):
    """
    PURPOSE: Build or refresh the reusable document-embedding index.
    CONNECTION: search_knowledge() -> _build_index().

    IMPORTANT:
        This is only a cache of knowledge-file embeddings. It is NOT the previous
        request's context and contains no conversation memory.
    """
    global _chunks, _embeddings, _knowledge_file_signature

    current_signature = _get_knowledge_signature()

    if (
        not force
        and _embeddings is not None
        and current_signature == _knowledge_file_signature
    ):
        return

    _chunks = split_documents(load_knowledge())
    _knowledge_file_signature = current_signature

    if not _chunks:
        _embeddings = np.empty((0, 1), dtype=np.float32)
        return

    try:
        texts = []
        for item in _chunks:
            texts.append(item["text"])

        _embeddings = _get_embedding_model().encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
    except RAGError:
        raise
    except Exception as exc:
        raise RAGError(
            f"Could not create knowledge embeddings: {exc}",
            "rag",
            "Check the embedding model.",
        ) from exc


def _is_python_program_query(query):
    """
    PURPOSE: Detect a Python-focused programming request for Creator.
    CONNECTION: search_knowledge() uses this to narrow candidate sources.
    """
    text = str(query).lower()

    other_languages = (
        "c++", "cpp", "java", "javascript", "typescript",
        "rust", "golang",
    )

    if any(language in text for language in other_languages):
        return False

    code_words = (
        "function", "program", "code", "script",
        "game", "class", "calculator", "tool",
    )

    return any(word in text for word in code_words)


def _retrieval_query(query, purpose):
    """
    PURPOSE: Prepare the embedding text for THIS request.
    CONNECTION: search_knowledge() -> SentenceTransformer.
    WHY: The original user wording stays intact; a small hint improves Python matches.
    """
    text = str(query).strip()

    if purpose == "creator" and _is_python_program_query(text):
        return (
            text
            + " Python beginner code complete runnable function "
            + "standard library example"
        )

    if purpose == "chat" and "python" in text.lower():
        return text + " Python concept explanation example"

    return text


def search_knowledge(query, top_k=RAG_TOP_K, purpose="chat"):
    """
    PURPOSE: Search the knowledge base AGAIN for the current request.

    CONNECTION:
        chat_api.py/document_api.py -> this function -> get_context() -> ai.py.

    IMPORTANT:
        A new query embedding and new semantic ranking happen on every call.
        Previous retrieved chunks are never reused as request context.

    PURPOSE:
        chat    = normal factual knowledge.
        creator = Python programming requests prefer the Python source set.
    """
    if not isinstance(query, str) or not query.strip():
        return []

    # Refresh the document index only when knowledge files changed.
    _build_index()

    if not _chunks:
        return []

    # This is the important per-request operation: embed the NEW question now.
    search_text = _retrieval_query(query, purpose)

    try:
        vector = _get_embedding_model().encode(
            [search_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]
        scores = np.dot(_embeddings, vector)
    except Exception as exc:
        raise RAGError(
            f"Semantic search failed: {exc}",
            "rag",
            "Try the question again.",
        ) from exc

    candidate_indices = list(range(len(_chunks)))

    if purpose == "creator" and _is_python_program_query(query):
        python_candidates = []

        for index, item in enumerate(_chunks):
            if item["source"] in _PYTHON_SOURCES:
                python_candidates.append(index)

        if python_candidates:
            candidate_indices = python_candidates

    ranked = sorted(
        candidate_indices,
        key=lambda index: float(scores[index]),
        reverse=True,
    )

    results = []

    for index in ranked[: int(top_k)]:
        score = float(scores[index])

        if score >= RAG_MIN_SCORE:
            item = _chunks[index]
            results.append({
                "source": item["source"],
                "text": item["text"],
                "score": round(score, 4),
            })

    return results


def get_context(results, max_chars=MAX_CONTEXT_CHARS):
    """
    PURPOSE: Convert THIS request's results into temporary prompt context.
    CONNECTION: search_knowledge() -> get_context() -> ai.py.
    IMPORTANT: The returned string is not saved after the request finishes.
    """
    pieces = []
    total = 0

    for item in results:
        piece = f"[Source: {item['source']}]\n{item['text']}"

        if total + len(piece) > max_chars:
            remaining = max_chars - total

            if remaining > 100:
                pieces.append(piece[:remaining])

            break

        pieces.append(piece)
        total += len(piece)

    return "\n\n".join(pieces)


def reset_index():
    """
    PURPOSE: Clear the cached document embeddings.
    CONNECTION: Useful for tests or teaching experiments.
    NOTE: Normal requests auto-detect knowledge file changes.
    """
    global _chunks, _embeddings, _knowledge_file_signature
    _chunks = []
    _embeddings = None
    _knowledge_file_signature = None
