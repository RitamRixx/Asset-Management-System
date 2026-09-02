"""
Shared FastAPI dependencies for auth + RBAC (sections 5-7 of the spec).

Every protected router imports `get_current_user` and, where applicable,
`require_role(...)` from here. Frontend route guards are cosmetic only —
this module is the actual enforcement point, per the spec's own instruction
that "frontend hiding a button is NOT security."
"""
from typing import Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import Role
from app.core.security import decode_access_token
from app.models.enums import UserStatus
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_error

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise credentials_error

    # if user.status != UserStatus.ACTIVE:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Account is disabled",
    #     )
    
    if user.status != UserStatus.ACTIVE:
        detail = {
            UserStatus.DISABLED: "Account is disabled",
            UserStatus.SUSPENDED: "Account is suspended",
            UserStatus.PENDING: "Account is pending activation",
        }.get(user.status, "Account is not active")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return user


def require_role(*allowed_roles: Role):
    """Usage: `Depends(require_role(Role.ADMIN, Role.IT_SUPPORT))`."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )
        return current_user

    return _check


def require_self_or_role(employee_id_param: str, *allowed_roles: Role):
    """
    For endpoints scoped to "my own record OR a privileged role" (rule #14:
    "Employees can only see their own assets"). Compares the path
    parameter named `employee_id_param` against the current user's linked
    Employee record.
    """

    def _check(request: Request, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role in allowed_roles:
            return current_user

        path_employee_id = request.path_params.get(employee_id_param)
        if path_employee_id is not None and current_user.employee_id == int(path_employee_id):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own records",
        )

    return _check
