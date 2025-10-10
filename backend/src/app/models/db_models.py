from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    sub = Column(String, unique=True, index=True)  # Auth0 sub
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ Proper class-bound relationship
    plaid_users = relationship(
        lambda: PlaidUser,
        back_populates="user",
        cascade="all, delete-orphan"
    )

    household_members = relationship(
        lambda: HouseholdMember,
        back_populates="user",
        cascade="all, delete-orphan"
    )


class PlaidUser(Base):
    __tablename__ = "plaid_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    access_token = Column(String, nullable=True)  # encrypted
    item_id = Column(String, nullable=True)       # encrypted
    institution_name = Column(String)                   # encrypted

    # ✅ back reference to User
    user = relationship(lambda: User, back_populates="plaid_users")

    # ✅ link to Accounts
    accounts = relationship(
        lambda: Account,
        back_populates="plaid_user",
        cascade="all, delete-orphan"
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    plaid_user_id = Column(Integer, ForeignKey("plaid_users.id"), nullable=False)
    account_id = Column(String, unique=True, index=True)  # Plaid account_id
    name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    subtype = Column(String, nullable=True)
    balance_current = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    nickname = Column(String, nullable=True)

    # ✅ back reference to PlaidUser
    plaid_user = relationship(lambda: PlaidUser, back_populates="accounts")

    household_account = relationship(lambda: HouseholdAccount, back_populates="account")

class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, nullable=True)

    household_members= relationship(
        lambda: HouseholdMember,
        back_populates="household",
        cascade="all, delete-orphan"
    )

    household_accounts = relationship(
        lambda: HouseholdAccount,
        back_populates="household",
        cascade="all, delete-orphan"
    )

class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)

    household = relationship(lambda: Household, back_populates="household_members")

    user = relationship(lambda: User, back_populates="household_members")

class HouseholdAccount(Base):
    __tablename__ = "household_accounts"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))

    household = relationship(lambda: Household, back_populates="household_accounts")

    account = relationship(lambda: Account, back_populates="household_account")