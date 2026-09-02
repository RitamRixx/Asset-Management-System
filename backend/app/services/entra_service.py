"""
Microsoft Entra ID SSO business logic (IAM Phase 3).

Authorization Code Flow with PKCE, token exchange handled entirely
server-side per the IAM roadmap ("backend-only token exchange") — the
frontend only ever sees our own JWT, never a Microsoft token. `msal`
(Microsoft's own library) validates the ID token's signature, issuer,
audience, and nonce internally during acquire_token_by_authorization_code;
this module adds the one check MSAL doesn't know to make for us: that the
token's tenant (`tid`) matches ENTRA_ALLOWED_TENANT_ID, since an app
registration alone doesn't guarantee single-tenant enforcement.

No self-signup, same rule as local auth (see api/auth.py's docstring): a
Microsoft sign-in only succeeds against an AMS User row an Admin already
created, matched by email. On first successful SSO login for that row,
this module *links* it to the Entra identity rather than creating a new
row.
"""
import base64
import hashlib
import secrets
from datetime import datetime, timezone

import msal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_sso_state_token, decode_sso_state_token
from app.models.enums import AuthProvider, UserStatus
from app.models.user import User
from app.repositories import user_repository
from app.services import audit_service

_AUTHORITY_TEMPLATE = "https://login.microsoftonline.com/{tenant_id}"
# Only need the ID token's identity claims — this app never calls Graph on
# the user's behalf, so no broader scope is requested.
_SCOPES = ["User.Read"]


def _require_entra_enabled() -> None:
    if not settings.ENTRA_ENABLED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Microsoft sign-in is not enabled.")


def _msal_app() -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        client_id=settings.ENTRA_CLIENT_ID,
        client_credential=settings.ENTRA_CLIENT_SECRET,
        authority=_AUTHORITY_TEMPLATE.format(tenant_id=settings.ENTRA_TENANT_ID),
    )


def _generate_pkce_pair() -> tuple[str, str]:
    """(code_verifier, code_challenge) per RFC 7636, S256 method."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def build_authorization_url() -> str:
    _require_entra_enabled()

    code_verifier, code_challenge = _generate_pkce_pair()
    nonce = secrets.token_urlsafe(32)
    state = create_sso_state_token({"code_verifier": code_verifier, "nonce": nonce})

    app = _msal_app()
    return app.get_authorization_request_url(
        scopes=_SCOPES,
        state=state,
        redirect_uri=settings.ENTRA_REDIRECT_URI,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )


def _find_or_link_user(db: Session, claims: dict) -> User:
    email = claims.get("preferred_username") or claims.get("email")
    object_id = claims.get("oid")
    tenant_id = claims.get("tid")

    if not email or not object_id or not tenant_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Microsoft did not return the expected identity claims.",
        )

    # Already-linked identity — the common case after the first login.
    user = user_repository.get_by_entra_identity(db, object_id, tenant_id)
    if user is not None:
        return user

    # First SSO login for this identity: only proceed if an Admin already
    # created a matching AMS account (no self-signup — same rule as local
    # auth).
    user = user_repository.get_by_email(db, email)
    if user is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "No AMS account exists for this Microsoft identity. Ask an administrator to create one first.",
        )

    old_provider = user.auth_provider
    user.auth_provider = AuthProvider.MICROSOFT
    user.entra_object_id = object_id
    user.entra_tenant_id = tenant_id
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=user.id,
        action="SSO_ACCOUNT_LINKED",
        entity_type="User",
        entity_id=user.id,
        old_value={"auth_provider": old_provider.value},
        new_value={"auth_provider": AuthProvider.MICROSOFT.value},
    )
    return user


def handle_callback(db: Session, *, code: str, state: str) -> User:
    _require_entra_enabled()

    state_payload = decode_sso_state_token(state)
    if state_payload is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Sign-in link expired or is invalid. Please try again."
        )

    app = _msal_app()
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=_SCOPES,
        redirect_uri=settings.ENTRA_REDIRECT_URI,
        code_verifier=state_payload["code_verifier"],
        nonce=state_payload["nonce"],
    )

    if "error" in result:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            f"Microsoft sign-in failed: {result.get('error_description', result['error'])}",
        )

    # MSAL has already validated signature/issuer/audience/nonce by this
    # point — id_token_claims is trustworthy.
    claims = result.get("id_token_claims", {})

    if settings.ENTRA_ALLOWED_TENANT_ID and claims.get("tid") != settings.ENTRA_ALLOWED_TENANT_ID:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This Microsoft account's organization is not permitted."
        )

    user = _find_or_link_user(db, claims)

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account is disabled.")

    user.last_login = datetime.now(timezone.utc)
    db.flush()

    audit_service.log_action(
        db, actor_user_id=user.id, action="SSO_LOGIN", entity_type="User", entity_id=user.id
    )
    return user