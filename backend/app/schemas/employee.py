"""Employee schemas (section 10 of the spec)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import EmploymentStatus


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    location_id: Optional[int] = None
    group_id: Optional[int] = None
    joining_date: Optional[date] = None
    profile_photo: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    location_id: Optional[int] = None
    group_id: Optional[int] = None
    profile_photo: Optional[str] = None


class EmployeeStatusUpdate(BaseModel):
    employment_status: EmploymentStatus


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    department_id: Optional[int]
    designation: Optional[str]
    manager_id: Optional[int]
    location_id: Optional[int]
    group_id: Optional[int]
    joining_date: Optional[date]
    employment_status: EmploymentStatus
    profile_photo: Optional[str]
    created_at: datetime
