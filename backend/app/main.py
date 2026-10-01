from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, auth, cases, devices, health
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.ws import agent_ws


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app_env)
    app = FastAPI(
        title="Android ForPlat",
        description="Android forensic investigation platform with rule-based evidence correlation.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(cases.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(devices.router, prefix="/api")
    app.include_router(agent_ws.router)
    return app


app = create_app()
