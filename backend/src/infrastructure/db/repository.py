from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.application.ports import UserRepository
from src.application.queries.ports import UserReadModel, UserReadRepository
from .models import UserModel

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=HashedPassword(model.password_hash),
            is_active=model.is_active,
            created_at=model.created_at,
            reset_token=model.reset_token,
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
        result = await self._session.execute(select(UserModel).where(UserModel.reset_token == token))
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
        model.reset_token = user.reset_token
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
        result = await self._session.execute(select(UserModel).where(UserModel.reset_token == token))
        model = result.scalar_one_or_none()
        if not model:
            return False

        user = SqlAlchemyUserRepository.to_domain(model)
        from datetime import datetime, timezone
        if not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
            return False
        return True
