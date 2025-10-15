import logging
from typing import List
from sqlalchemy.orm import Session, joinedload,  selectinload
from app.database import get_db_session
from app.models.db_models import User, PlaidUser, Account
from app.models.db_schemas import AccountUpdate
logger = logging.getLogger(__name__)

class UserRepository:

    def upsert_user(self, user: dict):
        with get_db_session() as db:
            db_user = db.query(User).filter(User.sub == user["sub"]).first()
            
            if db_user:
                logger.info("Found user - updating")
                # User exists → check if fields have changed
                if db_user.email != user["email"] or db_user.name != user.get("name"):
                    db_user.email = user["email"]
                    db_user.name = user.get("name")
                    db.commit()
                    db.refresh(db_user)
            else:
                logger.info("New user - inserting")
                # New user → insert
                new_user = User(
                    sub=user["sub"],
                    email=user["email"],
                    name=user.get("name")
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)

    def get_id(self, sub: str):
        with get_db_session() as db:
            db_user = db.query(User).filter(User.sub == sub).first()
            if db_user:
                return db_user.id
        
    def get_user_with_accounts(self, sub: str):
        with get_db_session() as db:
            db_user = db.query(User).options(
                selectinload(User.plaid_users).selectinload(PlaidUser.accounts)
            ).filter(User.sub == sub).first()
            return db_user

user_repository = UserRepository()