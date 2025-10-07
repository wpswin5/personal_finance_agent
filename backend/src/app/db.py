import pyodbc
import os

from datetime import datetime

def get_connection():
    conn_str = os.getenv("AZURE_SQL_CONN")
    return pyodbc.connect(conn_str)


def upsert_user(user: dict):
    """
    Insert a new user if they do not exist, otherwise update their fields if changed.
    user dict is expected to contain at least: sub, email, name
    """
    with get_connection() as conn:
        print("Connected to DB")
        cursor = conn.cursor()

        # Upsert: check if user exists by sub
        cursor.execute("SELECT id, email, name FROM users WHERE sub = ?", user["sub"])
        row = cursor.fetchone()

        if row:
            print("Found user - updating")
            # User exists → check if fields have changed
            db_email, db_name = row.email, row.name

            if db_email != user["email"] or db_name != user.get("name"):
                cursor.execute(
                    """
                    UPDATE users
                    SET email = ?, name = ?, updated_at = GETUTCDATE()
                    WHERE sub = ?
                    """,
                    user["email"],
                    user.get("name"),
                    user["sub"],
                )
                conn.commit()
        else:
            print("New user - inserting")
            # New user → insert
            cursor.execute(
                """
                INSERT INTO users (sub, email, name)
                VALUES (?, ?, ?)
                """,
                user["sub"],
                user["email"],
                user.get("name"),
            )
            conn.commit()

def get_id(sub: str):
    """
    Get user id by auth0 sub
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE sub = ?", sub)
    row = cursor.fetchone()

    return row[0]

