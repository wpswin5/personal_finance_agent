import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import SecurityScopes
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from app.models import (
    PlaidAccount,
    PlaidLinkTokenRequest, 
    PlaidLinkTokenResponse,
    PlaidPublicTokenExchangeRequest,
    PlaidPublicTokenExchangeResponse,
    PlaidAccountsResponse,
    PlaidTransactionsResponse,
    PlaidUser,
    SyncItemRequest
)
from app.db import get_connection
from app.services.plaid_service import plaid_service
from app.services.plaid_db_service import plaid_db_service
from app.security.utils import get_verified_token
from app.security.access_token import AccessToken

logger = logging.getLogger(__name__)
router = APIRouter()
load_dotenv()

@router.post("/create_link_token", response_model=PlaidLinkTokenResponse)
async def create_link_token(
    request: PlaidLinkTokenRequest,
    token: AccessToken = Depends(get_verified_token)
):
    """Create a link token for Plaid Link initialization."""
    try:
        print("Calling create_link_token")
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        print("Found user")
        
        # Create link token
        print("Calling plaid service")
        link_token = plaid_service.create_link_token(
            user_id=str(user_id),
            user_email=token.email if hasattr(token, 'email') else None
        )
        
        return PlaidLinkTokenResponse(link_token=link_token)
        
    except Exception as e:
        logger.error(f"Error creating link token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link token: {str(e)}"
        )

@router.post("/exchange_public_token", response_model=PlaidPublicTokenExchangeResponse)
async def exchange_public_token(
    request: PlaidPublicTokenExchangeRequest,
    token: AccessToken = Depends(get_verified_token)
):
    """Exchange public token for access token and store in database."""
    try:
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Exchange public token for access token
        print("exchanging result")
        exchange_result = plaid_service.exchange_public_token(request.public_token)
        access_token = exchange_result['access_token']
        item_id = exchange_result['item_id']
        print("Received response back")
        
        # Get institution name
        institution_name = plaid_service.get_institution_name(access_token)
        print("Got institution name", institution_name)
        
        # Store encrypted access token in database
        plaid_user_id = plaid_db_service.create_plaid_user(
            user_id=user_id,
            access_token=access_token,
            item_id=item_id,
            institution_name=institution_name
        )
        
        return PlaidPublicTokenExchangeResponse(
            access_token_id=str(plaid_user_id),
            item_id=item_id,
            institution_name=institution_name
        )
        
    except Exception as e:
        logger.error(f"Error exchanging public token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange public token: {str(e)}"
        )

@router.get("/accounts", response_model=PlaidAccountsResponse)
async def get_accounts(
    plaid_user_ids: Optional[List[int]] = None,
    token: AccessToken = Depends(get_verified_token)
):
    """Get accounts for the authenticated user."""
    try:
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get Plaid user record
        if plaid_user_ids:
            plaid_users = plaid_db_service.get_all_plaid_users_for_user(user_id)
            if not plaid_users or len(plaid_users) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plaid connection not found"
                )
        else:
            plaid_users = plaid_db_service.get_all_plaid_users_for_user(user_id)
            print("Users: ", plaid_users)
            if not plaid_users:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Plaid connection found for user"
                )
        
        # Get accounts from Plaid
        accounts = []
        for user in plaid_users:
            print("Individual user: ", user)
            response = plaid_service.get_accounts(user.access_token)
            print("Response:  ", response)
            for account in response:
                account.connection_id = user.id
                accounts.append(account)
        #accounts = plaid_service.get_accounts(plaid_user.access_token)
        
        return PlaidAccountsResponse(accounts=accounts)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get accounts: {str(e)}"
        )

@router.get("/transactions", response_model=PlaidTransactionsResponse)
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    account_ids: Optional[str] = None,
    count: int = 100,
    offset: int = 0,
    plaid_user_id: Optional[int] = None,
    token: AccessToken = Depends(get_verified_token)
):
    """Get transactions for the authenticated user."""
    try:
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get Plaid user record
        if plaid_user_id:
            plaid_user = plaid_db_service.get_plaid_user_by_user_id(user_id)
            if not plaid_user or plaid_user.id != plaid_user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plaid connection not found"
                )
        else:
            plaid_user = plaid_db_service.get_plaid_user_by_user_id(user_id)
            if not plaid_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Plaid connection found for user"
                )
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Parse account IDs
        account_id_list = None
        if account_ids:
            account_id_list = account_ids.split(',')
        
        # Get transactions from Plaid
        transactions = plaid_service.get_transactions(
            access_token=plaid_user.access_token,
            start_date=start_dt,
            end_date=end_dt,
            account_ids=account_id_list,
            count=count,
            offset=offset
        )
        
        return PlaidTransactionsResponse(
            transactions=transactions,
            total_transactions=len(transactions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transactions: {str(e)}"
        )

@router.get("/connections", response_model=List[PlaidUser])
async def get_plaid_connections(
    token: AccessToken = Depends(get_verified_token)
):
    """Get all Plaid connections for the authenticated user."""
    try:
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all Plaid connections for the user
        plaid_users = plaid_db_service.get_all_plaid_users_for_user(user_id)
        
        # Don't return the actual access tokens in the response
        for plaid_user in plaid_users:
            plaid_user.access_token = "***encrypted***"
        
        return plaid_users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Plaid connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Plaid connections: {str(e)}"
        )

@router.delete("/connections/{plaid_user_id}")
async def delete_plaid_connection(
    plaid_user_id: int,
    token: AccessToken = Depends(get_verified_token)
):
    """Delete a Plaid connection for the authenticated user."""
    try:
        # Get user ID from database using Auth0 sub
        user_id = plaid_db_service.get_user_id_by_sub(token.sub)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify the Plaid connection belongs to the user
        plaid_user = plaid_db_service.get_plaid_user_by_user_id(user_id)
        if not plaid_user or plaid_user.id != plaid_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plaid connection not found"
            )
        
        # Delete the Plaid connection
        success = plaid_db_service.delete_plaid_user(plaid_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete Plaid connection"
            )
        
        return {"message": "Plaid connection deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Plaid connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Plaid connection: {str(e)}"
        )

@router.post("/sync_item")
async def sync_item(request: SyncItemRequest, db=Depends(get_connection)):
    """
    Sync accounts + transactions for a given Plaid item.
    - Fetch access_token from DB
    - Call PlaidService (accounts + transactions)
    - Upsert results into Azure SQL (deduplicated with MERGE)
    """
    item_id = request.item_id
    cursor = db.cursor()

    # 1. Lookup access_token
    cursor.execute("SELECT access_token FROM plaid_users WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    access_token = row[0]

    # 2. Fetch Accounts (via PlaidService wrapper)
    accounts = plaid_service.get_accounts(access_token)
    for acct in accounts:
        cursor.execute("""
            MERGE accounts AS target
            USING (SELECT ? AS account_id) AS source
            ON target.account_id = source.account_id
            WHEN MATCHED THEN
                UPDATE SET name=?, type=?, subtype=?, balance_current=?, currency=?
            WHEN NOT MATCHED THEN
                INSERT (account_id, plaid_user_id, name, type, subtype, balance_current, currency)
                VALUES (?, (SELECT id FROM plaid_users WHERE item_id=?), ?, ?, ?, ?, ?);
        """, (
            acct.account_id,
            acct.name,
            acct.type,
            acct.subtype,
            acct.balance,
            acct.currency,
            acct.account_id,
            item_id,
            acct.name,
            acct.type,
            acct.subtype,
            acct.balance,
            acct.currency,
        ))

    # 3. Fetch Transactions (last 30 days default)
    transactions = plaid_service.get_transactions(access_token)
    for tx in transactions:
        print(tx)
        cursor.execute("""
            MERGE transactions AS target
            USING (SELECT ? AS transaction_id) AS source
            ON target.transaction_id = source.transaction_id
            WHEN MATCHED THEN
                UPDATE SET amount=?, created_at=?, merchant_name=?, description=?, is_pending=?, category=?
            WHEN NOT MATCHED THEN
                INSERT (transaction_id, account_id, amount, date_posted, merchant_name, description, is_pending, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            tx.transaction_id,
            tx.amount,
            tx.date,
            tx.merchant_name,
            tx.name,
            tx.pending,
            ",".join(tx.category) if tx.category else None,
            tx.transaction_id,
            tx.account_id,
            tx.amount,
            tx.date,
            tx.merchant_name,
            tx.name,
            tx.pending,
            ",".join(tx.category) if tx.category else None,
        ))

    db.commit()
    return {"status": "ok", "item_id": item_id, "accounts_synced": len(accounts), "transactions_synced": len(transactions)}