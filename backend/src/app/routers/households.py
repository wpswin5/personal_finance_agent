from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload,  selectinload
from app.database import get_db
from app.models.db_models import Household, HouseholdAccount, HouseholdMember
from app.models.db_schemas import HouseholdRead

router = APIRouter()

@router.get("/", response_model=List[HouseholdRead])
def get_user_plaid_connections(db: Session = Depends(get_db)):
    print("calling get HH")
    households = (
        db.query(Household)
        .options(
            selectinload(Household.household_members).selectinload(HouseholdMember.user),
            selectinload(Household.household_accounts).selectinload(HouseholdAccount.account)
        )
        .all()
    )
    if not households:
        raise HTTPException(status_code=404, detail="User not found")
    
    return households

@router.get("/{household_id}", response_model=HouseholdRead)
def get_user_plaid_connections(household_id: int, db: Session = Depends(get_db)):
    print("calling get HH")
    households = (
        db.query(Household)
        .filter(Household.id == household_id)
        .options(
            selectinload(Household.household_members).selectinload(HouseholdMember.user),
            selectinload(Household.household_accounts).selectinload(HouseholdAccount.account)
        )
        .first()
    )
    print(households)
    if not households:
        raise HTTPException(status_code=404, detail="User not found")
    
    return households
