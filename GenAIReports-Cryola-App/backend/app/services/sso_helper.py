"""
Responsible for validating ID tokens during SSO authentication.
Fetches JWKS from Microsoft for RS256 validation in production,
and allows HS256 tokens for local testing when SSO_DEV_MODE is enabled.
"""

from app.core.config import settings
from fastapi import HTTPException
from jose import jwt, JWTError, jwk
import requests

MICROSOFT_TENANT_ID = settings.MICROSOFT_TENANT_ID
MICROSOFT_CLIENT_ID = settings.MICROSOFT_CLIENT_ID

_JWKS_CACHE = None

def get_jwks() -> dict:
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        discovery_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration"
        resp = requests.get(discovery_url)
        resp.raise_for_status()
        jwks_uri = resp.json()["jwks_uri"]
        jwks_resp = requests.get(jwks_uri)
        jwks_resp.raise_for_status()
        _JWKS_CACHE = jwks_resp.json()
    return _JWKS_CACHE


def verify_ms_id_token(id_token: str) -> dict:
    # Production mode: verify via JWKS (RS256)
    try:
        headers = jwt.get_unverified_header(id_token)
        kid = headers.get("kid")
        jwks = get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        public_key = jwk.construct(key, algorithm="RS256")
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=MICROSOFT_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/v2.0"
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid ID token: {e}")