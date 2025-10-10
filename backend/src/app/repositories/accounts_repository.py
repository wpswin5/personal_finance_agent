import logging
from typing import List
from sqlalchemy.orm import Session, joinedload,  selectinload
from app.database import get_db_session
from app.models.db_models import User, PlaidUser, Account
from app.models.db_schemas import AccountUpdate
logger = logging.getLogger(__name__)

class AccountsRepository:

    def get_accounts(self):
        print("calling repo method")
        with get_db_session() as db:
            accounts = (
                db.query(Account)
                .all()
            )
        return accounts
    
    def update_account(self, account_id: int, update: AccountUpdate):
        with get_db_session() as db:
            account = db.query(Account).filter(Account.id == account_id).first()
            
            for field, value in update.model_dump(exclude_unset=True).items():
                setattr(account, field, value)

            db.commit()
            db.refresh(account)

        return account
    
    def get_connections_by_user_id(self, user_id: int):
        with get_db_session() as db:
            user = (
                db.query(User)
                .filter(User.id == user_id)
                .options(
                    selectinload(User.plaid_users).selectinload(PlaidUser.accounts)
                )
                .first()
            )
        
        return user
    
accounts_repository = AccountsRepository()