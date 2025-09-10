from fastapi import APIRouter, Depends
from app.auth_utils import validate_token
from app.db import get_connection


router = APIRouter()

@router.get("/me")
async def get_me(user: dict=Depends(validate_token)):
    # Persist user if first login
    print("getting user info")
    sub = user["sub"]
    email = user.get("email")
    with get_connection() as conn:
        print("sql conn open")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM users WHERE sub = ?", sub)
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute(
                "INSERT INTO users (sub, email, name) VALUES (?, ?, ?)",
                sub,
                email,
                user.get("name")
            )
            conn.commit()
    return {"sub": sub, "email": email}