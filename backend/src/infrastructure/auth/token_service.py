import jwt
import secrets
from datetime import datetime, timedelta, timezone
from src.domain.user import User
from src.application.ports import TokenService

class JwtTokenService(TokenService):
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expires_in = access_token_expire_minutes

    def generate_token(self, user: User) -> str:
        to_encode = {
            "sub": str(user.id),
            "email": user.email.value
        }
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expires_in)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)
