"""
Health check endpoint.

Not part of the business domain — used to verify the API is up and can
reach PostgreSQL. Useful for Docker healthchecks and for confirming Phase 1
wiring works before Phase 2 adds real entities.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
