"""
AMS Platform — FastAPI application entrypoint.

Phase 1: project setup only. Real routers (auth, employees, assets, ...)
are registered here one phase at a time, starting with Phase 4 (auth).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    agent,
    assets,
    assignments,
    audit,
    auth,
    components,
    dashboards,
    documents,
    employees,
    health,
    notifications,
    reference,
    reports,
    repairs,
    returns_transfers,
    software,
    sso,
    users,
    warranties,
)
from app.core.config import settings
from app.core.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(employees.router, prefix=settings.API_V1_PREFIX)
app.include_router(assets.router, prefix=settings.API_V1_PREFIX)
app.include_router(components.router, prefix=settings.API_V1_PREFIX)
app.include_router(software.router, prefix=settings.API_V1_PREFIX)
app.include_router(assignments.router, prefix=settings.API_V1_PREFIX)
app.include_router(returns_transfers.router, prefix=settings.API_V1_PREFIX)
app.include_router(repairs.router, prefix=settings.API_V1_PREFIX)
app.include_router(warranties.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboards.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(agent.router, prefix=settings.API_V1_PREFIX)
app.include_router(reference.router, prefix=settings.API_V1_PREFIX)
app.include_router(sso.router, prefix=settings.API_V1_PREFIX, tags=["auth"])


@app.get("/")
def root() -> dict:
    return {"service": settings.PROJECT_NAME, "version": settings.VERSION, "status": "running"}
