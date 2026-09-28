"""
STUDENT CODE MAP
============================================================
FILE: backend/database.py
PURPOSE: Teach SQLite with one table and a few direct SQL statements.

TABLE:
    users(id, name, email, password, created_at)

CONNECTIONS:
    auth.py -> create_user(), get_user(), get_user_by_id(), set_password()
    admin.py -> get_all_users(), delete_user()
    main.py -> init_db()

EDIT HERE:
    Change the SQL statements when teaching database changes.

BE CAREFUL:
    The password column stores a secure hash, never a plaintext password.
============================================================
"""

# sqlite3 is Python's built-in SQLite interface; no separate database server is required.
import sqlite3


# These settings give the database its file location and parent folder.
from backend.config import DATA_DIR, DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def get_connection():
    """
    PURPOSE: Open the SQLite database and return rows that behave like dictionaries.
    CONNECTION: Every database operation calls this function before running SQL.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """
    PURPOSE: Create the one users table when the application starts.
    CONNECTION: main.py -> init_db().
    TEACHING CONCEPT: This is the CREATE TABLE step.
    """
    connection = get_connection()
    try:
        connection.execute(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def create_user(name, email, password_hash):
    """
    PURPOSE: INSERT one new user into SQLite.
    CONNECTION: auth_api.py -> signup() -> this function.
    INPUT: Already-validated name/email + already-hashed password.
    """
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_user(email):
    """
    PURPOSE: SELECT one user by email.
    CONNECTION: auth.py uses this for login and admin startup.
    TEACHING CONCEPT: This is a simple SELECT query with a parameter.
    """
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id, name, email, password, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    """
    PURPOSE: SELECT one user by numeric ID.
    CONNECTION: auth.py -> get_logged_in_user().
    """
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id, name, email, password, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def set_password(user_id, password_hash):
    """
    PURPOSE: UPDATE one user's stored password hash.
    CONNECTION: auth.py -> ensure_admin_account().
    TEACHING CONCEPT: This is the UPDATE step.
    """
    connection = get_connection()
    try:
        connection.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (password_hash, user_id),
        )
        connection.commit()
    finally:
        connection.close()


def get_all_users(search=""):
    """
    PURPOSE: SELECT users for the simple Admin page.
    CONNECTION: admin.py -> main.py -> admin.html.
    NOTE: The password column is intentionally not returned to the browser.
    """
    search = str(search or "").strip()
    connection = get_connection()
    try:
        if search:
            like = "%" + search + "%"
            rows = connection.execute(
                """SELECT id, name, email, created_at
                   FROM users
                   WHERE name LIKE ? OR email LIKE ?
                   ORDER BY id DESC""",
                (like, like),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT id, name, email, created_at FROM users ORDER BY id DESC"
            ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def delete_user(user_id):
    """
    PURPOSE: DELETE one user row.
    CONNECTION: admin.py -> remove_user() -> Admin POST form.
    """
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def table_names():
    """
    PURPOSE: Show which tables exist for the teaching test suite.
    CONNECTION: tests/test_database.py.
    """
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    finally:
        connection.close()
    return [row[0] for row in rows]
