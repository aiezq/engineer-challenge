from fastapi import Request
from src.api.graphql.context import _extract_bearer_token, build_context
from src.domain.exceptions import InvalidCredentialsError


class StubTokenService:
    def __init__(self, payload=None, error: Exception | None = None):
        self._payload = payload or {}
        self._error = error

    def decode_token(self, token: str) -> dict:
        if self._error:
            raise self._error
        return self._payload


def make_request(headers: dict[str, str] | None = None) -> Request:
    raw_headers = [
        (key.lower().encode("utf-8"), value.encode("utf-8"))
        for key, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/graphql",
        "headers": raw_headers,
        "client": ("127.0.0.1", 12345),
        "query_string": b"",
    }
    return Request(scope)


def test_extract_bearer_token_returns_none_for_non_bearer_header():
    request = make_request({"Authorization": "Basic abc"})

    assert _extract_bearer_token(request) is None


async def test_build_context_reads_user_id_from_valid_token():
    request = make_request({"Authorization": "Bearer valid-token"})
    token_service = StubTokenService(payload={"sub": "user-123"})

    context = await build_context(request, token_service)

    assert context.current_user_id == "user-123"


async def test_build_context_ignores_invalid_token():
    request = make_request({"Authorization": "Bearer invalid-token"})
    token_service = StubTokenService(error=InvalidCredentialsError("Invalid access token"))

    context = await build_context(request, token_service)

    assert context.current_user_id is None
