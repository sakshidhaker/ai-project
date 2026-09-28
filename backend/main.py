"""
STUDENT CODE MAP
============================================================
FILE: backend/main.py
PURPOSE: Connect Flask pages, API blueprints, SQLite startup, the admin account, and model setup.

STARTUP FLOW:
    run.py -> create_app()
        -> folders
        -> SQLite users table
        -> built-in admin account
        -> automatic Qwen download check
        -> Flask routes

CONNECTIONS:
    HTML pages -> Jinja templates in frontend/
    API routes -> backend/api/*.py
    Database -> backend/database.py
    AI startup -> backend/ai.py

EDIT HERE:
    Add or change simple page routes here. Keep business logic in its own module.
============================================================
"""

# logging gives students a readable startup message without a large monitoring framework.
import logging

# quote safely puts Admin messages into the redirect URL.
from urllib.parse import quote

# Flask creates the app, renders Jinja templates, redirects pages, and returns health JSON.
from flask import Flask, jsonify, redirect, render_template, request

# Admin rules stay out of the template itself.
from backend.admin import list_users, remove_user

# ai.py performs the automatic model file check.
from backend.ai import ensure_model_downloaded, model_path

# auth.py supplies the session/admin helpers used by page routing and startup.
from backend.auth import ensure_admin_account, get_logged_in_user, is_admin_user

# config.py holds all shared project settings and folders.
from backend.config import (
    APP_NAME,
    APP_VERSION,
    FRONTEND_DIR,
    HOST,
    MODEL_NAME,
    PORT,
    SECRET_KEY,
    ensure_directories,
)

# SQLite is initialized before pages or APIs are allowed to use it.
from backend.database import init_db

# Each blueprint owns one API responsibility.
from backend.api.auth_api import auth_api
from backend.api.chat_api import chat_api
from backend.api.document_api import document_api
from backend.api.downloads_api import downloads_api

# ModelError lets startup report download problems without breaking login/admin pages.
from backend.exceptions import ModelError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def create_app():
    """
    PURPOSE: Build and configure the Flask application.
    CONNECTION: run.py imports the app; all page/API routes hang from this function.
    STARTUP: folders -> DB -> admin -> model download check -> Flask routes.
    """
    ensure_directories()
    init_db()
    ensure_admin_account()

    # Automatic model setup happens during startup, but a network failure does not lock students out of the UI.
    try:
        path = ensure_model_downloaded()
        logger.info("Qwen model ready: %s", path)
    except ModelError as exc:
        logger.warning("Qwen startup check: %s", exc.message)

    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR),
        static_folder=str(FRONTEND_DIR),
        static_url_path="/static",
    )
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Register each API module so the frontend can call its small route contract.
    app.register_blueprint(auth_api)
    app.register_blueprint(chat_api)
    app.register_blueprint(document_api)
    app.register_blueprint(downloads_api)

    @app.get("/api/health")
    def health():
        """
        PURPOSE: Return a basic startup check without running the model.
        CONNECTION: Browser or curl -> GET /api/health -> this function.
        """
        return jsonify({
            "success": True,
            "app": APP_NAME,
            "version": APP_VERSION,
            "database": "SQLite users table",
            "model": MODEL_NAME,
            "model_ready": model_path().is_file(),
        })

    @app.get("/")
    def home():
        """
        PURPOSE: Choose login, app, or admin based on the current session.
        CONNECTION: Browser -> / -> this function -> redirect.
        """
        user = get_logged_in_user()
        if not user:
            return redirect("/login")
        return redirect("/admin" if is_admin_user(user) else "/app")

    @app.get("/login")
    def login_page():
        """
        PURPOSE: Render login.html using Jinja.
        CONNECTION: Browser -> /login -> frontend/login.html.
        """
        user = get_logged_in_user()
        if user:
            return redirect("/admin" if is_admin_user(user) else "/app")
        return render_template("login.html", error=request.args.get("error", ""))

    @app.get("/signup")
    def signup_page():
        """
        PURPOSE: Render signup.html using Jinja.
        CONNECTION: Browser -> /signup -> frontend/signup.html.
        """
        if get_logged_in_user():
            return redirect("/app")
        return render_template("signup.html", error=request.args.get("error", ""))

    @app.get("/app")
    def app_page():
        """
        PURPOSE: Render the main Chat/Create workspace.
        CONNECTION: Session -> this route -> frontend/app.html.
        """
        user = get_logged_in_user()
        if not user:
            return redirect("/login")
        if is_admin_user(user):
            return redirect("/admin")
        return render_template(
            "app.html",
            user=user,
            model_name=MODEL_NAME,
            model_ready=model_path().is_file(),
            is_admin=is_admin_user(user),
        )

    @app.route("/admin", methods=["GET", "POST"])
    def admin_page():
        """
        PURPOSE: Render the simple Admin table and process search/delete forms.
        CONNECTION: admin.html -> this route -> admin.py -> database.py.
        NOTE: Search and deletion stay in Python; JavaScript is not needed here.
        """
        user = get_logged_in_user()
        if not user:
            return redirect("/login")
        if not is_admin_user(user):
            return redirect("/app")

        if request.method == "POST":
            # Python performs the deletion; the browser only submits the selected user ID.
            _, message = remove_user(request.form.get("user_id", ""), user)
            # Re-read the table after POST so Jinja shows the current SQLite state.
            return redirect("/admin?message=" + quote(message))

        search = request.args.get("q", "")
        message = request.args.get("message", "")
        return render_template(
            "admin.html",
            user=user,
            users=list_users(search),
            search=search,
            message=message,
        )

    @app.errorhandler(404)
    def not_found(error):
        """
        PURPOSE: Give unknown API paths JSON and unknown browser paths a friendly redirect.
        CONNECTION: Flask calls this when no registered route matches.
        """
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "API route not found."}), 404
        return redirect("/")

    logger.info(
        "%s %s ready at http://%s:%s",
        APP_NAME,
        APP_VERSION,
        HOST,
        PORT,
    )
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
