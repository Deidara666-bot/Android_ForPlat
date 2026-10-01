import logging

_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(app_env: str) -> None:
    """Never log secrets (JWT_SECRET, passwords, tokens, DATABASE_URL)."""
    level = logging.DEBUG if app_env == "development" else logging.INFO
    logging.basicConfig(level=level, format=_FORMAT, force=True)
