import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractContextManager, asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.audit_handlers import audit_http_exception, audit_validation_error
from app.api.routes import (
    acquisitions,
    agents,
    analysis,
    auth,
    cases,
    coverage,
    devices,
    events,
    evidence,
    health,
    rules,
)
from app.core.build_info import read_code_commit
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rules.errors import RuleLoadError
from app.research.rules.loader import RULES_DIR, RuleLoader
from app.schemas.rules import RulesHealth
from app.ws import agent_ws, dashboard_ws

logger = logging.getLogger(__name__)


@dataclass
class RulesStartupConfig:
    """How the startup load runs; the defaults are the real ones.

    Tests set `app.state.rules_startup` to switch the load off (`enabled=False`) or to point it at
    the test database and a temporary rules folder. There is no `.env` key for this.
    """

    enabled: bool = True
    session_factory: Callable[[], AbstractContextManager[Session]] = field(
        default=lambda: SessionLocal()
    )
    rules_dir: Path = RULES_DIR
    sources_path: Path | None = None


def load_rules_on_startup(app: FastAPI) -> None:
    """One transaction: knowledge base, then `load_validated()`, then commit (REF section YAML).

    Never raises: on any failure the transaction is rolled back, `app.state.rule_set` stays None and
    `app.state.rules_status` says why. There is no retry before the next restart. The ungated
    `load_validated` is used on purpose: the run-purpose gate belongs to an analysis, not startup.
    """
    config: RulesStartupConfig = getattr(app.state, "rules_startup", None) or RulesStartupConfig()
    app.state.rule_set = None
    app.state.rules_status = None  # None = no load was attempted
    if not config.enabled:
        return
    try:
        with config.session_factory() as db:
            try:
                knowledge_base = (
                    KnowledgeBaseLoader(config.sources_path)
                    if config.sources_path
                    else KnowledgeBaseLoader()
                )
                knowledge_base.load_to_db(db)
                rule_set = RuleLoader(
                    db, rules_dir=config.rules_dir, sources_path=config.sources_path
                ).load_validated()
                db.commit()
            except BaseException:
                db.rollback()
                raise
    except RuleLoadError as error:
        logger.error("rules not loaded at startup: %s", error)
        app.state.rules_status = RulesHealth(
            status="load_failed", code=error.code.value, rule_set_hash=None, kb_hash=None
        )
    except Exception:  # any failure must leave the backend alive; the detail goes to the log only
        logger.exception("rules not loaded at startup")
        app.state.rules_status = RulesHealth(
            status="load_failed", code=None, rule_set_hash=None, kb_hash=None
        )
    else:
        app.state.rule_set = rule_set
        app.state.rules_status = RulesHealth(
            status="ok", code=None, rule_set_hash=rule_set.hash, kb_hash=rule_set.kb_hash
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.code_commit = read_code_commit()  # once per start (REF section ENGINE, "Run")
    load_rules_on_startup(app)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app_env)
    app = FastAPI(
        title="Android ForPlat",
        description="Android forensic investigation platform with rule-based evidence correlation.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_exception_handler(StarletteHTTPException, audit_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, audit_validation_error)  # type: ignore[arg-type]
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(cases.router, prefix="/api")
    app.include_router(events.router, prefix="/api")
    app.include_router(coverage.router, prefix="/api")
    app.include_router(analysis.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(devices.router, prefix="/api")
    app.include_router(acquisitions.router, prefix="/api")
    app.include_router(evidence.router, prefix="/api")
    app.include_router(rules.router, prefix="/api")
    app.include_router(agent_ws.router)
    app.include_router(dashboard_ws.router)
    return app


app = create_app()
