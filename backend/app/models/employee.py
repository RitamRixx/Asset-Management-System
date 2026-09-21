"""Employee model (section 10 of the spec)."""
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EmploymentStatus
from app.models.mixins import TimestampMixin


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30))

    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), index=True) # DEPRECATED
    designation: Mapped[Optional[str]] = mapped_column(String(100))
    # Self-referential manager link.
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), index=True)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), index=True) # DEPRECATED
    org_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("org_units.id"), index=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), index=True)

    joining_date: Mapped[Optional[date]] = mapped_column(Date)
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        default=EmploymentStatus.ACTIVE, nullable=False, index=True
    )
    profile_photo: Mapped[Optional[str]] = mapped_column(String(255))

    department: Mapped[Optional["Department"]] = relationship(  # noqa: F821
        back_populates="employees", foreign_keys=[department_id]
    )
    org_unit: Mapped[Optional["OrgUnit"]] = relationship(  # noqa: F821
        foreign_keys=[org_unit_id]
    )
    manager: Mapped[Optional["Employee"]] = relationship(
        remote_side=[id], foreign_keys=[manager_id]
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
