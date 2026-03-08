from dataclasses import dataclass
from src.domain.value_objects import Email
from src.domain.exceptions import InvalidCredentialsError
from src.application.ports import UserRepository, PasswordHasher, TokenService
from src.infrastructure.observability.logger import log

@dataclass
class AuthenticateCommand:
    email: str
    password: str

@dataclass
class AuthenticateResult:
    access_token: str
    user_id: str

class AuthenticateHandler:
    def __init__(
        self, 
        user_repo: UserRepository, 
        password_hasher: PasswordHasher,
        token_service: TokenService
    ):
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def handle(self, command: AuthenticateCommand) -> AuthenticateResult:
        try:
            email = Email(command.email)
        except Exception:
            log.info("authentication_failed", reason="invalid_email")
            raise InvalidCredentialsError("Invalid email or password")

        user = await self._user_repo.get_by_email(email)
        if not user:
            log.info("authentication_failed", reason="user_not_found")
            raise InvalidCredentialsError("Invalid email or password")
            
        if not self._password_hasher.verify_password(command.password, user.password_hash.value):
            log.info("authentication_failed", reason="invalid_password", user_id=str(user.id))
            raise InvalidCredentialsError("Invalid email or password")
            
        token = self._token_service.generate_token(user)
        log.info("authentication_succeeded", user_id=str(user.id))
        return AuthenticateResult(access_token=token, user_id=str(user.id))
