from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload,  selectinload
from app.database import get_db
from app.models.db_models import User, PlaidUser
from app.models.db_schemas import UserRead

router = APIRouter()

@router.get("/{user_id}/connections", response_model=UserRead)
def get_user_plaid_connections(user_id: int, db: Session = Depends(get_db)):
    print("Calling get connections")
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .options(
            selectinload(User.plaid_users).selectinload(PlaidUser.accounts)
        )
        .first()
    )
    print(user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
