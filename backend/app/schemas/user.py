"""
User schemas (Phase 4).

`UserRead` deliberately excludes `password_hash` — there's no code path
anywhere in this API that returns it, by construction of the schema.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.permissions import Role
from app.models.enums import UserStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role
    employee_id: Optional[int] = None


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
