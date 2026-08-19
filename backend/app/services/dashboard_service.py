"""
Dashboard aggregation (section 34). Each function returns exactly the
fields that section lists for that role's panel — kept as plain dicts
rather than heavy schemas since dashboards are read-only, shape-stable
summaries, not domain entities.
"""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assignment import AssetAssignment
from app.models.audit import AuditLog
from app.models.employee import Employee
from app.models.enums import (
    AssetStatus,
    EmploymentStatus,
    LicenseStatus,
    RepairStatus,
)
from app.models.repair import RepairTicket
from app.models.software import SoftwareLicense
from app.repositories import asset_repository, warranty_repository


def admin_dashboard(db: Session) -> dict:
    total_employees = db.scalar(select(func.count(Employee.id)))
    active_employees = db.scalar(
        select(func.count(Employee.id)).where(Employee.employment_status == EmploymentStatus.ACTIVE)
    )
    asset_counts = asset_repository.count_by_status(db)

    recent_activity = list(
        db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(20))
    )

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_assets": sum(asset_counts.values()),
        "assets_by_status": asset_counts,
        "warranties_expiring_soon": len(warranty_repository.list_expiring_soon(db)),
        "licenses_expiring_soon": db.scalar(
            select(func.count(SoftwareLicense.id)).where(
                SoftwareLicense.expiry_date.is_not(None),
                SoftwareLicense.expiry_date >= date.today(),
                SoftwareLicense.expiry_date <= date.today() + timedelta(days=30),
            )
        ),
        "recent_activity": [
            {
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in recent_activity
        ],
    }


def it_dashboard(db: Session) -> dict:
    asset_counts = asset_repository.count_by_status(db)
    open_repair_statuses = [
        s for s in RepairStatus if s not in (RepairStatus.CLOSED, RepairStatus.CANCELLED, RepairStatus.RESOLVED)
    ]
    open_repairs = db.scalar(
        select(func.count(RepairTicket.id)).where(RepairTicket.status.in_(open_repair_statuses))
    )
    pending_acknowledgment = db.scalar(
        select(func.count(AssetAssignment.id)).where(AssetAssignment.acknowledged_at.is_(None))
    )

    return {
        "available_assets": asset_counts.get(AssetStatus.AVAILABLE.value, 0),
        "assigned_assets": asset_counts.get(AssetStatus.ASSIGNED.value, 0),
        "assets_under_repair": asset_counts.get(AssetStatus.UNDER_REPAIR.value, 0),
        "pending_assignment_acknowledgments": pending_acknowledgment,
        "open_repair_tickets": open_repairs,
        "warranties_expiring_soon": len(warranty_repository.list_expiring_soon(db)),
        "licenses_expiring_soon": db.scalar(
            select(func.count(SoftwareLicense.id)).where(
                SoftwareLicense.expiry_date.is_not(None),
                SoftwareLicense.expiry_date >= date.today(),
                SoftwareLicense.expiry_date <= date.today() + timedelta(days=30),
            )
        ),
        # Section 37: no live agent exists yet in this phase of the build.
        "agent_status": "not_implemented",
    }


def hr_dashboard(db: Session) -> dict:
    today = date.today()
    total_employees = db.scalar(select(func.count(Employee.id)))
    new_joiners_30d = db.scalar(
        select(func.count(Employee.id)).where(
            Employee.joining_date.is_not(None),
            Employee.joining_date >= today - timedelta(days=30),
            Employee.joining_date <= today,
        )
    )
    upcoming_joiners = db.scalar(
        select(func.count(Employee.id)).where(
            Employee.joining_date.is_not(None), Employee.joining_date > today
        )
    )
    on_notice_period = db.scalar(
        select(func.count(Employee.id)).where(
            Employee.employment_status == EmploymentStatus.NOTICE_PERIOD
        )
    )

    return {
        "total_employees": total_employees,
        "new_joiners_last_30_days": new_joiners_30d,
        "upcoming_joiners": upcoming_joiners,
        "employees_on_notice_period": on_notice_period,
    }
