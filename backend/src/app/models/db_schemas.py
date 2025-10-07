from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# -----------------------------
# Account Schemas
# -----------------------------
class AccountBase(BaseModel):
    account_id: str
    name: Optional[str]
    type: Optional[str]
    subtype: Optional[str]
    balance_current: Optional[float]
    currency: str = "USD"


class AccountCreate(AccountBase):
    plaid_user_id: int


class AccountRead(AccountBase):
    id: int
    plaid_user_id: int

    class Config:
        orm_mode = True


# -----------------------------
# PlaidUser Schemas
# -----------------------------
class PlaidUserBase(BaseModel):
    item_id: Optional[str]
    institution_name: Optional[str]


class PlaidUserCreate(PlaidUserBase):
    user_id: int
    access_token: Optional[str]  # store encrypted before insert


class PlaidUserRead(PlaidUserBase):
    id: int
    user_id: int
    accounts: List[AccountRead] = []

    class Config:
        orm_mode = True


# -----------------------------
# User Schemas
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]
    sub: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    plaid_users: List[PlaidUserRead] = []

    class Config:
        orm_mode = True


# -----------------------------
# HH Schemas
# -----------------------------
class HouseholdMemberBase(BaseModel):
    household_id: int
    user_id: int
    role: Optional[str]

class HouseholdMemberCreate(HouseholdMemberBase):
    pass

class HouseholdMemberRead(HouseholdMemberBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class HouseholdAccountBase(BaseModel):
    household_id: int
    account_id: int

class HouseholdAccountCreate(HouseholdAccountBase):
    pass

class HouseholdAccountRead(HouseholdAccountBase):
    id: int

    class Config:
        orm_mode = True

class HouseholdBase(BaseModel):
    name: Optional[str] = "test"

class HouseholdCreate(HouseholdBase):
    pass

class HouseholdRead(HouseholdBase):
    id: int = 0
    created_at: Optional[datetime] = datetime.now()
    household_members: List[HouseholdMemberRead] = []
    household_accounts: List[HouseholdAccountRead] = []

    class Config:
        orm_mode = True

