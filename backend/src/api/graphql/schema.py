import strawberry
from typing import Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from .types import (
    UserType, AuthResultType, PasswordResetRequestResultType, RegisterUserInput, 
    AuthenticateInput, RequestResetInput, ResetPasswordInput
)
from .context import GraphQLContext, build_context
from src.application.queries.get_user import GetUserByIdQuery, GetUserByIdHandler
from src.application.queries.validate_reset_token import ValidateResetTokenHandler, ValidateResetTokenQuery
from src.application.commands.register import RegisterUserCommand, RegisterUserHandler
from src.application.commands.authenticate import AuthenticateCommand, AuthenticateHandler
from src.application.commands.password_reset import (
    RequestPasswordResetCommand, RequestPasswordResetHandler,
    ResetPasswordCommand, ResetPasswordHandler
)
from src.config import get_settings
from src.domain.exceptions import InvalidCredentialsError
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.repository import (
    SqlAlchemyOutboxRepository,
    SqlAlchemyUserReadRepository,
    SqlAlchemyUserRepository,
)
from src.infrastructure.auth.password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.rate_limiter import rate_limit
from src.infrastructure.auth.token_service import JwtTokenService

# Quick dependency injection helpers for simplicity
def get_user_repo(session: AsyncSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_user_read_repo(session: AsyncSession) -> SqlAlchemyUserReadRepository:
    return SqlAlchemyUserReadRepository(session)


def get_outbox_repo(session: AsyncSession) -> SqlAlchemyOutboxRepository:
    return SqlAlchemyOutboxRepository(session)

settings = get_settings()
hasher = BcryptPasswordHasher()
token_service = JwtTokenService(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes,
)


def _require_current_user_id(info: Info[GraphQLContext, None]) -> str:
    current_user_id = info.context.get("current_user_id")
    if not current_user_id:
        raise InvalidCredentialsError("Authentication required")
    return current_user_id

@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, info: Info[GraphQLContext, None], user_id: str) -> Optional[UserType]:
        current_user_id = _require_current_user_id(info)
        if current_user_id != user_id:
            raise InvalidCredentialsError("Forbidden")

        async with AsyncSessionLocal() as session:
            repo = get_user_read_repo(session)
            handler = GetUserByIdHandler(repo)
            result = await handler.handle(GetUserByIdQuery(user_id=user_id))
            if result:
                return UserType(
                    id=result.id, email=result.email, 
                    is_active=result.is_active, created_at=result.created_at
                )
            return None

    @strawberry.field
    async def me(self, info: Info[GraphQLContext, None]) -> Optional[UserType]:
        current_user_id = _require_current_user_id(info)
        async with AsyncSessionLocal() as session:
            repo = get_user_read_repo(session)
            handler = GetUserByIdHandler(repo)
            result = await handler.handle(GetUserByIdQuery(user_id=current_user_id))
            if result:
                return UserType(
                    id=result.id,
                    email=result.email,
                    is_active=result.is_active,
                    created_at=result.created_at,
                )
            return None

    @strawberry.field
    async def validate_reset_token(self, info: Info[GraphQLContext, None], token: str) -> bool:
        await rate_limit(info.context["request"], limit=10, window=60, key_suffix="validate_reset_token")
        async with AsyncSessionLocal() as session:
            repo = get_user_read_repo(session)
            handler = ValidateResetTokenHandler(repo)
            return await handler.handle(ValidateResetTokenQuery(token=token))

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, info: Info[GraphQLContext, None], input: RegisterUserInput) -> UserType:
        await rate_limit(info.context["request"], limit=5, window=60, key_suffix="register")
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = RegisterUserHandler(repo, hasher)
            user = await handler.handle(RegisterUserCommand(email=input.email, password=input.password))
            await session.commit()
            return UserType(
                id=str(user.id), email=user.email.value, 
                is_active=user.is_active, created_at=user.created_at.isoformat()
            )

    @strawberry.mutation
    async def authenticate(self, info: Info[GraphQLContext, None], input: AuthenticateInput) -> AuthResultType:
        await rate_limit(info.context["request"], limit=5, window=60, key_suffix="authenticate")
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = AuthenticateHandler(repo, hasher, token_service)
            result = await handler.handle(AuthenticateCommand(email=input.email, password=input.password))
            return AuthResultType(access_token=result.access_token, user_id=result.user_id)

    @strawberry.mutation
    async def request_password_reset(
        self,
        info: Info[GraphQLContext, None],
        input: RequestResetInput,
    ) -> PasswordResetRequestResultType:
        await rate_limit(info.context["request"], limit=5, window=60, key_suffix="request_password_reset")
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            outbox_repo = get_outbox_repo(session)
            handler = RequestPasswordResetHandler(
                repo,
                outbox_repo,
                token_service,
                app_base_url=settings.app_base_url,
                preview_enabled=settings.app_env != "production",
            )
            result = await handler.handle(RequestPasswordResetCommand(email=input.email))
            await session.commit()
            return PasswordResetRequestResultType(
                ok=result.ok,
                delivery_mode=result.delivery_mode,
                reset_url_preview=result.reset_url_preview,
            )

    @strawberry.mutation
    async def reset_password(self, info: Info[GraphQLContext, None], input: ResetPasswordInput) -> bool:
        await rate_limit(info.context["request"], limit=5, window=60, key_suffix="reset_password")
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = ResetPasswordHandler(repo, hasher, token_service)
            await handler.handle(ResetPasswordCommand(token=input.token, new_password=input.new_password))
            await session.commit()
            return True


async def get_context(request: Request) -> GraphQLContext:
    return await build_context(request, token_service)

schema = strawberry.Schema(query=Query, mutation=Mutation)
