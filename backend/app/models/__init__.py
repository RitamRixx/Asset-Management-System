"""
ORM models package.

Every model module is imported here, unconditionally, so that:
  1. `Base.metadata.create_all()` (tests) sees every table.
  2. Alembic's `--autogenerate` sees every table.
  3. Cross-file relationship() string references (e.g. Department <->
     Employee) resolve correctly, since SQLAlchemy needs all mapped classes
     registered before it configures mappers.

Import order doesn't matter for the string-based relationships, but is
kept roughly dependency-first for readability.
"""
from app.models.org import Department, Location, Vendor  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.asset_type import AssetType, ComponentType  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.component import AssetComponent  # noqa: F401
from app.models.software import Software, SoftwareLicense, SoftwareAssignment  # noqa: F401
from app.models.assignment import AssetAssignment, AssignmentItem  # noqa: F401
from app.models.transfer import AssetTransfer  # noqa: F401
from app.models.asset_return import AssetReturn  # noqa: F401
from app.models.repair import RepairTicket, RepairHistory  # noqa: F401
from app.models.warranty import Warranty  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.device_agent import DeviceAgent  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.password_reset import PasswordResetToken
from app.models.organization import OrganizationSettings  # noqa: F401
from app.models.revoked_token import RevokedToken  # noqa: F401

__all__ = [
    "Department",
    "Location",
    "Vendor",
    "Employee",
    "User",
    "AssetType",
    "ComponentType",
    "Asset",
    "AssetComponent",
    "Software",
    "SoftwareLicense",
    "SoftwareAssignment",
    "AssetAssignment",
    "AssignmentItem",
    "AssetTransfer",
    "AssetReturn",
    "RepairTicket",
    "RepairHistory",
    "Warranty",
    "Document",
    "AuditLog",
    "Notification",
    "DeviceAgent",
    "Group",
    "PasswordResetToken",
    "OrganizationSettings",
    "RevokedToken"
]
