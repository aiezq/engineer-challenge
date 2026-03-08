import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, Request
from redis.exceptions import RedisError
from starlette.types import Scope

from src.config import Settings
from src.infrastructure.auth import rate_limiter


def make_request() -> Request:
    scope: Scope = {
        "type": "http",
        "method": "POST",
        "path": "/graphql",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "query_string": b"",
        "scheme": "http",
        "server": ("testserver", 80),
    }
    return Request(scope)


def make_settings(*, rate_limit_fail_open: bool) -> Settings:
    return Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379",
        app_base_url="http://localhost:3000",
        jwt_secret_key="test-secret",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
        rate_limit_fail_open=rate_limit_fail_open,
        cors_origins=("http://localhost:3000",),
    )


class RateLimiterTests(unittest.IsolatedAsyncioTestCase):
    async def test_allows_request_when_redis_is_down_and_fail_open_enabled(self) -> None:
        redis_client = SimpleNamespace(
            incr=AsyncMock(side_effect=RedisError("redis down")),
            expire=AsyncMock(),
        )
        with patch.object(rate_limiter, "redis_client", redis_client), patch.object(
            rate_limiter,
            "get_settings",
            return_value=make_settings(rate_limit_fail_open=True),
        ):
            await rate_limiter.rate_limit(make_request(), key_suffix="register")

    async def test_raises_service_unavailable_when_redis_is_down_and_fail_open_disabled(self) -> None:
        redis_client = SimpleNamespace(
            incr=AsyncMock(side_effect=RedisError("redis down")),
            expire=AsyncMock(),
        )
        with patch.object(rate_limiter, "redis_client", redis_client), patch.object(
            rate_limiter,
            "get_settings",
            return_value=make_settings(rate_limit_fail_open=False),
        ):
            with self.assertRaises(HTTPException) as error:
                await rate_limiter.rate_limit(make_request(), key_suffix="register")

        self.assertEqual(error.exception.status_code, 503)
