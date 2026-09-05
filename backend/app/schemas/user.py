"""
User schemas (Phase 4).

`UserRead` deliberately excludes `password_hash` — there's no code path
anywhere in this API that returns it, by construction of the schema.
"""
from datetime import datetime
from typing import Optional

# from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from app.core.password_policy import validate_password_strength

from app.core.permissions import Role
from app.models.enums import UserStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role
    employee_id: Optional[int] = None

    @field_validator("password")
    @classmethod
    def _check_strength(cls, value: str) -> str:
        errors = validate_password_strength(value)
        if errors:
            raise ValueError(" ".join(errors))
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    status: UserStatus
    employee_id: Optional[int]
    last_login: Optional[datetime]
    created_at: datetime


class UserStatusUpdate(BaseModel):
    status: UserStatus

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _check_strength(cls, value: str) -> str:
        errors = validate_password_strength(value)
        if errors:
            raise ValueError(" ".join(errors))
        return value
