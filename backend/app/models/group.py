"""
AMS Group model 

A Group is a pure AMS/business organizational concept (Sales, IT Support,
Finance, ...) and is deliberately NOT the same thing as a Microsoft Entra
ID group, nor the same thing as `Department` (org.py) — Department already
has its own established usage across dashboards/reports and is left
untouched. No CRUD API exists for Group yet — that lands alongside the
admin user-management updates in a later IAM phase.
"""
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)