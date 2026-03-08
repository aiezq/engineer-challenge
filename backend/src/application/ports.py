from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, TypedDict
from src.domain.user import User
from src.domain.value_objects import Email


class TokenPayload(TypedDict, total=False):
    sub: str
    email: str
    exp: object


@dataclass(frozen=True)
class OutboxMessage:
    id: str
    event_type: str
    event_version: int
    payload: dict[str, object]
    attempt_count: int
    available_at: datetime


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_reset_token(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass


class OutboxRepository(ABC):
    @abstractmethod
    async def enqueue(
        self,
        *,
        event_type: str,
        event_version: int,
        payload: dict[str, object],
    ) -> None:
        pass

    @abstractmethod
    async def reserve_pending(self, *, limit: int) -> list[OutboxMessage]:
        pass

    @abstractmethod
    async def mark_delivered(self, message_id: str) -> None:
        pass

    @abstractmethod
    async def mark_failed(self, message_id: str, error: str, retry_at: datetime) -> None:
        pass


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass


class TokenService(ABC):
    @abstractmethod
    def generate_token(self, user: User) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        pass

    @abstractmethod
    def generate_reset_token(self) -> str:
        pass

    @abstractmethod
    def hash_reset_token(self, token: str) -> str:
        pass


class PasswordResetDelivery(ABC):
    @abstractmethod
    async def deliver_password_reset(self, payload: dict[str, object]) -> None:
        pass
