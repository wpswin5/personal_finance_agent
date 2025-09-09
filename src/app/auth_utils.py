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


token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiJlYTIwNDMzMC00ZTQ3LTQ5ZTItODQ5OC04ZGVjNWUxODI2OWEiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vNWM2MDk5OWItOThhMS00Mzk1LWE2YzgtMmVmMDg1ZjQyZWZmL3YyLjAiLCJpYXQiOjE3NTczNzY1MjIsIm5iZiI6MTc1NzM3NjUyMiwiZXhwIjoxNzU3MzgwNDIyLCJhaW8iOiJrMlJnWUxoKzVxbVVxOEJDOWZmSHo3VWtSQ3dTY1dleW1qNnRNYStpV2ZHVWk0Q1l4QlVBIiwiYXpwIjoiZDJmYWFiMzItNmU4Ny00NWNhLWI5ODMtZjAxYWIwOTI4ZTkzIiwiYXpwYWNyIjoiMSIsIm9pZCI6ImI1OTA2MDk5LTgxZDUtNDFlZC1iZmM1LTdkODg5YjhjZTRkMyIsInJoIjoiMS5BYzhBbTVsZ1hLR1lsVU9teUM3d2hmUXVfekJESU9wSFR1SkpoSmlON0Y0WUpwclBBQURQQUEuIiwic3ViIjoiYjU5MDYwOTktODFkNS00MWVkLWJmYzUtN2Q4ODliOGNlNGQzIiwidGlkIjoiNWM2MDk5OWItOThhMS00Mzk1LWE2YzgtMmVmMDg1ZjQyZWZmIiwidXRpIjoicU1ScF9jNV9FVWV5aXBuSXU5RUVBQSIsInZlciI6IjIuMCIsInhtc19mdGQiOiJPUVhPZUsyZUZLaFhiWG1hSnoyRUlnSXVwRzRpMGE4ZXFhRVZhOGhCRGlvQmRYTmxZWE4wTFdSemJYTSJ9.Bvd3W1OBrAkXdF3zXEbe9qW1m9m5H9BFLkT2ks8uonlHHv5wApUwQGTD1lZpmKDOCUqDOuq3ElrnL9Fuohv4__BglNxBLV42gvWc0uP0eWhqyESEBSfMq2tdv3mtBugXzjTXlNzPvgMXyyzGRDTdTQ2xIAJ63cBigdaRLAetrN9_JS2uqu3ClLMSrC-2lCacZBBdCiBC4JkbNefL-33aUmLD5g-zROWsq32JLb6ITF7nlhHiSZti-3cIZlcrzo4C-WCJy6kMhFWnDp6JNY2JlkTj4luQiNynp5KQphcPYxv6EFWr0ojOuaXUpJqVR83UFtVjWLQnRwjGxoeK_5Ig1g"

decoded = jwt.get_unverified_claims(token)
print("aud:", decoded.get("aud"))
print("iss:", decoded.get("iss"))
print("scp:", decoded.get("scp"))

print(decoded)


def validate_token(credentials=Security(bearer_scheme)):
    if not credentials:
        print("no creds")
        raise HTTPException(401, "Not authenticated")
    token = credentials.credentials
    try:
        print("creds: " + token)
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
