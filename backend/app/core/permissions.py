"""
Role definitions for Role-Based Access Control.

Phase 5 will add the full permission matrix (which role can call which
endpoint / mutate which entity) on top of this enum, plus a
`require_role(...)` FastAPI dependency for enforcing it server-side.

Per section 7 of the spec: frontend hiding a button is NOT security —
every protected endpoint must check this on the backend.
"""
from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    HR = "HR"
    IT_SUPPORT = "IT_SUPPORT"
    EMPLOYEE = "EMPLOYEE"
