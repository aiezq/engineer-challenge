import asyncio
import unittest
from fastapi import Request
from starlette.types import Scope
from src.api.graphql.context import build_context, extract_bearer_token
from src.application.ports import TokenPayload, TokenService
from src.domain.exceptions import InvalidCredentialsError
from src.domain.user import User


class StubTokenService(TokenService):
    def __init__(self, payload: TokenPayload | None = None, error: Exception | None = None):
        self._payload: TokenPayload = payload or {}
        self._error = error

    def generate_token(self, user: User) -> str:
        raise NotImplementedError

    def decode_token(self, token: str) -> TokenPayload:
        if self._error:
            raise self._error
        return self._payload

    def generate_reset_token(self) -> str:
        raise NotImplementedError

    def hash_reset_token(self, token: str) -> str:
        return token


def make_request(headers: dict[str, str] | None = None) -> Request:
    raw_headers = [
        (key.lower().encode("utf-8"), value.encode("utf-8"))
        for key, value in (headers or {}).items()
    ]
    scope: Scope = {
        "type": "http",
        "method": "POST",
        "path": "/graphql",
        "headers": raw_headers,
        "client": ("127.0.0.1", 12345),
        "query_string": b"",
    }
    return Request(scope)


class GraphQLContextTests(unittest.TestCase):
    def test_extract_bearer_token_returns_none_for_non_bearer_header(self) -> None:
        request = make_request({"Authorization": "Basic abc"})

        self.assertIsNone(extract_bearer_token(request))

    def test_build_context_reads_user_id_from_valid_token(self) -> None:
        request = make_request({"Authorization": "Bearer valid-token"})
        token_service = StubTokenService(payload={"sub": "user-123"})

        context = asyncio.run(build_context(request, token_service))

        self.assertEqual(context["current_user_id"], "user-123")

    def test_build_context_ignores_invalid_token(self) -> None:
        request = make_request({"Authorization": "Bearer invalid-token"})
        token_service = StubTokenService(error=InvalidCredentialsError("Invalid access token"))

        context = asyncio.run(build_context(request, token_service))

        self.assertIsNone(context["current_user_id"])
