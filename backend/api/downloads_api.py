"""
STUDENT CODE MAP
============================================================
FILE: backend/api/downloads_api.py
PURPOSE: Send a generated PDF/DOCX file back to the logged-in browser.

CONNECTION:
    document_api.py -> /api/download/<filename> -> generated/ -> browser download

EDIT HERE:
    Change allowed file extensions only when the project learns another artifact type.
============================================================
"""

# Blueprint groups the download route; jsonify is used for a simple invalid-extension error.
from flask import Blueprint, jsonify, send_from_directory

# Only logged-in users may download generated files.
from backend.auth import login_required

# This is the one directory where generated artifacts are allowed to live.
from backend.config import GENERATED_DIR

downloads_api = Blueprint("downloads_api", __name__, url_prefix="/api")


@downloads_api.get("/download/<path:filename>")
@login_required
def download(user, filename):
    """
    PURPOSE: Send one generated PDF/DOCX file to the browser.
    CONNECTION: document_api.py returns this URL after creating the file.
    """
    if not filename.lower().endswith((".pdf", ".docx")):
        return jsonify({
            "success": False,
            "message": "Only PDF and DOCX files are available.",
        }), 400
    return send_from_directory(GENERATED_DIR, filename, as_attachment=True)
