"""
STUDENT CODE MAP
============================================================
FILE: backend/admin.py
PURPOSE: Keep the small Admin rules outside the HTML page.

CONNECTIONS:
    main.py -> list_users()/remove_user()
    database.py -> SELECT/DELETE operations
    auth.py -> checks whether the current user is the configured administrator

EDIT HERE:
    Change admin-only rules here instead of putting business logic inside HTML.
============================================================
"""

# This helper verifies that the current session belongs to the configured admin.
from backend.auth import is_admin_user

# These functions perform the actual SQLite queries.
from backend.database import delete_user, get_all_users


def list_users(search=""):
    """
    PURPOSE: Return the rows shown on the Admin page.
    CONNECTION: main.py -> admin.html.
    """
    return get_all_users(search)


def remove_user(user_id, current_user):
    """
    PURPOSE: Delete one user while protecting the administrator account.
    CONNECTION: main.py -> Admin POST -> this function -> database.delete_user().
    RETURNS: (success_boolean, human_readable_message).
    """
    if not is_admin_user(current_user):
        return False, "Admin access is required."

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False, "The selected user ID is invalid."

    if user_id == int(current_user["id"]):
        return False, "The administrator account cannot delete itself."

    if not delete_user(user_id):
        return False, "User was not found."
    return True, "User deleted."
