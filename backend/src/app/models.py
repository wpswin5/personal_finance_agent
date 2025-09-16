from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List

class TransactionIn(BaseModel):
    user_id: str
    posted_at: date
    amount: float
    currency: str
    merchant_name: str
    description: str

    @validator("amount")
    def check_amount(cls, v):
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v

# Plaid Models
class PlaidLinkTokenRequest(BaseModel):
    user_id: str

class PlaidLinkTokenResponse(BaseModel):
    link_token: str

class PlaidPublicTokenExchangeRequest(BaseModel):
    public_token: str
    user_id: str

class PlaidPublicTokenExchangeResponse(BaseModel):
    access_token_id: str  # We return an ID, not the actual token
    item_id: str
    institution_name: Optional[str] = None

class PlaidUser(BaseModel):
    id: Optional[int] = None
    user_id: int
    access_token: str  # This will be encrypted in the database
    item_id: str
    institution_name: Optional[str] = None
    created_at: Optional[datetime] = None

class PlaidAccount(BaseModel):
    account_id: str
    name: str
    type: str
    subtype: Optional[str] = None
    balance: float
    currency: str

class PlaidTransaction(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    date: date
    name: str
    merchant_name: Optional[str] = None
    category: List[str] = []
    pending: bool = False

class PlaidAccountsResponse(BaseModel):
    accounts: List[PlaidAccount]

class PlaidTransactionsResponse(BaseModel):
    transactions: List[PlaidTransaction]
    total_transactions: int
