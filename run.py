"""
STUDENT STARTUP MAP
============================================================
FILE: run.py
PURPOSE: Provide the one beginner-friendly command used to start the project.

FLOW:
    python run.py
        -> backend.main imports create_app()
        -> folders are created
        -> SQLite users table is created
        -> admin account is ensured
        -> Qwen model download is checked automatically
        -> Flask starts

CONNECTION:
    Students normally change backend/config.py, not this file.
============================================================
"""

# HOST and PORT tell Flask where to listen; keeping them here would duplicate config.py.
from backend.config import HOST, PORT

# Importing app runs the small create_app() startup sequence in backend/main.py.
from backend.main import app


if __name__ == "__main__":
    print(f"AI Creator Engine is running at http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
