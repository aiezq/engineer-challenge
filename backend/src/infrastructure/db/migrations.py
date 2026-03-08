from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import get_settings
from src.infrastructure.observability.logger import log, setup_logging


INITIAL_REVISION = "0001_initial_auth_schema"
LATEST_REVISION = "head"


@dataclass(frozen=True)
class DatabaseSchemaState:
    has_alembic_version: bool
    has_users_table: bool
    has_reset_token_hash: bool
    has_outbox_messages: bool


def _make_alembic_config(database_url: str) -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _decide_bootstrap_strategy(state: DatabaseSchemaState) -> tuple[str, str | None]:
    if state.has_alembic_version:
        return ("upgrade", LATEST_REVISION)

    if not state.has_users_table:
        return ("upgrade", LATEST_REVISION)

    if state.has_reset_token_hash and state.has_outbox_messages:
        return ("stamp", LATEST_REVISION)

    if not state.has_reset_token_hash and not state.has_outbox_messages:
        return ("stamp_then_upgrade", INITIAL_REVISION)

    raise RuntimeError(
        "Database schema is in a partially migrated state. "
        "Expected either legacy pre-Alembic schema or fully migrated schema."
    )


def _inspect_schema(connection: object) -> DatabaseSchemaState:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    user_columns = (
        {column["name"] for column in inspector.get_columns("users")}
        if "users" in tables
        else set()
    )

    return DatabaseSchemaState(
        has_alembic_version="alembic_version" in tables,
        has_users_table="users" in tables,
        has_reset_token_hash="reset_token_hash" in user_columns,
        has_outbox_messages="outbox_messages" in tables,
    )


async def detect_database_schema_state(database_url: str) -> DatabaseSchemaState:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            return await connection.run_sync(_inspect_schema)
    finally:
        await engine.dispose()


async def run_migrations() -> None:
    settings = get_settings()
    config = _make_alembic_config(settings.database_url)
    state = await detect_database_schema_state(settings.database_url)
    action, revision = _decide_bootstrap_strategy(state)

    log.info(
        "database_migration_strategy_selected",
        action=action,
        revision=revision,
        has_alembic_version=state.has_alembic_version,
        has_users_table=state.has_users_table,
        has_reset_token_hash=state.has_reset_token_hash,
        has_outbox_messages=state.has_outbox_messages,
    )

    if action == "stamp":
        command.stamp(config, revision or LATEST_REVISION)
        return

    if action == "stamp_then_upgrade":
        command.stamp(config, revision or INITIAL_REVISION)
        command.upgrade(config, LATEST_REVISION)
        return

    command.upgrade(config, revision or LATEST_REVISION)


def main() -> None:
    setup_logging()
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
