import os
from dataclasses import dataclass
from functools import lru_cache

APP_ENV_DEVELOPMENT = "development"
APP_ENV_TEST = "test"
APP_ENV_PRODUCTION = "production"
DEFAULT_DEV_JWT_SECRET_KEY = "orbitto-dev-jwt-secret-key-change-me"


def _split_csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if not value:
        return default

    return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("RATE_LIMIT_FAIL_OPEN must be a boolean value")


def _resolve_jwt_secret_key(app_env: str) -> str:
    configured_secret = os.getenv("JWT_SECRET_KEY")
    if configured_secret:
        return configured_secret

    if app_env == APP_ENV_PRODUCTION:
        raise ValueError("JWT_SECRET_KEY is required when APP_ENV=production")

    return DEFAULT_DEV_JWT_SECRET_KEY


def _resolve_rate_limit_fail_open(app_env: str) -> bool:
    override = _parse_optional_bool(os.getenv("RATE_LIMIT_FAIL_OPEN"))
    if override is not None:
        return override

    return app_env in {APP_ENV_DEVELOPMENT, APP_ENV_TEST}


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    rate_limit_fail_open: bool
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", APP_ENV_DEVELOPMENT).strip().lower() or APP_ENV_DEVELOPMENT
    if app_env not in {APP_ENV_DEVELOPMENT, APP_ENV_TEST, APP_ENV_PRODUCTION}:
        raise ValueError("APP_ENV must be one of: development, test, production")

    return Settings(
        app_env=app_env,
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://orbitto_user:orbitto_password@localhost:5432/orbitto_db",
        ),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        jwt_secret_key=_resolve_jwt_secret_key(app_env),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        rate_limit_fail_open=_resolve_rate_limit_fail_open(app_env),
        cors_origins=_split_csv(
            os.getenv("CORS_ORIGINS"),
            ("http://localhost:3000", "http://127.0.0.1:3000"),
        ),
    )
