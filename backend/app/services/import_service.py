"""
Bulk CSV import.

Each row is wrapped in its own `db.begin_nested()` SAVEPOINT: if a row
fails (bad data, duplicate serial/email, whatever), only that row's
savepoint rolls back — rows already processed earlier in the same batch
stay staged for the final `db.commit()` at the API layer, and rows after
it still get a fair attempt. Without per-row savepoints, a single bad row
partway through a 500-row file would either poison the whole transaction
(everything after silently no-ops against a session SQLAlchemy has
already marked broken) or force an all-or-nothing import — neither is
what a "bulk import" is supposed to mean.
"""
import csv
import io
from datetime import date
from typing import Any, Callable

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.employee import Employee
from app.models.enums import AssetCondition
from app.repositories import employee_repository
from app.services import asset_service, employee_service


def _read_csv_rows(file_bytes: bytes) -> list[dict[str, str]]:
    try:
        text = file_bytes.decode("utf-8-sig")  # -sig: tolerates a BOM from Excel exports
    except UnicodeDecodeError:
        raise HTTPException(400, "File is not valid UTF-8 text. Export the CSV as UTF-8.")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(400, "CSV has no header row.")
    return list(reader)


def _error_message(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        return str(exc.detail)
    if isinstance(exc, IntegrityError):
        # Never surface the raw SQL/parameter dump from a DB constraint
        # violation — extract just the constraint name via psycopg2's
        # diagnostics (falling back to a generic message if unavailable)
        # instead. Belt-and-suspenders alongside the explicit pre-checks
        # below: this also covers any constraint those checks don't name.
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint:
            return f"Duplicate or invalid value (violates '{constraint}')."
        return "This row conflicts with an existing record."
    return str(exc)


def _run_import(
    db: Session, rows: list[dict[str, str]], build_and_create: Callable[[dict[str, str]], Any]
) -> dict:
    created = 0
    errors: list[dict] = []

    for i, row in enumerate(rows, start=2):  # row 1 is the header
        try:
            with db.begin_nested():
                build_and_create(row)
            created += 1
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see module docstring
            errors.append({"row": i, "message": _error_message(exc)})

    return {"created": created, "skipped": len(errors), "errors": errors}


def import_employees(db: Session, file_bytes: bytes, actor_user_id: int) -> dict:
    rows = _read_csv_rows(file_bytes)

    def build_and_create(row: dict[str, str]) -> Employee:
        first_name = (row.get("first_name") or "").strip()
        last_name = (row.get("last_name") or "").strip()
        email = (row.get("email") or "").strip()
        if not first_name or not last_name or not email:
            raise ValueError("first_name, last_name, and email are required")

        data: dict[str, Any] = {"first_name": first_name, "last_name": last_name, "email": email}
        if row.get("department_id"):
            data["department_id"] = int(row["department_id"])
        if row.get("location_id"):
            data["location_id"] = int(row["location_id"])
        if row.get("org_unit_id"):
            data["org_unit_id"] = int(row["org_unit_id"])
        if row.get("designation"):
            data["designation"] = row["designation"].strip()
        if row.get("joining_date"):
            data["joining_date"] = date.fromisoformat(row["joining_date"].strip())

        # Mirrors the pre-check in api/employees.py's single-create endpoint
        # so a duplicate email produces the same clean message here as it
        # does there, rather than falling through to the generic
        # IntegrityError translation above.
        if employee_repository.get_by_email(db, email) is not None:
            raise ValueError(f"An employee with email {email} already exists")

        return employee_service.create_employee(db, data, actor_user_id)

    return _run_import(db, rows, build_and_create)


def import_assets(db: Session, file_bytes: bytes, actor_user_id: int) -> dict:
    rows = _read_csv_rows(file_bytes)

    def build_and_create(row: dict[str, str]) -> Asset:
        asset_type_raw = (row.get("asset_type_id") or "").strip()
        if not asset_type_raw:
            raise ValueError("asset_type_id is required")

        data: dict[str, Any] = {"asset_type_id": int(asset_type_raw)}
        if row.get("manufacturer"):
            data["manufacturer"] = row["manufacturer"].strip()
        if row.get("model"):
            data["model"] = row["model"].strip()
        if row.get("serial_number"):
            data["serial_number"] = row["serial_number"].strip()
        if row.get("purchase_date"):
            data["purchase_date"] = date.fromisoformat(row["purchase_date"].strip())
        if row.get("purchase_cost"):
            data["purchase_cost"] = row["purchase_cost"].strip()
        if row.get("condition"):
            data["condition"] = AssetCondition(row["condition"].strip().upper())
        if row.get("org_unit_id"):
            data["org_unit_id"] = int(row["org_unit_id"])

        return asset_service.create_asset(db, data, actor_user_id)

    return _run_import(db, rows, build_and_create)
