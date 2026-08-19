"""
Bootstrap seed script.

Run once after migrations, before anyone can log in:

    python -m app.scripts.seed_admin

Creates the first Admin user (from env vars, falling back to safe dev
defaults) and a small set of baseline reference data (asset types,
component types, a default department/location) so the app isn't empty on
first run. Safe to re-run — every insert checks for an existing row first.
"""
import os

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.asset_type import AssetType, ComponentType
from app.models.enums import UserStatus
from app.models.org import Department, Location
from app.core.permissions import Role
from app.models.user import User
from app.repositories import user_repository

DEFAULT_ASSET_TYPES = [
    "Laptop", "Desktop", "Monitor", "Mobile", "Tablet", "Printer",
    "Keyboard", "Mouse", "Headphone", "Charger", "Dock", "UPS",
    "Router", "SSD", "HDD", "RAM", "GPU", "Access Card",
]
DEFAULT_COMPONENT_TYPES = ["CPU", "RAM", "SSD", "HDD", "GPU", "Battery", "Motherboard"]
DEFAULT_DEPARTMENTS = ["IT", "HR", "Finance", "Sales", "Engineering", "Marketing"]


def seed() -> None:
    db = SessionLocal()
    try:
        admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@ams-platform.com")
        admin_password = os.getenv("SEED_ADMIN_PASSWORD", "ChangeMe123!")

        if user_repository.get_by_email(db, admin_email) is None:
            admin = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=Role.ADMIN,
                status=UserStatus.ACTIVE,
            )
            db.add(admin)
            print(f"Created admin user: {admin_email} (change the password after first login)")
        else:
            print(f"Admin user {admin_email} already exists, skipping")

        for name in DEFAULT_ASSET_TYPES:
            if db.query(AssetType).filter_by(name=name).first() is None:
                db.add(AssetType(name=name))

        for name in DEFAULT_COMPONENT_TYPES:
            if db.query(ComponentType).filter_by(name=name).first() is None:
                db.add(ComponentType(name=name))

        for name in DEFAULT_DEPARTMENTS:
            if db.query(Department).filter_by(name=name).first() is None:
                db.add(Department(name=name))

        if db.query(Location).filter_by(name="Kolkata").first() is None:
            db.add(Location(name="Kolkata", city="Kolkata", country="India"))

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
