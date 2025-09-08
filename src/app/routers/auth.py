from fastapi import APIRouter, Depends
from app.auth_utils import validate_token

router = APIRouter()

@router.get("/me")
async def get_me(claims=Depends(validate_token)):
    return {
        "sub": claims["sub"],
        "email": claims.get("email"),
    }