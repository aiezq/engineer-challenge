import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

import alembic.command as command
from alembic.config import Config


def make_alembic_config(database_url: str) -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


class MigrationTests(unittest.TestCase):
    def test_upgrade_head_succeeds_on_empty_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty.sqlite"
            config = make_alembic_config(f"sqlite+aiosqlite:///{db_path}")

            command.upgrade(config, "head")

            with sqlite3.connect(db_path) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }

        self.assertIn("users", tables)
        self.assertIn("outbox_messages", tables)

    def test_legacy_reset_token_is_backfilled_into_reset_token_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "legacy.sqlite"
            config = make_alembic_config(f"sqlite+aiosqlite:///{db_path}")

            command.upgrade(config, "0001_initial_auth_schema")
            with sqlite3.connect(db_path) as connection:
                connection.execute(
                    """
                    INSERT INTO users (
                        id, email, password_hash, is_active, created_at, reset_token, reset_token_expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "11111111-1111-1111-1111-111111111111",
                        "user@example.com",
                        "hashed-password",
                        1,
                        "2026-03-08T00:00:00+00:00",
                        "legacy-token",
                        "2026-03-08T01:00:00+00:00",
                    ),
                )
                connection.commit()

            command.upgrade(config, "head")
            with sqlite3.connect(db_path) as connection:
                token_hash = connection.execute(
                    "SELECT reset_token_hash FROM users WHERE email = ?",
                    ("user@example.com",),
                ).fetchone()[0]

            self.assertEqual(
                token_hash,
                hashlib.sha256("legacy-token".encode("utf-8")).hexdigest(),
            )

    def test_newest_revision_has_downgrade_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "downgrade.sqlite"
            config = make_alembic_config(f"sqlite+aiosqlite:///{db_path}")

            command.upgrade(config, "head")
            command.downgrade(config, "0001_initial_auth_schema")

            with sqlite3.connect(db_path) as connection:
                columns = {
                    row[1]
                    for row in connection.execute("PRAGMA table_info(users)").fetchall()
                }
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }

        self.assertIn("users", tables)
        self.assertNotIn("outbox_messages", tables)
        self.assertNotIn("reset_token_hash", columns)
