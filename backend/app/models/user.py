"""
User model (section 9 of the spec).

Auth identity is deliberately kept separate from Employee profile data:
every User is optionally linked to an Employee record (an IT/HR/Admin user
might not have — or might also have — an employee profile), but the two
lifecycles are independent.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.permissions import Role
from app.models.enums import UserStatus
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"), unique=True
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    # Argon2 hash (see app.core.security, Phase 4). Never store plaintext.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.EMPLOYEE, nullable=False)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
