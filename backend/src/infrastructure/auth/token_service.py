import jwt
import secrets
from datetime import datetime, timedelta, timezone
from jwt import InvalidTokenError
from typing import cast
from src.application.ports import TokenPayload, TokenService
from src.domain.user import User
from src.domain.exceptions import InvalidCredentialsError

class JwtTokenService(TokenService):
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expires_in = access_token_expire_minutes

    def generate_token(self, user: User) -> str:
        to_encode: TokenPayload = {
            "sub": str(user.id),
            "email": user.email.value,
        }
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expires_in)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = cast(dict[str, object], jwt.decode(token, self._secret_key, algorithms=[self._algorithm]))
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
