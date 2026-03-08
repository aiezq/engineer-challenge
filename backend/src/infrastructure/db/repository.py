from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.application.ports import UserRepository
from src.application.queries.ports import UserReadModel, UserReadRepository
from .models import UserModel

class SqlAlchemyUserRepository(UserRepository, UserReadRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=HashedPassword(model.password_hash),
            is_active=model.is_active,
            created_at=model.created_at,
            reset_token=model.reset_token,
            reset_token_expires_at=model.reset_token_expires_at
        )

    def _to_read_model(self, model: UserModel) -> UserReadModel:
        return UserReadModel(
            id=str(model.id),
            email=model.email,
            is_active=model.is_active,
            created_at=model.created_at.isoformat() if model.created_at else ""
        )

    async def get_by_id(self, user_id: str):
        # We handle both UserRepository (returns User) and UserReadRepository (returns UserReadModel)
        # However, due to Python's duck typing, we need to distinguish which method was called.
        # It's cleaner to split them, but for this exercise we implement them on the same class.
        pass

    async def get_domain_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_read_by_id(self, user_id: str) -> Optional[UserReadModel]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return self._to_read_model(model) if model else None

    # Implementing UserRepository
    async def get_by_email(self, email: Email) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email.value))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_reset_token(self, token: str) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.reset_token == token))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

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

    # Implementing UserReadRepository
    async def is_reset_token_valid(self, token: str) -> bool:
        user = await self.get_by_reset_token(token)
        if not user:
            return False
        from datetime import datetime, timezone
        if not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
            return False
        return True
