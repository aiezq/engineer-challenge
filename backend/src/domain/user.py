import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from .value_objects import Email, HashedPassword
from .exceptions import InvalidResetTokenError


@dataclass
class User:
    id: uuid.UUID
    email: Email
    password_hash: HashedPassword
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reset_token: Optional[str] = None
    reset_token_expires_at: Optional[datetime] = None

    @classmethod
    def create(cls, email: Email, password_hash: HashedPassword) -> "User":
        return cls(
            id=uuid.uuid4(),
            email=email,
            password_hash=password_hash
        )

    def request_password_reset(self, reset_token: str, expires_in_minutes: int = 15):
        """Generates a token for password reset"""
        from datetime import timedelta
        self.reset_token = reset_token
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

    def reset_password(self, new_password_hash: HashedPassword, token: str):
        """Resets the password if the token is valid"""
        if not self.reset_token or self.reset_token != token:
            raise InvalidResetTokenError("Invalid token")
        
        if not self.reset_token_expires_at or self.reset_token_expires_at < datetime.now(timezone.utc):
            raise InvalidResetTokenError("Token has expired")
            
        self.password_hash = new_password_hash
        
        # Invalidate token
        self.reset_token = None
        self.reset_token_expires_at = None
