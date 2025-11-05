from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from auth0 import authentication

from app.database import get_db
from app.models.db_models import Household, HouseholdAccount, HouseholdMember
from app.models.db_schemas import (
    HouseholdRead,
    HouseholdCreate,
    HouseholdMemberCreate,
    HouseholdMemberRead,
)
from app.security.utils import verify_token
from app.dependencies import get_auth0_users_client
from app.repositories.user_repository import user_repository

from pydantic import BaseModel

router = APIRouter()


def _get_current_user_id(access_token: str, auth0_users: authentication.Users) -> int:
    """Helper to resolve Auth0 userinfo -> local user id.

    Raises HTTPException(404) if local user not found.
    """
    userinfo = auth0_users.userinfo(access_token=access_token)
    user_id = user_repository.get_id(userinfo.get("sub"))
    if user_id is None:
        raise HTTPException(status_code=404, detail="User id not found")
    return user_id


@router.get("/", response_model=List[HouseholdRead])
def get_households(db: Session = Depends(get_db)):
    households = (
        db.query(Household)
        .options(
            selectinload(Household.household_members).selectinload(HouseholdMember.user),
            selectinload(Household.household_accounts).selectinload(HouseholdAccount.account),
        )
        .all()
    )
    if not households:
        raise HTTPException(status_code=404, detail="No households found")

    return households


@router.get("/{household_id}", response_model=HouseholdRead)
def get_household_by_id(household_id: int, db: Session = Depends(get_db)):
    household = (
        db.query(Household)
        .filter(Household.id == household_id)
        .options(
            selectinload(Household.household_members).selectinload(HouseholdMember.user),
            selectinload(Household.household_accounts).selectinload(HouseholdAccount.account),
        )
        .first()
    )
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    return household


# -------------------------
# POST: create_household
# -------------------------
@router.post("/", response_model=HouseholdRead, status_code=status.HTTP_201_CREATED)
def create_household(
    household_in: HouseholdCreate,
    access_token: str = Depends(verify_token),
    auth0_users: authentication.Users = Depends(get_auth0_users_client),
    db: Session = Depends(get_db),
):
    """Create a household. If owner_id is not provided, default to the current user.

    Example request body:
    {
      "name": "My Family",
      "owner_id": 123  # optional
    }
    """
    current_user_id = _get_current_user_id(access_token, auth0_users)

    owner_id = getattr(household_in, "owner_id", None) or current_user_id

    new_household = Household(name=household_in.name, owner_id=owner_id)
    db.add(new_household)
    db.commit()
    db.refresh(new_household)

    # Also create a HouseholdMember mapping for the owner with role 'Admin'
    try:
        owner_member = (
            db.query(HouseholdMember)
            .filter(HouseholdMember.household_id == new_household.id, HouseholdMember.user_id == owner_id)
            .first()
        )
        if not owner_member:
            owner_member = HouseholdMember(household_id=new_household.id, user_id=owner_id, role="Admin")
            db.add(owner_member)
            db.commit()
            db.refresh(owner_member)
    except Exception:
        # If member insert fails for any reason, roll back household creation to avoid partial state
        db.rollback()
        raise

    return new_household


# -------------------------
# DELETE: delete_household
# -------------------------
@router.delete("/{household_id}")
def delete_household(
    household_id: int,
    access_token: str = Depends(verify_token),
    auth0_users: authentication.Users = Depends(get_auth0_users_client),
    db: Session = Depends(get_db),
):
    """Delete a household and cascade-delete related accounts and members.

    Only the household owner may delete the household.
    """
    current_user_id = _get_current_user_id(access_token, auth0_users)

    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    if household.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Only the household owner may delete the household")

    db.delete(household)
    db.commit()

    return {"detail": "Household deleted"}


# -------------------------
# POST: add_household_member
# -------------------------
@router.post("/{household_id}/members", response_model=HouseholdMemberRead, status_code=status.HTTP_201_CREATED)
def add_household_member(
    household_id: int,
    member_in: HouseholdMemberCreate,
    db: Session = Depends(get_db),
    access_token: str = Depends(verify_token),
    auth0_users: authentication.Users = Depends(get_auth0_users_client),
):
    """Add a member to a household. Role defaults to 'member' if not provided.

    Example body:
    {
      "user_id": 42,
      "role": "member"  # optional
    }
    """
    # Ensure household exists
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    # default role
    role = member_in.role or "member"

    # prevent duplicate membership (optional, but helpful)
    existing = (
        db.query(HouseholdMember)
        .filter(HouseholdMember.household_id == household_id, HouseholdMember.user_id == member_in.user_id)
        .first()
    )
    if existing:
        return existing

    member = HouseholdMember(household_id=household_id, user_id=member_in.user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)

    return member


# -------------------------
# DELETE: delete_household_members
# -------------------------
class DeleteMembersRequest(BaseModel):
    user_ids: List[int]


@router.delete("/{household_id}/members")
def delete_household_members(
    household_id: int,
    body: DeleteMembersRequest,
    access_token: str = Depends(verify_token),
    auth0_users: authentication.Users = Depends(get_auth0_users_client),
    db: Session = Depends(get_db),
):
    """Remove the specified user_ids from the household members list.

    Only the household owner may perform this action.
    """
    current_user_id = _get_current_user_id(access_token, auth0_users)

    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    if household.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Only the household owner may remove members")

    # perform delete
    res = (
        db.query(HouseholdMember)
        .filter(HouseholdMember.household_id == household_id, HouseholdMember.user_id.in_(body.user_ids))
        .delete(synchronize_session=False)
    )
    db.commit()

    return {"deleted": res}
