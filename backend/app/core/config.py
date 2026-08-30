"""
Application configuration.

All values are loaded from environment variables (see .env.example at the
project root). Nothing sensitive is hardcoded here.
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AMS Platform"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"

    # PostgreSQL connection string, e.g.
    # postgresql+psycopg2://ams_user:ams_password@db:5432/ams_db
    DATABASE_URL: str

    # JWT / auth (Phase 4)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
####
    # Microsoft Entra ID / Microsoft 365 SSO (IAM Phase 3)
    # Disabled by default so local email/password authentication continues
    # to work exactly as before until Entra is explicitly configured.
    ENTRA_ENABLED: bool = False
    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""
    ENTRA_CLIENT_SECRET: str = ""
    ENTRA_REDIRECT_URI: str = ""
    ENTRA_ALLOWED_TENANT_ID: str = ""
####
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Email delivery (section 33: "Notification channels can initially be
    # in-app; later: Email"). Disabled by default so a deployment with no
    # SMTP configured just logs instead of failing — see email_service.py.
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "no-reply@ams-platform.local"
    SMTP_FROM_NAME: str = "AMS Platform"

    # extra="ignore": the shared .env also carries POSTGRES_* vars that only
    # docker-compose/Postgres itself need, not this Settings class.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
