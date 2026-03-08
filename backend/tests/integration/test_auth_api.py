import unittest
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol, cast
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.api.graphql import schema as graphql_schema
from src.application.queries.ports import UserReadModel
from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.main import app


class ResponseLike(Protocol):
    status_code: int

    def json(self) -> Any:
        ...


class ClientLike(Protocol):
    def get(self, path: str) -> ResponseLike:
        ...

    def post(
        self,
        path: str,
        *,
        json: dict[str, object],
        headers: dict[str, str],
    ) -> ResponseLike:
        ...

    def close(self) -> None:
        ...


class PatchLike(Protocol):
    def start(self) -> object:
        ...

    def stop(self) -> None:
        ...


class InMemoryUserRepo:
    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}

    async def get_by_id(self, user_id: str) -> UserReadModel | None:
        user = self._users_by_id.get(user_id)
        if not user:
            return None
        return UserReadModel(
            id=str(user.id),
            email=user.email.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )

    async def get_by_email(self, email: Email) -> User | None:
        for user in self._users_by_id.values():
            if user.email.value == email.value:
                return user
        return None

    async def get_by_reset_token(self, token: str) -> User | None:
        for user in self._users_by_id.values():
            if user.reset_token_hash == token:
                return user
        return None

    async def save(self, user: User) -> None:
        self._users_by_id[str(user.id)] = user

    async def is_reset_token_valid(self, token: str) -> bool:
        user = await self.get_by_reset_token(token)
        if not user or not user.reset_token_expires_at:
            return False
        return user.reset_token_expires_at > datetime.now(timezone.utc)

    def add_user(self, user: User) -> None:
        self._users_by_id[str(user.id)] = user


class DummySession:
    async def commit(self) -> None:
        return None

    async def flush(self) -> None:
        return None


class DummySessionContext:
    async def __aenter__(self) -> DummySession:
        return DummySession()

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def make_session_context() -> DummySessionContext:
    return DummySessionContext()


def _client_get(client: ClientLike, path: str) -> ResponseLike:
    return client.get(path)


def _client_post(
    client: ClientLike,
    path: str,
    payload: dict[str, object],
    headers: dict[str, str],
) -> ResponseLike:
    return client.post(path, json=payload, headers=headers)


class AuthApiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryUserRepo()
        self.patches: list[PatchLike] = [
            patch("src.main.init_db", new=AsyncMock(return_value=None)),
            patch("src.api.graphql.schema.AsyncSessionLocal", new=make_session_context),
            patch("src.api.graphql.schema.get_user_repo", new=self._get_user_repo),
            patch("src.api.graphql.schema.get_user_read_repo", new=self._get_user_read_repo),
            patch("src.api.graphql.schema.rate_limit", new=AsyncMock(return_value=None)),
        ]
        for active_patch in self.patches:
            active_patch.start()

        self.client: ClientLike = cast(ClientLike, TestClient(app))

    def tearDown(self) -> None:
        self.client.close()
        for active_patch in reversed(self.patches):
            active_patch.stop()

    def _get_user_repo(self, session: object) -> InMemoryUserRepo:
        _ = session
        return self.repo

    def _get_user_read_repo(self, session: object) -> InMemoryUserRepo:
        _ = session
        return self.repo

    def graphql(
        self,
        query: str,
        variables: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ResponseLike:
        return _client_post(
            self.client,
            "/graphql",
            {"query": query, "variables": variables or {}},
            headers or {},
        )

    def create_user(self, email: str, password: str) -> User:
        hashed_password = graphql_schema.hasher.hash_password(password)
        user = User.create(email=Email(email), password_hash=HashedPassword(hashed_password))
        self.repo.add_user(user)
        return user

    def test_health_check_endpoint(self) -> None:
        response = _client_get(self.client, "/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_register_mutation_creates_user(self) -> None:
        response = self.graphql(
            """
            mutation Register($email: String!, $password: String!) {
              register(input: { email: $email, password: $password }) {
                email
              }
            }
            """,
            {"email": "  User@Example.com ", "password": "ValidPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", payload)
        self.assertEqual(payload["data"]["register"]["email"], "user@example.com")

    def test_register_mutation_rejects_weak_password(self) -> None:
        response = self.graphql(
            """
            mutation Register($email: String!, $password: String!) {
              register(input: { email: $email, password: $password }) {
                id
              }
            }
            """,
            {"email": "user@example.com", "password": "weakpass"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", payload)
        self.assertIn("at least 12 characters", payload["errors"][0]["message"])

    def test_authenticate_mutation_returns_access_token_for_valid_credentials(self) -> None:
        self.create_user("user@example.com", "ValidPassword1")

        response = self.graphql(
            """
            mutation Authenticate($email: String!, $password: String!) {
              authenticate(input: { email: $email, password: $password }) {
                accessToken
                userId
              }
            }
            """,
            {"email": "user@example.com", "password": "ValidPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", payload)
        self.assertTrue(payload["data"]["authenticate"]["accessToken"])

    def test_authenticate_mutation_rejects_invalid_credentials(self) -> None:
        self.create_user("user@example.com", "ValidPassword1")

        response = self.graphql(
            """
            mutation Authenticate($email: String!, $password: String!) {
              authenticate(input: { email: $email, password: $password }) {
                accessToken
              }
            }
            """,
            {"email": "user@example.com", "password": "WrongPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", payload)
        self.assertIn("Invalid email or password", payload["errors"][0]["message"])

    def test_me_requires_authentication(self) -> None:
        response = self.graphql(
            """
            query Me {
              me {
                id
              }
            }
            """
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", payload)
        self.assertIn("Authentication required", payload["errors"][0]["message"])

    def test_me_returns_current_user_for_valid_token(self) -> None:
        user = self.create_user("user@example.com", "ValidPassword1")
        token = graphql_schema.token_service.generate_token(user)

        response = self.graphql(
            """
            query Me {
              me {
                id
                email
              }
            }
            """,
            headers={"Authorization": f"Bearer {token}"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["me"]["email"], "user@example.com")

    def test_request_password_reset_does_not_leak_account_existence_and_stores_hash(self) -> None:
        user = self.create_user("user@example.com", "ValidPassword1")
        raw_token = "known-reset-token"

        with patch.object(graphql_schema.token_service, "generate_reset_token", return_value=raw_token):
            existing_response = self.graphql(
                """
                mutation RequestReset($email: String!) {
                  requestPasswordReset(input: { email: $email })
                  {
                    ok
                    deliveryMode
                    resetUrlPreview
                  }
                }
                """,
                {"email": "user@example.com"},
            )
            unknown_response = self.graphql(
                """
                mutation RequestReset($email: String!) {
                  requestPasswordReset(input: { email: $email })
                  {
                    ok
                    deliveryMode
                    resetUrlPreview
                  }
                }
                """,
                {"email": "missing@example.com"},
            )

        self.assertEqual(existing_response.status_code, 200)
        self.assertEqual(unknown_response.status_code, 200)
        self.assertTrue(existing_response.json()["data"]["requestPasswordReset"]["ok"])
        self.assertTrue(unknown_response.json()["data"]["requestPasswordReset"]["ok"])
        self.assertEqual(
            existing_response.json()["data"]["requestPasswordReset"]["deliveryMode"],
            "demo-preview",
        )
        self.assertIn(
            raw_token,
            existing_response.json()["data"]["requestPasswordReset"]["resetUrlPreview"],
        )
        self.assertIsNone(unknown_response.json()["data"]["requestPasswordReset"]["resetUrlPreview"])
        self.assertEqual(user.reset_token_hash, graphql_schema.token_service.hash_reset_token(raw_token))
        self.assertNotEqual(user.reset_token_hash, raw_token)

    def test_validate_reset_token_returns_true_for_valid_hashed_token_and_false_for_invalid(self) -> None:
        user = self.create_user("user@example.com", "ValidPassword1")
        raw_token = "raw-reset-token"
        user.request_password_reset(graphql_schema.token_service.hash_reset_token(raw_token))

        valid_response = self.graphql(
            """
            query ValidateResetToken($token: String!) {
              validateResetToken(token: $token)
            }
            """,
            {"token": raw_token},
        )
        invalid_response = self.graphql(
            """
            query ValidateResetToken($token: String!) {
              validateResetToken(token: $token)
            }
            """,
            {"token": "unknown-token"},
        )

        self.assertTrue(valid_response.json()["data"]["validateResetToken"])
        self.assertFalse(invalid_response.json()["data"]["validateResetToken"])

    def test_reset_password_accepts_raw_token_against_hashed_storage(self) -> None:
        user = self.create_user("user@example.com", "ValidPassword1")
        raw_token = "raw-reset-token"
        user.request_password_reset(graphql_schema.token_service.hash_reset_token(raw_token))

        response = self.graphql(
            """
            mutation ResetPassword($token: String!, $newPassword: String!) {
              resetPassword(input: { token: $token, newPassword: $newPassword })
            }
            """,
            {"token": raw_token, "newPassword": "AnotherPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["data"]["resetPassword"])
        self.assertTrue(
            graphql_schema.hasher.verify_password("AnotherPassword1", user.password_hash.value)
        )
        self.assertIsNone(user.reset_token_hash)

    def test_reset_password_rejects_invalid_token(self) -> None:
        self.create_user("user@example.com", "ValidPassword1")

        response = self.graphql(
            """
            mutation ResetPassword($token: String!, $newPassword: String!) {
              resetPassword(input: { token: $token, newPassword: $newPassword })
            }
            """,
            {"token": "bad-token", "newPassword": "AnotherPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", payload)
        self.assertIn("Invalid token", payload["errors"][0]["message"])

    def test_reset_password_rejects_expired_token(self) -> None:
        user = self.create_user("user@example.com", "ValidPassword1")
        raw_token = "expired-reset-token"
        user.request_password_reset(graphql_schema.token_service.hash_reset_token(raw_token))
        user.reset_token_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

        response = self.graphql(
            """
            mutation ResetPassword($token: String!, $newPassword: String!) {
              resetPassword(input: { token: $token, newPassword: $newPassword })
            }
            """,
            {"token": raw_token, "newPassword": "AnotherPassword1"},
        )

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", payload)
        self.assertIn("expired", payload["errors"][0]["message"])
