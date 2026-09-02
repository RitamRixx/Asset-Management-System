"""Microsoft Entra SSO schemas (IAM Phase 3)."""
from pydantic import BaseModel


class SsoLoginResponse(BaseModel):
    authorization_url: str