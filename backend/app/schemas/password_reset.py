"""Password reset request/confirm schemas (IAM Phase 4)."""
from pydantic import BaseModel, EmailStr, field_validator

from app.core.password_policy import validate_password_strength


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


    @field_validator("new_password")
    @classmethod
    def _check_strength(cls, value: str) -> str:
        errors = validate_password_strength(value)
        if errors:
            raise ValueError(" ".join(errors))
        return value


