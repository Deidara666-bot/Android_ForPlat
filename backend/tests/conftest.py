import os
from collections.abc import Iterator
from pathlib import Path

# Must run before `app` is imported: settings are read at import time by app.main.
os.environ["APP_ENV"] = "test"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://forensic_app:local-dev-only@localhost:5432/android_forensic",
)
os.environ["JWT_SECRET"] = "test-only-secret-that-is-at-least-32-bytes-long"

import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.models.user import User  # noqa: E402

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


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    """App client whose DB dependency is the rolled-back test session."""
    from app.api.deps import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user(session: Session) -> User:
    examiner = User(email="pemeriksa@lab.local", password_hash=hash_password("correct-horse"))
    session.add(examiner)
    session.flush()
    return examiner


@pytest.fixture
def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
