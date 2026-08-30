# """
# User model (section 9 of the spec).

# Auth identity is deliberately kept separate from Employee profile data:
# every User is optionally linked to an Employee record (an IT/HR/Admin user
# might not have — or might also have — an employee profile), but the two
# lifecycles are independent.
# """
# from datetime import datetime
# from typing import Optional

# from sqlalchemy import DateTime, ForeignKey, String
# from sqlalchemy.orm import Mapped, mapped_column

# from app.core.database import Base
# from app.core.permissions import Role
# from app.models.enums import UserStatus
# from app.models.mixins import TimestampMixin


# class User(Base, TimestampMixin):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     employee_id: Mapped[Optional[int]] = mapped_column(
#         ForeignKey("employees.id"), unique=True
#     )
#     email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
#     # Argon2 hash (see app.core.security, Phase 4). Never store plaintext.
#     password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
#     role: Mapped[Role] = mapped_column(default=Role.EMPLOYEE, nullable=False)
#     status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE, nullable=False)
#     last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


"""
User model (section 9 of the spec; extended for IAM Phase 2).

Auth identity is deliberately kept separate from Employee profile data:
every User is optionally linked to an Employee record (an IT/HR/Admin user
might not have — or might also have — an employee profile), but the two
lifecycles are independent.

IAM extension: a User now supports two authentication providers (LOCAL,
MICROSOFT). `password_hash` is nullable because a Microsoft-only user has
no AMS-managed password at all — enforced as a service-layer invariant in
auth_service.authenticate_user (a LOCAL-only entry point), not a DB
constraint, to keep this migration additive.

`entra_object_id` + `entra_tenant_id` form a composite unique pair rather
than a single unique column: Microsoft's `oid` claim is only guaranteed
unique *within* a tenant, not globally, so the tenant must be part of the
identity key (see IAM spec section 3). `failed_login_count` / `locked_until`
back lockout/rate-limiting for LOCAL auth only — Microsoft's own
Conditional Access covers brute-force protection for SSO users, so these
stay 0/NULL for MICROSOFT rows.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.permissions import Role
from app.models.enums import AuthProvider, UserStatus
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("entra_object_id", "entra_tenant_id", name="uq_users_entra_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"), unique=True
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    # Nullable: a MICROSOFT-provider user has no AMS-managed password.
    # Argon2 hash when present (see app.core.security). Never store plaintext.
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))

    role: Mapped[Role] = mapped_column(default=Role.EMPLOYEE, nullable=False)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # --- IAM: authentication provider + external identity mapping ---
    auth_provider: Mapped[AuthProvider] = mapped_column(
        default=AuthProvider.LOCAL, nullable=False
    )
    # Microsoft's stable per-tenant identifier — not email. See
    # __table_args__ above for why this is a composite key with tenant.
    entra_object_id: Mapped[Optional[str]] = mapped_column(String(100))
    entra_tenant_id: Mapped[Optional[str]] = mapped_column(String(100))

    # --- IAM: local-auth lockout / rate-limiting state ---
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))