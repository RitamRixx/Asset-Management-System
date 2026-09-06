"""
Auth router (Phase 4).

Only `/auth/login` lives here. There is deliberately no `/auth/register` —
per section 7, users do not self-register; accounts are created by Admins
via `POST /api/v1/users` (see users.py).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, Token
from app.services import auth_service, password_reset_service
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.schemas.auth import LoginRequest, Token
from app.api.deps import get_current_user
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.repositories import revoked_token_repository
from app.services import auth_service, captcha_service

router = APIRouter()


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    captcha_service.verify_captcha(payload.captcha_token)
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account is disabled",
        )
    db.commit()
    # token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    token, jti, expire = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    from app.models.issued_token import IssuedToken
    from app.repositories import issued_token_repository
    issued_token_repository.create(db, IssuedToken(jti=jti, user_id=user.id, expires_at=expire))
    db.commit()
    return Token(access_token=token)


@router.post("/auth/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    password_reset_service.request_password_reset(db, payload.email)
    db.commit()
    return {"detail": "If an account exists for this email, a reset link has been sent."}


@router.post("/auth/reset-password", response_model=Token)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> Token:
    user = password_reset_service.reset_password(db, payload.token, payload.new_password)
    db.commit()
    token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    return Token(access_token=token)

@router.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    auth_header = request.headers.get("Authorization", "")
    raw_token = auth_header.removeprefix("Bearer ").strip()
    payload = decode_access_token(raw_token)

    if payload and payload.get("jti"):
        revoked_token_repository.create(
            db,
            RevokedToken(
                jti=payload["jti"],
                user_id=current_user.id,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            ),
        )
        db.commit()

    return {"message": "Logged out."}