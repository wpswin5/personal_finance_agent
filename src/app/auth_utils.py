import os
import requests
from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer
from jose import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

#TENANT_ID = os.getenv("TENANT_ID")
#API_CLIENT_ID = os.getenv("API_CLIENT_ID")

#ISSUER = f"https://login.microsoftonline.com/5c60999b-98a1-4395-a6c8-2ef085f42eff/v2.0"
#OPENID_CONFIG = f"{ISSUER}/.well-known/openid-configuration"

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]

jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
jwks_client = PyJWKClient(jwks_url)

#config = requests.get(OPENID_CONFIG).json()
#jwk_client = PyJWKClient(config["jwks_uri"])
#bearer_scheme = HTTPBearer(auto_error=False)

def validate_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        print("no creds")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]  # Bearer <token>
    print("token: " + token)
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(token, signing_key, algorithms=ALGORITHMS, audience=API_AUDIENCE)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {e}")
