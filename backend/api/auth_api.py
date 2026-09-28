"""
STUDENT CODE MAP
============================================================
FILE: backend/api/auth_api.py
PURPOSE: Connect the small HTML login/signup forms to Python authentication.

ROUTES:
    POST /api/auth/signup
    POST /api/auth/login
    POST /api/auth/logout

CONNECTION:
    browser form -> this file -> auth.py -> database.py

EDIT HERE:
    Change form validation flow or redirect destinations here.
============================================================
"""

# quote safely places a readable validation message inside a redirect URL.
from urllib.parse import quote

# IntegrityError tells us when SQLite rejects a duplicate email.
from sqlite3 import IntegrityError

# Blueprint groups related Flask API routes; request reads form data; redirect returns to a page.
from flask import Blueprint, redirect, request

# These auth helpers contain the actual password/session rules.
from backend.auth import (
    check_password,
    check_password_strength,
    hash_password,
    log_in_user,
    log_out_user,
    validate_email,
    validate_name,
)

# This identifies the one reserved administrator email.
from backend.config import ADMIN_EMAIL

# These functions write/read the users table.
from backend.database import create_user, get_user

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")


def _form_error(message, page):
    """
    PURPOSE: Send a normal HTML form back to its page with a readable error.
    CONNECTION: signup() and login() call this when validation fails.
    """
    return redirect(f"/{page}?error={quote(message)}")


@auth_api.post("/signup")
def signup():
    """
    PURPOSE: Validate, hash, store, and sign in a new student.
    CONNECTION: signup.html -> POST /api/auth/signup -> this function.
    CALLS: auth validation helpers -> database.create_user().
    """
    name = str(request.form.get("name", "")).strip()
    email = str(request.form.get("email", "")).strip().lower()
    password = request.form.get("password", "")

    valid, message = validate_name(name)
    if not valid:
        return _form_error(message, "signup")

    valid, message = validate_email(email)
    if not valid:
        return _form_error(message, "signup")

    if email == ADMIN_EMAIL:
        return _form_error("That email is reserved for the administrator.", "signup")

    valid, message = check_password_strength(password)
    if not valid:
        return _form_error(message, "signup")

    try:
        user_id = create_user(name, email, hash_password(password))
    except IntegrityError:
        return _form_error("An account with that email already exists.", "signup")

    log_in_user(user_id)
    return redirect("/app")


@auth_api.post("/login")
def login():
    """
    PURPOSE: Find the email, compare the password hash, and create a session.
    CONNECTION: login.html -> POST /api/auth/login -> this function.
    NEXT: Redirect to /admin for the built-in admin; otherwise /app.
    """
    email = str(request.form.get("email", "")).strip().lower()
    password = request.form.get("password", "")

    valid, _ = validate_email(email)
    if not valid or not password:
        return _form_error("Email or password is incorrect.", "login")

    user = get_user(email)
    if not user or not check_password(password, user["password"]):
        return _form_error("Email or password is incorrect.", "login")

    log_in_user(user["id"])
    return redirect("/admin" if email == ADMIN_EMAIL else "/app")


@auth_api.post("/logout")
def logout():
    """
    PURPOSE: Clear the Flask session.
    CONNECTION: logout form -> this route -> auth.log_out_user() -> /login.
    """
    log_out_user()
    return redirect("/login")
