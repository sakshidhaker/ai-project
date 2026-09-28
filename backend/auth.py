"""
STUDENT CODE MAP
============================================================
FILE: backend/auth.py
PURPOSE: Validate accounts, hash/check passwords, manage Flask sessions, and protect routes.

CONNECTIONS:
    api/auth_api.py -> signup/login/logout
    main.py -> get_logged_in_user()/is_admin_user()/ensure_admin_account()
    protected APIs -> login_required

EDIT HERE:
    Change password rules in check_password_strength().
============================================================
"""

# wraps keeps the original Flask view metadata when login_required adds a wrapper.
from functools import wraps

# Any makes the optional user dictionary annotation easy to understand for students.
from typing import Any

# Flask stores the signed session; jsonify is used for API authorization errors.
from flask import jsonify, session

# Werkzeug provides the password hashing functions used by this small app.
from werkzeug.security import check_password_hash, generate_password_hash

# These settings define the simple account limits and built-in demo admin login.
from backend.config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
)

# These are the only database operations needed by authentication.
from backend.database import create_user, get_user, get_user_by_id, set_password


def hash_password(password):
    """
    PURPOSE: Turn the real password into a one-way hash before it reaches SQLite.
    CONNECTION: api/auth_api.py -> signup() -> this function -> database.create_user().
    WHY: Plaintext passwords must never be stored.
    """
    return generate_password_hash(password)


def check_password(password, password_hash):
    """
    PURPOSE: Compare a typed password with the secure value stored in users.password.
    CONNECTION: api/auth_api.py -> login() -> this function.
    RETURNS: True when the password matches; otherwise False.
    """
    return check_password_hash(password_hash, password)


def check_password_strength(password):
    """
    PURPOSE: Check length, uppercase, lowercase, number, and special character.
    CONNECTION: api/auth_api.py -> signup() -> this function.
    EDIT HERE: Change the rules below when teaching password validation.
    """
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."

    has_upper = False
    has_lower = False
    has_number = False
    has_special = False

    for character in password:
        if character.isupper():
            has_upper = True
        elif character.islower():
            has_lower = True
        elif character.isdigit():
            has_number = True
        else:
            has_special = True

    if not has_upper:
        return False, "Password needs an uppercase letter."
    if not has_lower:
        return False, "Password needs a lowercase letter."
    if not has_number:
        return False, "Password needs a number."
    if not has_special:
        return False, "Password needs a special character."
    return True, ""


def validate_name(name):
    """
    PURPOSE: Validate the visible display name from signup.html.
    CONNECTION: auth_api.py -> signup().
    """
    name = str(name or "").strip()
    if not name:
        return False, "Name is required."
    if len(name) > MAX_NAME_LENGTH:
        return False, f"Name must be {MAX_NAME_LENGTH} characters or fewer."
    return True, ""


def validate_email(email):
    """
    PURPOSE: Perform a small beginner-readable email check.
    CONNECTION: auth_api.py -> signup() and login().
    NOTE: This intentionally avoids a complicated email-validation regex.
    """
    email = str(email or "").strip().lower()
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False, "Please enter a valid email address."
    if email.count("@") != 1:
        return False, "Please enter a valid email address."
    if email.startswith("@") or email.endswith("@"):
        return False, "Please enter a valid email address."
    if "." not in email.split("@", 1)[1]:
        return False, "Please enter a valid email address."
    return True, ""


def log_in_user(user_id):
    """
    PURPOSE: Store only the current user's ID in the signed Flask session.
    CONNECTION: auth_api.py -> login()/signup() -> this function.
    """
    session.clear()
    session["user_id"] = int(user_id)


def log_out_user():
    """
    PURPOSE: Remove all session values when the user logs out.
    CONNECTION: auth_api.py -> logout().
    """
    session.clear()


def get_logged_in_user():
    """
    PURPOSE: Read the current user from the session and SQLite.
    CONNECTION: main.py and login_required() call this before protected pages/routes.
    RETURNS: User dictionary or None.
    """
    user_id = session.get("user_id")
    if user_id is None:
        return None

    try:
        user = get_user_by_id(int(user_id))
    except (TypeError, ValueError):
        user = None

    if user is None:
        log_out_user()
    return user


def is_admin_user(user: dict[str, Any] | None):
    """
    PURPOSE: Identify the single configured admin without adding an is_admin database column.
    CONNECTION: main.py decides whether /app or /admin should open.
    """
    return bool(user and user.get("email", "").lower() == ADMIN_EMAIL)


def ensure_admin_account():
    """
    PURPOSE: Make sure the built-in local demo admin can always sign in.
    CONNECTION: main.py calls this once during application startup.
    WHY: A copied/old SQLite file should not leave the demo admin inaccessible.

    DEMO LOGIN:
        email = admin@local.test
        password = admin
    """
    existing = get_user(ADMIN_EMAIL)
    admin_hash = hash_password(ADMIN_PASSWORD)

    if existing:
        set_password(existing["id"], admin_hash)
        return

    create_user("AI Creator Admin", ADMIN_EMAIL, admin_hash)


def login_required(view):
    """
    PURPOSE: Protect an API route from users who are not signed in.
    CONNECTION: @login_required appears above chat, generate, and download routes.
    TEACHING CONCEPT: This is a small decorator. It runs before the real route function.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_logged_in_user()
        if not user:
            return jsonify({
                "success": False,
                "stage": "authorization",
                "message": "Login is required.",
                "suggestion": "Log in and try again.",
            }), 401
        return view(user, *args, **kwargs)

    return wrapped
