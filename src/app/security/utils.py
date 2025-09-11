from fastapi import Depends
from fastapi.security import SecurityScopes

from security.oauth import oauth2_scheme
from security.token_tools import AccessToken
from security.token_tools import TokenTools, CREDENTIALS_EXCEPTION


def token_tools_factory(token=Depends(oauth2_scheme)) -> TokenTools:
    return TokenTools(token=token)

def get_verified_token(
    token_tools: TokenTools = Depends(token_tools_factory),
) -> AccessToken:
    return token_tools.verified_claim()


def verify_token(token_tools: TokenTools = Depends(token_tools_factory)) -> str:
    if token_tools.verify():
        return token_tools.token
    else:
        raise CREDENTIALS_EXCEPTION


def verify_token_scoped(scopes: SecurityScopes, token_tools: TokenTools = Depends(token_tools_factory)) -> bool:
    return token_tools.verify(security_scopes=scopes)