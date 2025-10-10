from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload,  selectinload
from app.database import get_db
from app.models.db_models import User, PlaidUser, Account
from app.models.db_schemas import UserRead, AccountRead, AccountUpdate
from app.repositories.accounts_repository import accounts_repository

router = APIRouter()

@router.get("/", response_model=List[AccountRead])
def get_accounts():
    accounts = accounts_repository.get_accounts()
    if not accounts:
        raise HTTPException(status_code=404, detail="Accounts not found")
    
    return accounts

@router.patch("/{account_id}", response_model=AccountRead)
def update_account_nickname(account_id: int, update: AccountUpdate):
    account = accounts_repository.update_account(account_id, update)
    return account


@router.get("/{user_id}/connections", response_model=UserRead)
def get_user_plaid_connections(user_id: int):
    user = accounts_repository.get_connections_by_user_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
