import logging
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.exceptions import ApiException

from app.config import get_settings
from app.models.plaid_models import PlaidAccount, PlaidTransaction
# Tokens are decrypted at the DB boundary by the repository; this service expects plaintext tokens

logger = logging.getLogger(__name__)

class PlaidService:
    """Service for interacting with Plaid API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = self._create_client()
    
    def _create_client(self) -> plaid_api.PlaidApi:
        """Create and configure Plaid API client."""
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': self.settings.PLAID_CLIENT_ID,
                'secret': self.settings.PLAID_SECRET,
            }
        )
        api_client = ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)
    
    def _get_plaid_host(self):
        """Get the appropriate Plaid host based on environment."""
        env_mapping = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }
        return env_mapping.get(self.settings.PLAID_ENV, 'https://sandbox.plaid.com')
    
    def create_link_token(self, user_id: str, user_email: Optional[str] = None) -> str:
        """Create a link token for Plaid Link initialization."""
        print("Calling plaid API")
        try:
            request = LinkTokenCreateRequest(
                #client_id=os.getenv("PLAID_CLIENT_ID"),
                #client_secret=os.getenv("PLAID_SECRET"),
                products=[Products('transactions')],
                client_name="Personal Finance Agent",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )

            
            response = self.client.link_token_create(request)
            print("Got response")
            return response['link_token']
            
        except ApiException as e:
            logger.error(f"Error creating link token: {e}")
            raise Exception(f"Failed to create link token: {str(e)}")
    
    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """Exchange public token for access token and item ID."""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return response
            
            
        except ApiException as e:
            logger.error(f"Error exchanging public token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    def get_accounts(self, access_token: str) -> List[PlaidAccount]:
        """Get accounts for a given access token."""
        try:
            # PlaidRepository now decrypts tokens at the DB boundary. This service expects a plaintext token.
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                plaid_account = PlaidAccount(
                    account_id=account['account_id'],
                    name=account['name'],
                    type=str(account['type']),
                    subtype=str(account.get('subtype')),
                    balance=account['balances']['current'] or 0.0,
                    currency=account['balances']['iso_currency_code'] or 'USD'
                )
                accounts.append(plaid_account)
            
            return accounts
            
        except ApiException as e:
            logger.error(f"Error getting accounts: {e}")
            raise Exception(f"Failed to get accounts: {str(e)}")
    
    def sync_transactions(
        self, 
        access_token: str, 
        start_date: datetime = None, 
        end_date: datetime = None,
        account_ids: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Plaid incremental transactions/sync cursor loop and return {'transactions': [...], 'cursor': final_cursor}.

        This method always performs the incremental sync (cursor loop) and returns a dict
        with the added transactions and the final cursor. It no longer supports the
        legacy single-call list return format.
        """
        try:
            # PlaidRepository now decrypts tokens at the DB boundary. This service expects a plaintext token.
            decrypted_token = access_token
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Always run the incremental sync loop and collect all 'added' transactions
            all_added = []
            next_cursor = cursor
            while True:
                req = TransactionsSyncRequest(access_token=decrypted_token)
                if next_cursor:
                    req.cursor = next_cursor
                if account_ids:
                    req.account_ids = account_ids
                if count:
                    req.count = count

                response = self.client.transactions_sync(req).to_dict()

                added = response.get('added', [])
                all_added.extend(added)

                has_more = response.get('has_more', False)
                next_cursor = response.get('next_cursor') or response.get('cursor')

                if not has_more:
                    break

            # map to PlaidTransaction objects
            transactions = []
            for transaction in all_added:
                # category: prefer personal_finance_category.primary, else category list
                category_val = None
                if transaction.get('personal_finance_category'):
                    pfc = transaction.get('personal_finance_category')
                    category_val = [pfc.get('primary')] if pfc else None
                elif transaction.get('category'):
                    category_val = transaction.get('category')

                plaid_transaction = PlaidTransaction(
                    transaction_id=transaction.get('transaction_id'),
                    account_id=transaction.get('account_id'),
                    amount=transaction.get('amount'),
                    date=transaction.get('date'),
                    name=transaction.get('name'),
                    merchant_name=transaction.get('merchant_name'),
                    category=category_val or [],
                    pending=transaction.get('pending', False)
                )
                transactions.append(plaid_transaction)

            return {"transactions": transactions, "cursor": next_cursor}
            
        except ApiException as e:
            logger.error(f"Error getting transactions: {e}")
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    def get_institution_name(self, access_token: str) -> Optional[str]:
        """Get institution name for a given access token."""
        try:
            # Decrypt the access token if it's encrypted
            #decrypted_token = encryption_service.decrypt(access_token)
            
            # Get item info first
            from plaid.model.item_get_request import ItemGetRequest
            request = ItemGetRequest(access_token=access_token)
            response = self.client.item_get(request)
            
            institution_id = response['item']['institution_id']
            
            # Get institution details
            from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
            inst_request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=[CountryCode('US')]
            )
            inst_response = self.client.institutions_get_by_id(inst_request)
            
            return inst_response['institution']['name']
            
        except ApiException as e:
            logger.error(f"Error getting institution name: {e}")
            return None

# Global instance
plaid_service = PlaidService()