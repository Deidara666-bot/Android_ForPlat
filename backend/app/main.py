from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(get_settings().app_env)
    return FastAPI(title="Android ForPlat")


app = create_app()
