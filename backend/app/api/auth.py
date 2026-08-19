"""
Auth router (Phase 4).

Only `/auth/login` lives here. There is deliberately no `/auth/register` —
per section 7, users do not self-register; accounts are created by Admins
via `POST /api/v1/users` (see users.py).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, Token
from app.services import auth_service

router = APIRouter()


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account is disabled",
        )
    db.commit()
    token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    return Token(access_token=token)
