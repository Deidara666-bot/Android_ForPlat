from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command

_TABLES = {
    "acquisition_operations",
    "acquisition_sessions",
    "agents",
    "case_devices",
    "cases",
    "devices",
    "evidence",
    "users",
}


def _tables(url: str) -> set[str]:
    engine = create_engine(url)
    try:
        return set(inspect(engine).get_table_names()) - {"alembic_version"}
    finally:
        engine.dispose()


def test_upgrade_downgrade_upgrade_roundtrip(alembic_config: Config, db_url: str) -> None:
    command.upgrade(alembic_config, "head")
    assert _tables(db_url) == _TABLES

    command.downgrade(alembic_config, "base")
    assert _tables(db_url) == set()

    command.upgrade(alembic_config, "head")
    assert _tables(db_url) == _TABLES
