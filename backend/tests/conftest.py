import os
from collections.abc import Iterator
from pathlib import Path

# Must run before `app` is imported: settings are read at import time by app.main.
os.environ["APP_ENV"] = "test"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://forensic_app:local-dev-only@127.0.0.1:5432/android_forensic",
)
os.environ["JWT_SECRET"] = "test-only-secret-that-is-at-least-32-bytes-long"

import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402

_BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def db_url() -> str:
    """URL of the test database: the dev database name plus `_test` (REF §ENV)."""
    url = make_url(get_settings().database_url)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def alembic_config(db_url: str) -> Config:
    config = Config(str(_BACKEND_DIR / "alembic.ini"))
    config.attributes["url"] = db_url
    return config


@pytest.fixture(scope="session")
def migrated_db(db_url: str, alembic_config: Config) -> str:
    from alembic import command

    command.upgrade(alembic_config, "head")
    return db_url


@pytest.fixture
def session(migrated_db: str) -> Iterator[Session]:
    engine = create_engine(migrated_db)
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db_session:
            yield db_session
        transaction.rollback()
    engine.dispose()
