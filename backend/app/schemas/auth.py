"""Auth schemas (Phase 4)."""
from pydantic import BaseModel, EmailStr, field_validator
from app.core.password_policy import validate_password_strength


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str = ""


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
