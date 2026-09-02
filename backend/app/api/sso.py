"""
Microsoft Entra SSO router (IAM Phase 3).

Both endpoints are public (no bearer auth) — that's the point, this *is*
how a bearer token gets issued. `/auth/sso/login` hands back the Microsoft
authorization URL for the frontend to redirect to; `/auth/sso/callback` is
what Microsoft redirects back to, and is where the actual token exchange
happens, entirely server-side.
"""
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.core.security import create_access_token
# from app.schemas.auth import Token
# from app.schemas.sso import SsoLoginResponse
# from app.services import entra_service

# router = APIRouter(prefix="/auth/sso", tags=["auth"])


# @router.get("/login", response_model=SsoLoginResponse)
# def sso_login() -> SsoLoginResponse:
#     return SsoLoginResponse(authorization_url=entra_service.build_authorization_url())


# @router.get("/callback", response_model=Token)
# def sso_callback(code: str, state: str, db: Session = Depends(get_db)) -> Token:
#     user = entra_service.handle_callback(db, code=code, state=state)
#     db.commit()
#     token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
#     return Token(access_token=token)


"""
Microsoft Entra SSO router (IAM Phase 3).

`/auth/sso/login` is called by the frontend (fetch, not a navigation) and
hands back the Microsoft authorization URL to redirect the browser to.
`/auth/sso/callback` is what Microsoft redirects the browser back to after
the user authenticates — since this is a real browser navigation, not a
fetch, it can't return JSON usefully. Instead it does the token exchange
server-side and then 302s the browser to the frontend's callback route
with either `?token=...` or `?sso_error=...` in the query string, mirroring
how OAuth implicit/hybrid flows typically hand a token to an SPA.
"""
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.sso import SsoLoginResponse
from app.services import entra_service

router = APIRouter(prefix="/auth/sso", tags=["auth"])


@router.get("/login", response_model=SsoLoginResponse)
def sso_login() -> SsoLoginResponse:
    return SsoLoginResponse(authorization_url=entra_service.build_authorization_url())


@router.get("/callback")
def sso_callback(code: str, state: str, db: Session = Depends(get_db)) -> RedirectResponse:
    callback_path = f"{settings.FRONTEND_BASE_URL}/sso/callback"
    try:
        user = entra_service.handle_callback(db, code=code, state=state)
        db.commit()
    except HTTPException as exc:
        db.rollback()
        query = urlencode({"sso_error": str(exc.detail)})
        return RedirectResponse(url=f"{callback_path}?{query}")

    token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    query = urlencode({"token": token})
    return RedirectResponse(url=f"{callback_path}?{query}")