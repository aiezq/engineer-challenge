import os
import secrets
from dataclasses import dataclass
from functools import lru_cache


def _split_csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if not value:
        return default

    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://orbitto_user:orbitto_password@localhost:5432/orbitto_db",
        ),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        cors_origins=_split_csv(
            os.getenv("CORS_ORIGINS"),
            ("http://localhost:3000", "http://127.0.0.1:3000"),
        ),
    )
