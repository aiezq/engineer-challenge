from dataclasses import dataclass
from datetime import datetime


PASSWORD_RESET_REQUESTED_EVENT_TYPE = "password_reset_requested"
PASSWORD_RESET_REQUESTED_EVENT_VERSION = 1


@dataclass(frozen=True)
class PasswordResetRequestedEvent:
    user_id: str
    email: str
    reset_url: str
    expires_at: datetime

    @property
    def event_type(self) -> str:
        return PASSWORD_RESET_REQUESTED_EVENT_TYPE

    @property
    def event_version(self) -> int:
        return PASSWORD_RESET_REQUESTED_EVENT_VERSION

    def to_payload(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "reset_url": self.reset_url,
            "expires_at": self.expires_at.isoformat(),
        }
