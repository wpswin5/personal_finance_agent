import logging
from typing import Optional, List
import pyodbc
from app.db import get_connection
from app.models import PlaidUser
from app.security.encryption import encryption_service

logger = logging.getLogger(__name__)

class PlaidDBService:
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
            print(access_token)
            encrypted_token = encryption_service.encrypt(access_token)
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO plaid_users (user_id, access_token, item_id, institution_name, created_at)
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, GETDATE())
                """
                
                cursor.execute(query, user_id, encrypted_token, item_id, institution_name)
                result = cursor.fetchone()
                plaid_user_id = result[0]
                conn.commit()
                
                logger.info(f"Created Plaid user record with ID: {plaid_user_id}")
                return plaid_user_id
                
        except pyodbc.Error as e:
            logger.error(f"Database error creating Plaid user: {e}")
            raise Exception(f"Failed to create Plaid user: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating Plaid user: {e}")
            raise Exception(f"Failed to create Plaid user: {str(e)}")
    
    def get_plaid_user_by_user_id(self, user_id: int) -> Optional[PlaidUser]:
        """Get Plaid user by user ID."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, user_id, access_token, item_id, institution_name, created_at
                    FROM plaid_users
                    WHERE user_id = ?
                """
                
                cursor.execute(query, user_id)
                row = cursor.fetchone()
                
                if row:
                    return PlaidUser(
                        id=row[0],
                        user_id=row[1],
                        access_token=row[2],  # Keep encrypted for now
                        item_id=row[3],
                        institution_name=row[4],
                        created_at=row[5]
                    )
                
                return None
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_plaid_user_by_item_id(self, item_id: str) -> Optional[PlaidUser]:
        """Get Plaid user by item ID."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, user_id, access_token, item_id, institution_name, created_at
                    FROM plaid_users
                    WHERE item_id = ?
                """
                
                cursor.execute(query, item_id)
                row = cursor.fetchone()
                
                if row:
                    return PlaidUser(
                        id=row[0],
                        user_id=row[1],
                        access_token=row[2],  # Keep encrypted for now
                        item_id=row[3],
                        institution_name=row[4],
                        created_at=row[5]
                    )
                
                return None
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user by item ID: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_all_plaid_users_for_user(self, user_id: int) -> List[PlaidUser]:
        """Get all Plaid connections for a user."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, user_id, access_token, item_id, institution_name, created_at
                    FROM plaid_users
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """
                
                cursor.execute(query, user_id)
                rows = cursor.fetchall()
                
                plaid_users = []
                for row in rows:
                    plaid_user = PlaidUser(
                        id=row[0],
                        user_id=row[1],
                        access_token=row[2],  # Keep encrypted for now
                        item_id=row[3],
                        institution_name=row[4],
                        created_at=row[5]
                    )
                    plaid_users.append(plaid_user)
                
                return plaid_users
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid users: {e}")
            raise Exception(f"Failed to get Plaid users: {str(e)}")
    
    def update_institution_name(self, plaid_user_id: int, institution_name: str) -> bool:
        """Update institution name for a Plaid user."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    UPDATE plaid_users
                    SET institution_name = ?
                    WHERE id = ?
                """
                
                cursor.execute(query, institution_name, plaid_user_id)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            logger.error(f"Database error updating institution name: {e}")
            raise Exception(f"Failed to update institution name: {str(e)}")
    
    def delete_plaid_user(self, plaid_user_id: int) -> bool:
        """Delete a Plaid user record."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    DELETE FROM plaid_users
                    WHERE id = ?
                """
                
                cursor.execute(query, plaid_user_id)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            logger.error(f"Database error deleting Plaid user: {e}")
            raise Exception(f"Failed to delete Plaid user: {str(e)}")
    
    def get_user_id_by_sub(self, sub: str) -> Optional[int]:
        """Get user ID by Auth0 sub."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id FROM users WHERE sub = ?
                """
                
                cursor.execute(query, sub)
                row = cursor.fetchone()
                
                return row[0] if row else None
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting user by sub: {e}")
            raise Exception(f"Failed to get user: {str(e)}")

# Global instance
plaid_db_service = PlaidDBService()