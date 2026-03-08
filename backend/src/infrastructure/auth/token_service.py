import importlib
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from jwt import InvalidTokenError
from src.application.ports import TokenPayload, TokenService
from src.domain.user import User
from src.domain.exceptions import InvalidCredentialsError

jwt_module: Any = importlib.import_module("jwt")


def _jwt_encode(payload: dict[str, object], key: str, algorithm: str) -> str:
    return cast(str, jwt_module.encode(payload, key, algorithm=algorithm))


def _jwt_decode(token: str, key: str, algorithms: list[str]) -> dict[str, object]:
    return cast(dict[str, object], jwt_module.decode(token, key, algorithms=algorithms))

class JwtTokenService(TokenService):
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expires_in = access_token_expire_minutes

    def generate_token(self, user: User) -> str:
        to_encode: dict[str, object] = {
            "sub": str(user.id),
            "email": user.email.value,
        }
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expires_in)
        to_encode["exp"] = expire

        encoded_jwt = _jwt_encode(to_encode, self._secret_key, self._algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = _jwt_decode(token, self._secret_key, [self._algorithm])
        except InvalidTokenError as exc:
            raise InvalidCredentialsError("Invalid access token") from exc

        subject = payload.get("sub")
        email = payload.get("email")

        return {
            "sub": subject if isinstance(subject, str) else "",
            "email": email if isinstance(email, str) else "",
            "exp": payload.get("exp"),
        }

    def generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_reset_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
