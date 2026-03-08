from dataclasses import dataclass
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import InvalidResetTokenError
from src.application.ports import UserRepository, PasswordHasher, TokenService

@dataclass
class RequestPasswordResetCommand:
    email: str

class RequestPasswordResetHandler:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self._user_repo = user_repo
        self._token_service = token_service

    async def handle(self, command: RequestPasswordResetCommand) -> None:
        try:
            email = Email(command.email)
        except Exception:
            # Avoid info leakage
            return

        user = await self._user_repo.get_by_email(email)
        if not user:
            # Avoid info leakage
            return

        reset_token = self._token_service.generate_reset_token()
        user.request_password_reset(reset_token)
        await self._user_repo.save(user)
        
        # Here we would normally emit a Domain Event like "PasswordResetRequested" 
        # which an event handler would listen to and send an email. 


@dataclass
class ResetPasswordCommand:
    token: str
    new_password: str

class ResetPasswordHandler:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    async def handle(self, command: ResetPasswordCommand) -> None:
        user = await self._user_repo.get_by_reset_token(command.token)
        if not user:
            raise InvalidResetTokenError("Invalid token")
            
        raw_password = RawPassword(command.new_password)
        hashed_password = HashedPassword(self._password_hasher.hash_password(raw_password.value))
        
        user.reset_password(hashed_password, command.token)
        await self._user_repo.save(user)
