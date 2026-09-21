"""Reference/organizational data (sections 11-12 of the spec, plus Vendors)."""
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    # Nullable + no ondelete cascade: a department's manager is just an
    # employee, and employees are never hard-deleted (rule #6), so this
    # never dangles. `use_alter=True` + an explicit name breaks the
    # departments<->employees circular FK cycle (employees.department_id
    # points back here) so Alembic/DDL tooling can create and drop both
    # tables cleanly via a deferred ALTER TABLE.
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id", use_alter=True, name="fk_departments_manager_id")
    )
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department", foreign_keys="Employee.department_id"
    )


class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(150))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)


# Note: `Employee` is referenced above only as a string in relationship()/
# Mapped[list["Employee"]], so no import is needed here. SQLAlchemy resolves
# it against the mapper registry once app.models (see __init__.py) has
# imported every model module — importing this module directly at the top
# would create a circular import with employee.py, which itself refers back
# to Department.

class OrgUnitType(Base, TimestampMixin):
    __tablename__ = "org_unit_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    typical_rank: Mapped[Optional[int]] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)


class OrgUnit(Base, TimestampMixin):
    __tablename__ = "org_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    unit_type_id: Mapped[int] = mapped_column(ForeignKey("org_unit_types.id"), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("org_units.id"), index=True)

    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id", use_alter=True, name="fk_org_units_manager_id")
    )
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    unit_type: Mapped["OrgUnitType"] = relationship()
    parent: Mapped[Optional["OrgUnit"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["OrgUnit"]] = relationship(back_populates="parent")
