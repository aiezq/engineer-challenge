import strawberry
from typing import Optional
from .types import (
    UserType, AuthResultType, RegisterUserInput, 
    AuthenticateInput, RequestResetInput, ResetPasswordInput
)
from src.application.queries.get_user import GetUserByIdQuery, GetUserByIdHandler
from src.application.commands.register import RegisterUserCommand, RegisterUserHandler
from src.application.commands.authenticate import AuthenticateCommand, AuthenticateHandler
from src.application.commands.password_reset import (
    RequestPasswordResetCommand, RequestPasswordResetHandler,
    ResetPasswordCommand, ResetPasswordHandler
)
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.repository import SqlAlchemyUserReadRepository, SqlAlchemyUserRepository
from src.infrastructure.auth.password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.token_service import JwtTokenService

# Quick dependency injection helpers for simplicity
def get_user_repo(session):
    return SqlAlchemyUserRepository(session)


def get_user_read_repo(session):
    return SqlAlchemyUserReadRepository(session)

hasher = BcryptPasswordHasher()
token_service = JwtTokenService(secret_key="SECRET_DONT_USE_IN_PROD")

@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, user_id: str) -> Optional[UserType]:
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

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, input: RegisterUserInput) -> UserType:
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
    async def authenticate(self, input: AuthenticateInput) -> AuthResultType:
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = AuthenticateHandler(repo, hasher, token_service)
            result = await handler.handle(AuthenticateCommand(email=input.email, password=input.password))
            return AuthResultType(access_token=result.access_token, user_id=result.user_id)

    @strawberry.mutation
    async def request_password_reset(self, input: RequestResetInput) -> bool:
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = RequestPasswordResetHandler(repo, token_service)
            await handler.handle(RequestPasswordResetCommand(email=input.email))
            await session.commit()
            return True

    @strawberry.mutation
    async def reset_password(self, input: ResetPasswordInput) -> bool:
        async with AsyncSessionLocal() as session:
            repo = get_user_repo(session)
            handler = ResetPasswordHandler(repo, hasher)
            await handler.handle(ResetPasswordCommand(token=input.token, new_password=input.new_password))
            await session.commit()
            return True

schema = strawberry.Schema(query=Query, mutation=Mutation)
