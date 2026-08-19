"""
Report generation (section 36).

Implements three representative reports end-to-end (Asset Inventory,
Employee Asset, Warranty) as CSV — the rest of section 36's list (Software
License, Repair, Transfer History, Assignment History, Return, Missing
Asset, Retired Asset, Department Asset) follows the exact same
query-then-csv.writer pattern and is a natural extension point, called out
in the README rather than stubbed out here.
"""
import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.asset_type import AssetType
from app.models.assignment import AssignmentItem, AssetAssignment
from app.models.employee import Employee
from app.models.enums import AssignmentStatus
from app.models.warranty import Warranty


def _csv_from_rows(header: list[str], rows: list[list]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def asset_inventory_report(db: Session) -> str:
    stmt = select(Asset, AssetType.name).join(AssetType, Asset.asset_type_id == AssetType.id)
    rows = [
        [
            asset.asset_code,
            type_name,
            asset.manufacturer or "",
            asset.model or "",
            asset.serial_number or "",
            asset.status.value,
            asset.condition.value,
            str(asset.purchase_date or ""),
            str(asset.purchase_cost or ""),
        ]
        for asset, type_name in db.execute(stmt).all()
    ]
    header = [
        "Asset Code", "Type", "Manufacturer", "Model", "Serial Number",
        "Status", "Condition", "Purchase Date", "Purchase Cost",
    ]
    return _csv_from_rows(header, rows)


def employee_asset_report(db: Session) -> str:
    stmt = (
        select(Employee, Asset)
        .join(AssetAssignment, AssetAssignment.employee_id == Employee.id)
        .join(AssignmentItem, AssignmentItem.assignment_id == AssetAssignment.id)
        .join(Asset, Asset.id == AssignmentItem.asset_id)
        .where(AssignmentItem.status == AssignmentStatus.ACTIVE)
        .order_by(Employee.employee_code)
    )
    rows = [
        [employee.employee_code, employee.full_name, employee.email, asset.asset_code, asset.model or ""]
        for employee, asset in db.execute(stmt).all()
    ]
    header = ["Employee Code", "Employee Name", "Email", "Asset Code", "Asset Model"]
    return _csv_from_rows(header, rows)


def warranty_report(db: Session) -> str:
    stmt = select(Warranty, Asset.asset_code).join(Asset, Warranty.asset_id == Asset.id)
    rows = [
        [
            asset_code,
            str(warranty.warranty_start or ""),
            str(warranty.warranty_end or ""),
            warranty.warranty_type or "",
            warranty.computed_status,
        ]
        for warranty, asset_code in db.execute(stmt).all()
    ]
    header = ["Asset Code", "Warranty Start", "Warranty End", "Warranty Type", "Status"]
    return _csv_from_rows(header, rows)
