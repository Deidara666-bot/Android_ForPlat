from fastapi import FastAPI

from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(get_settings().app_env)
    app = FastAPI(
        title="Android ForPlat",
        description="Android forensic investigation platform with rule-based evidence correlation.",
    )
    app.include_router(health.router, prefix="/api")
    return app


app = create_app()
