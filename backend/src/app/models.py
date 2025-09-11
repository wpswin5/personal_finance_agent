from pydantic import BaseModel, validator
from datetime import date

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
