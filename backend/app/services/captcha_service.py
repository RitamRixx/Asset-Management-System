"""
hCaptcha verification (IAM Phase 10).

Server-side-only: the frontend gets a widget + site key and sends us back
a response token, which we verify against hCaptcha's siteverify endpoint
using our *secret* key — the secret never reaches the browser. Fails
closed (verification error/timeout = reject the login attempt) rather
than failing open, since the entire point is blocking scripted attempts;
silently skipping verification on a network hiccup would defeat that.
"""
import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("ams.captcha")

_VERIFY_URL = "https://hcaptcha.com/siteverify"


def verify_captcha(token: str) -> None:
    if not settings.HCAPTCHA_ENABLED:
        return

    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CAPTCHA verification is required.")

    try:
        response = httpx.post(
            _VERIFY_URL,
            data={"secret": settings.HCAPTCHA_SECRET_KEY, "response": token},
            timeout=5.0,
        )
        result = response.json()
    except (httpx.HTTPError, ValueError):
        logger.exception("hCaptcha verification request failed")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Could not verify CAPTCHA. Please try again."
        )

    if not result.get("success"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CAPTCHA verification failed. Please try again.")