"""
Password hashing and JWT helpers (Phase 4).

- Passwords: Argon2 via passlib. Never store or log plaintext passwords.
- Tokens: JWT (python-jose), signed with settings.JWT_SECRET_KEY.
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_SSO_STATE_TOKEN_TYPE = "sso_state"
_SSO_STATE_EXPIRE_MINUTES = 10

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, extra_claims: Optional[dict[str, Any]] = None) -> str:
    """`subject` is the user id (as a string, per JWT convention for `sub`)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # payload: dict[str, Any] = {"sub": subject, "exp": expire}
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "jti": secrets.token_urlsafe(16)}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def create_sso_state_token(data: dict[str, Any]) -> str:
    """Short-lived, signed token carrying the PKCE verifier + nonce through
    Microsoft's redirect round-trip (see services/entra_service.py). Not an
    access token — gets its own `typ` claim and a much shorter expiry than
    create_access_token's, so it can't be reused as a bearer token even if
    it leaked in a referrer header somewhere."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=_SSO_STATE_EXPIRE_MINUTES)
    payload: dict[str, Any] = {**data, "typ": _SSO_STATE_TOKEN_TYPE, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_sso_state_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
    if payload.get("typ") != _SSO_STATE_TOKEN_TYPE:
        return None
    return payload