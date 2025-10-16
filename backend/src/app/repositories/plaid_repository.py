import logging
from typing import Optional, List
import pyodbc
from app.db import get_connection
from app.database import get_db_session
from app.models.db_models import PlaidUser
from app.security.encryption import encryption_service

logger = logging.getLogger(__name__)

class PlaidRepository:
    """Service for managing Plaid user data in the database."""
    
    def create_plaid_user(
        self, 
        user_id: int, 
        access_token: str, 
        item_id: str, 
        institution_name: Optional[str] = None
    ) -> int:
        """Create a new Plaid user record with encrypted access token."""
        try:
            # Encrypt the access token before storing
            encrypted_token = encryption_service.encrypt(access_token)
            
            with get_db_session() as db:
                new_plaid_user = PlaidUser(
                    user_id=user_id,
                    access_token=encrypted_token,
                    item_id=item_id,
                    institution_name=institution_name
                )
                db.add(new_plaid_user)
                db.commit()
                db.refresh(new_plaid_user)
                
                return new_plaid_user.id
        except pyodbc.Error as e:
            logger.error(f"Database error creating Plaid user: {e}")
            raise Exception(f"Failed to create Plaid user: {str(e)}")
    
    def get_plaid_user_by_user_id(self, user_id: int) -> Optional[PlaidUser]:
        """Get Plaid user by user ID."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.user_id == user_id).first()
                return plaid_user
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user by user ID: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_plaid_user_by_item_id(self, item_id: str) -> Optional[PlaidUser]:
        """Get Plaid user by item ID."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                return plaid_user
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user by item ID: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_all_plaid_users_for_user(self, user_id: int) -> List[PlaidUser]:
        """Get all Plaid connections for a user."""
        try:
            with get_db_session() as db:
                print("Getting all Plaid users for user id: ", user_id)
                plaid_users = db.query(PlaidUser).filter(PlaidUser.user_id == user_id).all()
                return plaid_users
        except pyodbc.Error as e:
            logger.error(f"Database error getting all Plaid users for user: {e}")
            raise Exception(f"Failed to get Plaid users: {str(e)}")
    
    def update_institution_name(self, plaid_user_id: int, institution_name: str) -> bool:
        """Update institution name for a Plaid user."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.id == plaid_user_id).first()
                if plaid_user:
                    plaid_user.institution_name = institution_name
                    db.commit()
                    db.refresh(plaid_user)
                    return True
                return False
        except pyodbc.Error as e:
            logger.error(f"Database error updating institution name: {e}")
            raise Exception(f"Failed to update institution name: {str(e)}")
    
    def delete_plaid_user(self, plaid_user_id: int) -> bool:
        """Delete a Plaid user record."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.id == plaid_user_id).first()
                if plaid_user:
                    db.delete(plaid_user)
                    db.commit()
                    return True
                return False
        except pyodbc.Error as e:
            logger.error(f"Database error deleting Plaid user: {e}")
            raise Exception(f"Failed to delete Plaid user: {str(e)}")

# Global instance
plaid_repository = PlaidRepository()