import logging
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
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
from app.models import PlaidAccount, PlaidTransaction
from app.security.encryption import encryption_service

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
            print(response)
            return response['link_token']
            
        except ApiException as e:
            logger.error(f"Error creating link token: {e}")
            raise Exception(f"Failed to create link token: {str(e)}")
    
    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """Exchange public token for access token and item ID."""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            print(response)
            return response
            
            
        except ApiException as e:
            logger.error(f"Error exchanging public token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    def get_accounts(self, access_token: str) -> List[PlaidAccount]:
        """Get accounts for a given access token."""
        try:
            # Decrypt the access token if it's encrypted
            decrypted_token = encryption_service.decrypt(access_token)
            
            request = AccountsGetRequest(access_token=decrypted_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                print(account)
                print("**************")
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
    
    def get_transactions(
        self, 
        access_token: str, 
        start_date: datetime = None, 
        end_date: datetime = None,
        account_ids: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0
    ) -> List[PlaidTransaction]:
        """Get transactions for a given access token."""
        try:
            # Decrypt the access token if it's encrypted
            decrypted_token = encryption_service.decrypt(access_token)
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            request = TransactionsGetRequest(
                access_token=decrypted_token,
                start_date=start_date.date(),
                end_date=end_date.date()
                #count=count,
                #offset=offset
            )
            
            if account_ids:
                request.account_ids = account_ids
            
            response = self.client.transactions_get(request)
            
            transactions = []
            for transaction in response['transactions']:
                plaid_transaction = PlaidTransaction(
                    transaction_id=transaction['transaction_id'],
                    account_id=transaction['account_id'],
                    amount=transaction['amount'],
                    date=transaction['date'],
                    name=transaction['name'],
                    merchant_name=transaction.get('merchant_name'),
                    category=[ transaction.personal_finance_category.primary ],
                    pending=transaction.get('pending', False)
                )
                transactions.append(plaid_transaction)

            return transactions
            
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