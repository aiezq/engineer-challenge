import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.application.ports import OutboxMessage, OutboxRepository, UserRepository
from src.application.queries.ports import UserReadModel, UserReadRepository
from .models import OutboxMessageModel, UserModel


OUTBOX_STATUS_PENDING = "pending"
OUTBOX_STATUS_PROCESSING = "processing"
OUTBOX_STATUS_DELIVERED = "delivered"


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def to_domain(model: UserModel) -> User:
        reset_token_hash = model.reset_token_hash
        if not reset_token_hash and model.legacy_reset_token:
            reset_token_hash = _hash_reset_token(model.legacy_reset_token)
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=HashedPassword(model.password_hash),
            is_active=model.is_active,
            created_at=model.created_at,
            reset_token_hash=reset_token_hash,
            reset_token_expires_at=model.reset_token_expires_at
        )

    async def _get_model_by_id(self, user_id: str) -> Optional[UserModel]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> Optional[User]:
        model = await self._get_model_by_id(user_id)
        return self.to_domain(model) if model else None

    async def get_by_email(self, email: Email) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email.value))
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def get_by_reset_token(self, token: str) -> Optional[User]:
        hashed_token = _hash_reset_token(token)
        result = await self._session.execute(
            select(UserModel).where(
                or_(
                    UserModel.reset_token_hash == hashed_token,
                    UserModel.legacy_reset_token == token,
                )
            )
        )
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def save(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if not model:
            model = UserModel(id=user.id)
            self._session.add(model)
        
        model.email = user.email.value
        model.password_hash = str(user.password_hash.value)
        model.is_active = user.is_active
        model.created_at = user.created_at
        model.legacy_reset_token = None
        model.reset_token_hash = user.reset_token_hash
        model.reset_token_expires_at = user.reset_token_expires_at

        await self._session.flush()

class SqlAlchemyUserReadRepository(UserReadRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: str) -> Optional[UserReadModel]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if not model:
            return None

        return UserReadModel(
            id=str(model.id),
            email=model.email,
            is_active=model.is_active,
            created_at=model.created_at.isoformat()
        )

    async def is_reset_token_valid(self, token: str) -> bool:
        hashed_token = _hash_reset_token(token)
        result = await self._session.execute(
            select(UserModel).where(
                or_(
                    UserModel.reset_token_hash == hashed_token,
                    UserModel.legacy_reset_token == token,
                )
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        user = SqlAlchemyUserRepository.to_domain(model)
        if not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
            return False
        return True


class SqlAlchemyOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def enqueue(
        self,
        *,
        event_type: str,
        event_version: int,
        payload: dict[str, object],
    ) -> None:
        self._session.add(
            OutboxMessageModel(
                event_type=event_type,
                event_version=event_version,
                payload=payload,
            )
        )
        await self._session.flush()

    async def reserve_pending(self, *, limit: int) -> list[OutboxMessage]:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.status == OUTBOX_STATUS_PENDING,
                OutboxMessageModel.available_at <= now,
            )
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        models = list(result.scalars().all())
        for model in models:
            model.status = OUTBOX_STATUS_PROCESSING
            model.attempt_count += 1

        await self._session.flush()
        return [
            OutboxMessage(
                id=str(model.id),
                event_type=model.event_type,
                event_version=model.event_version,
                payload=model.payload,
                attempt_count=model.attempt_count,
                available_at=model.available_at,
            )
            for model in models
        ]

    async def mark_delivered(self, message_id: str) -> None:
        model = await self._session.get(OutboxMessageModel, uuid.UUID(message_id))
        if not model:
            return
        model.status = OUTBOX_STATUS_DELIVERED
        model.delivered_at = datetime.now(timezone.utc)
        model.last_error = None
        await self._session.flush()

    async def mark_failed(self, message_id: str, error: str, retry_at: datetime) -> None:
        model = await self._session.get(OutboxMessageModel, uuid.UUID(message_id))
        if not model:
            return
        model.status = OUTBOX_STATUS_PENDING
        model.available_at = retry_at
        model.last_error = error[:1000]
        await self._session.flush()
