import unittest
from dataclasses import dataclass

from src.application.commands.password_reset import (
    RequestPasswordResetCommand,
    RequestPasswordResetHandler,
)
from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword


class StubUserRepo:
    def __init__(self, user: User | None) -> None:
        self.user = user
        self.saved_user: User | None = None

    async def get_by_id(self, user_id: str) -> User | None:
        _ = user_id
        return None

    async def get_by_email(self, email: Email) -> User | None:
        if self.user and self.user.email.value == email.value:
            return self.user
        return None

    async def get_by_reset_token(self, token: str) -> User | None:
        _ = token
        return None

    async def save(self, user: User) -> None:
        self.saved_user = user


class StubOutboxRepo:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    async def enqueue(
        self,
        *,
        event_type: str,
        event_version: int,
        payload: dict[str, object],
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "event_version": event_version,
                "payload": payload,
            }
        )


class StubTokenService:
    def generate_token(self, user: User) -> str:
        raise NotImplementedError

    def decode_token(self, token: str) -> dict[str, object]:
        raise NotImplementedError

    def generate_reset_token(self) -> str:
        return "raw-reset-token"

    def hash_reset_token(self, token: str) -> str:
        return f"hashed::{token}"


def make_user() -> User:
    return User.create(
        email=Email("user@example.com"),
        password_hash=HashedPassword("hashed-password"),
    )


class RequestPasswordResetHandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_creates_outbox_event_for_existing_user(self) -> None:
        user = make_user()
        outbox_repo = StubOutboxRepo()
        handler = RequestPasswordResetHandler(
            StubUserRepo(user),
            outbox_repo,
            StubTokenService(),
            app_base_url="http://localhost:3000",
            preview_enabled=True,
        )

        result = await handler.handle(RequestPasswordResetCommand(email="user@example.com"))

        self.assertTrue(result.ok)
        self.assertEqual(result.delivery_mode, "demo-preview")
        self.assertEqual(user.reset_token_hash, "hashed::raw-reset-token")
        self.assertEqual(len(outbox_repo.events), 1)
        self.assertEqual(outbox_repo.events[0]["event_type"], "password_reset_requested")
        payload = outbox_repo.events[0]["payload"]
        self.assertEqual(payload["email"], "user@example.com")
        self.assertIn("raw-reset-token", str(payload["reset_url"]))

    async def test_does_not_leak_account_existence_for_missing_user(self) -> None:
        outbox_repo = StubOutboxRepo()
        handler = RequestPasswordResetHandler(
            StubUserRepo(None),
            outbox_repo,
            StubTokenService(),
            app_base_url="http://localhost:3000",
            preview_enabled=False,
        )

        result = await handler.handle(RequestPasswordResetCommand(email="missing@example.com"))

        self.assertTrue(result.ok)
        self.assertEqual(result.delivery_mode, "email")
        self.assertIsNone(result.reset_url_preview)
        self.assertEqual(outbox_repo.events, [])
