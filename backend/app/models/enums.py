"""
Shared enums for status fields across the domain (section 8-27 of the spec).

Kept in one module so services/schemas can import a single source of truth
instead of redefining string literals everywhere.
"""
import enum


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    NOTICE_PERIOD = "NOTICE_PERIOD"
    RESIGNED = "RESIGNED"
    TERMINATED = "TERMINATED"
    INACTIVE = "INACTIVE"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class AssetStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    RESERVED = "RESERVED"
    UNDER_REPAIR = "UNDER_REPAIR"
    DAMAGED = "DAMAGED"
    LOST = "LOST"
    RETIRED = "RETIRED"
    DISPOSED = "DISPOSED"


class AssetCondition(str, enum.Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"
    DAMAGED = "DAMAGED"


class ComponentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"


class LicenseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"


class SoftwareAssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class AssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    TRANSFERRED = "TRANSFERRED"


class ReturnCondition(str, enum.Enum):
    GOOD = "GOOD"
    DAMAGED = "DAMAGED"
    MISSING = "MISSING"


class TransferStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class RepairPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RepairStatus(str, enum.Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    DIAGNOSING = "DIAGNOSING"
    SENT_TO_VENDOR = "SENT_TO_VENDOR"
    IN_REPAIR = "IN_REPAIR"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class DocumentEntityType(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    ASSET = "ASSET"
    REPAIR = "REPAIR"
    PURCHASE = "PURCHASE"
    WARRANTY = "WARRANTY"
    ASSIGNMENT = "ASSIGNMENT"


class DeviceAgentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
