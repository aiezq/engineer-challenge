from dataclasses import dataclass
from src.application.events import PasswordResetRequestedEvent
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import InvalidResetTokenError
from src.application.ports import OutboxRepository, PasswordHasher, TokenService, UserRepository
from src.infrastructure.observability.logger import log


@dataclass
class RequestPasswordResetResult:
    ok: bool
    delivery_mode: str
    reset_url_preview: str | None = None

@dataclass
class RequestPasswordResetCommand:
    email: str

class RequestPasswordResetHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        outbox_repo: OutboxRepository,
        token_service: TokenService,
        app_base_url: str,
        preview_enabled: bool,
    ):
        self._user_repo = user_repo
        self._outbox_repo = outbox_repo
        self._token_service = token_service
        self._app_base_url = app_base_url.rstrip("/")
        self._preview_enabled = preview_enabled

    async def handle(self, command: RequestPasswordResetCommand) -> RequestPasswordResetResult:
        result = RequestPasswordResetResult(
            ok=True,
            delivery_mode="demo-preview" if self._preview_enabled else "email",
        )
        try:
            email = Email(command.email)
        except Exception:
            log.info("password_reset_request_ignored", reason="invalid_email")
            return result

        user = await self._user_repo.get_by_email(email)
        if not user:
            log.info("password_reset_request_ignored", reason="user_not_found")
            return result

        reset_token = self._token_service.generate_reset_token()
        reset_token_hash = self._token_service.hash_reset_token(reset_token)
        reset_url = f"{self._app_base_url}/reset-password?token={reset_token}"
        user.request_password_reset(reset_token_hash)
        await self._user_repo.save(user)

        expires_at = user.reset_token_expires_at
        if expires_at is None:
            raise RuntimeError("Reset token expiration must be set")

        event = PasswordResetRequestedEvent(
            user_id=str(user.id),
            email=user.email.value,
            reset_url=reset_url,
            expires_at=expires_at,
        )
        await self._outbox_repo.enqueue(
            event_type=event.event_type,
            event_version=event.event_version,
            payload=event.to_payload(),
        )

        if self._preview_enabled:
            result.reset_url_preview = reset_url

        log.info(
            "password_reset_requested",
            user_id=str(user.id),
            delivery_mode=result.delivery_mode,
            event_type=event.event_type,
            event_version=event.event_version,
            preview_available=bool(result.reset_url_preview),
        )
        return result


@dataclass
class ResetPasswordCommand:
    token: str
    new_password: str

class ResetPasswordHandler:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher, token_service: TokenService):
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def handle(self, command: ResetPasswordCommand) -> None:
        user = await self._user_repo.get_by_reset_token(command.token)
        if not user:
            raise InvalidResetTokenError("Invalid token")

        token_hash = self._token_service.hash_reset_token(command.token)
            
        raw_password = RawPassword(command.new_password)
        hashed_password = HashedPassword(self._password_hasher.hash_password(raw_password.value))
        
        user.reset_password(hashed_password, token_hash)
        await self._user_repo.save(user)
        log.info("password_reset_completed", user_id=str(user.id))
