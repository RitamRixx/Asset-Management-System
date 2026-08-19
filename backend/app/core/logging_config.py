"""
Logging configuration.

Without this, custom loggers (e.g. app.services.email_service's
"ams.email") propagate to the root logger, which has no handler attached
by default — uvicorn only configures its own named loggers, not root — so
`logger.info(...)` calls anywhere in application code are silently
swallowed rather than actually appearing anywhere. Calling this once at
startup (see app/main.py) fixes that for every module in the app, not
just email.
"""
import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
