import os
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
API_CLIENT_ID = os.getenv("API_CLIENT_ID")

ISSUER = f"https://login.microsoftonline.com/5c60999b-98a1-4395-a6c8-2ef085f42eff/v2.0"
OPENID_CONFIG = f"{ISSUER}/.well-known/openid-configuration"

config = requests.get(OPENID_CONFIG).json()
jwk_client = PyJWKClient(config["jwks_uri"])
bearer_scheme = HTTPBearer(auto_error=False)

def validate_token(credentials=Security(bearer_scheme)):
    if not credentials:
        raise HTTPException(401, "Not authenticated")
    token = credentials.credentials
    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=API_CLIENT_ID,
            issuer=ISSUER,
        )
        return claims
    except Exception as e:
        raise HTTPException(401, f"Token invalid: {e}")
