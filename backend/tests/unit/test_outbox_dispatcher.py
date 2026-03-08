import unittest
from datetime import datetime, timezone

from src.application.ports import OutboxMessage
from src.config import (
    APP_ENV_PRODUCTION,
    APP_ENV_TEST,
    DEFAULT_DEV_JWT_SECRET_KEY,
    Settings,
)
from src.infrastructure.delivery.password_reset import (
    LoggingResetDeliveryAdapter,
    SmtpResetDeliveryAdapter,
    build_password_reset_delivery,
)
from src.infrastructure.outbox.dispatcher import OutboxDispatcher


class DummySession:
    async def commit(self) -> None:
        return None


class DummySessionContext:
    def __init__(self, session: DummySession):
        self._session = session

    async def __aenter__(self) -> DummySession:
        return self._session

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class FakeOutboxRepo:
    def __init__(self, messages: list[OutboxMessage]) -> None:
        self._messages = messages
        self.delivered_ids: list[str] = []
        self.failed_ids: list[str] = []

    async def enqueue(self, *, event_type: str, event_version: int, payload: dict[str, object]) -> None:
        raise NotImplementedError

    async def reserve_pending(self, *, limit: int) -> list[OutboxMessage]:
        messages = self._messages[:limit]
        self._messages = self._messages[limit:]
        return messages

    async def mark_delivered(self, message_id: str) -> None:
        self.delivered_ids.append(message_id)

    async def mark_failed(self, message_id: str, error: str, retry_at: datetime) -> None:
        _ = error
        _ = retry_at
        self.failed_ids.append(message_id)


class FakeDelivery:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.payloads: list[dict[str, object]] = []

    async def deliver_password_reset(self, payload: dict[str, object]) -> None:
        self.payloads.append(payload)
        if self.should_fail:
            raise RuntimeError("delivery failed")


def make_message() -> OutboxMessage:
    return OutboxMessage(
        id="message-1",
        event_type="password_reset_requested",
        event_version=1,
        payload={
            "user_id": "user-1",
            "email": "user@example.com",
            "reset_url": "http://localhost:3000/reset-password?token=raw-token",
            "expires_at": datetime.now(timezone.utc).isoformat(),
        },
        attempt_count=1,
        available_at=datetime.now(timezone.utc),
    )


def make_settings(app_env: str, **overrides: object) -> Settings:
    defaults: dict[str, object] = {
        "app_env": app_env,
        "database_url": "sqlite+aiosqlite:///:memory:",
        "redis_url": "redis://localhost:6379",
        "app_base_url": "http://localhost:3000",
        "jwt_secret_key": DEFAULT_DEV_JWT_SECRET_KEY,
        "jwt_algorithm": "HS256",
        "access_token_expire_minutes": 30,
        "rate_limit_fail_open": True,
        "smtp_host": None,
        "smtp_port": None,
        "smtp_username": None,
        "smtp_password": None,
        "smtp_from_email": None,
        "smtp_use_tls": True,
        "cors_origins": ("http://localhost:3000",),
    }
    defaults.update(overrides)
    return Settings(**defaults)


class OutboxDispatcherTests(unittest.IsolatedAsyncioTestCase):
    async def test_marks_message_delivered_on_success(self) -> None:
        repo = FakeOutboxRepo([make_message()])
        delivery = FakeDelivery()
        dispatcher = OutboxDispatcher(
            session_factory=lambda: DummySessionContext(DummySession()),
            outbox_repo_factory=lambda session: repo,
            password_reset_delivery=delivery,
        )

        processed = await dispatcher.dispatch_once()

        self.assertEqual(processed, 1)
        self.assertEqual(repo.delivered_ids, ["message-1"])
        self.assertEqual(repo.failed_ids, [])
        self.assertEqual(len(delivery.payloads), 1)

    async def test_marks_message_failed_on_delivery_error(self) -> None:
        repo = FakeOutboxRepo([make_message()])
        delivery = FakeDelivery(should_fail=True)
        dispatcher = OutboxDispatcher(
            session_factory=lambda: DummySessionContext(DummySession()),
            outbox_repo_factory=lambda session: repo,
            password_reset_delivery=delivery,
        )

        processed = await dispatcher.dispatch_once()

        self.assertEqual(processed, 1)
        self.assertEqual(repo.delivered_ids, [])
        self.assertEqual(repo.failed_ids, ["message-1"])


class DeliverySelectionTests(unittest.TestCase):
    def test_dev_environment_uses_logging_delivery(self) -> None:
        adapter = build_password_reset_delivery(make_settings(APP_ENV_TEST))
        self.assertIsInstance(adapter, LoggingResetDeliveryAdapter)

    def test_production_uses_smtp_delivery_when_configured(self) -> None:
        adapter = build_password_reset_delivery(
            make_settings(
                APP_ENV_PRODUCTION,
                jwt_secret_key="x" * 32,
                smtp_host="smtp.example.com",
                smtp_port=587,
                smtp_username="mailer",
                smtp_password="secret",
                smtp_from_email="noreply@example.com",
            )
        )
        self.assertIsInstance(adapter, SmtpResetDeliveryAdapter)

    def test_production_requires_smtp_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "SMTP configuration is required"):
            build_password_reset_delivery(
                make_settings(APP_ENV_PRODUCTION, jwt_secret_key="x" * 32)
            )
