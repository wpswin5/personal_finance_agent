import typing
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel, AnyUrl, EmailStr

from auth0.exceptions import Auth0Error

from app.security.utils import verify_token
from app.dependencies import get_auth0_users_client, get_auth0_management_client, authentication, management
from app.config import get_settings, Settings
from app.repositories.user_repository import user_repository

router = APIRouter()

settings: Settings = get_settings()

@router.get("/id")
async def get_current_user_id(
    access_token: str = Depends(verify_token),
    auth0_users: authentication.Users = Depends(get_auth0_users_client)
) -> int:
    try:
        userinfo = auth0_users.userinfo(access_token=access_token)
        user_id = user_repository.get_id(userinfo.get("sub"))
        print("User id: ", user_id)
    except Auth0Error as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except:
        raise
    return user_id

@router.get("/me")
async def read_user_me(
    access_token: str = Depends(verify_token), 
    auth0_users: authentication.Users = Depends(get_auth0_users_client)
) -> dict:
    try:
        userinfo = auth0_users.userinfo(access_token=access_token)
        user_repository.upsert_user(userinfo)
    except Auth0Error as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except:
        raise
    return userinfo

class CreateUser(BaseModel):
    connection: str = settings.AUTH0_DEFAULT_DB_CONNECTION
    email: EmailStr
    password: str
    name: str
    verify_email: bool = False  # Whether the user will receive a verification email after creation (true) or no email (false). Overrides behavior of email_verified parameter.
    email_verified: typing.Optional[
        bool
    ] = False  # Whether this email address is verified (true) or unverified (false). User will receive a verification email after creation if email_verified is false or not specified
    given_name: typing.Optional[str] = None
    family_name: typing.Optional[str] = None
    nickname: typing.Optional[str] = None
    picture: typing.Optional[AnyUrl] = None
@router.post("/")
async def create_new_user(
    create_user: CreateUser,
    auth0_mgmt_client: management.Auth0 = Depends(get_auth0_management_client)
):
    """
    Create user in auth0.
    if verify_email=True -> send verification mail
    """
    # Create user in auth0 db
    try:
        response = auth0_mgmt_client.users.create(
            body=create_user.dict(exclude_none=True)
        )
    except Auth0Error as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return  response

@router.delete("/{user_id}", dependencies=[Depends(verify_token)])
async def delete_user(
    user_id: str,
    auth0_mgmt_client: management.Auth0 = Depends(get_auth0_management_client)
):
    """
    Remove user from auth0.
    """
    try:
        response = auth0_mgmt_client.users.delete(id=user_id)
    except Auth0Error as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return {
        "auth0": response
    }



# from fastapi import APIRouter, Depends
# from app.security.utils import VerifyToken
# from app.db import get_connection


# router = APIRouter()
# auth = VerifyToken

# @router.get("/me")
async def get_me(user: dict=Depends(verify_token)):
    # Persist user if first login
    user_repository.upsert_user(user)
    return user