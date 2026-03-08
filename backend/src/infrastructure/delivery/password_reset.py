import asyncio
import smtplib
from email.message import EmailMessage

from src.application.ports import PasswordResetDelivery
from src.config import APP_ENV_PRODUCTION, Settings
from src.infrastructure.observability.logger import log


class LoggingResetDeliveryAdapter(PasswordResetDelivery):
    async def deliver_password_reset(self, payload: dict[str, object]) -> None:
        log.info(
            "password_reset_delivery_logged",
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            reset_url=payload.get("reset_url"),
            event_version=payload.get("event_version"),
        )


class SmtpResetDeliveryAdapter(PasswordResetDelivery):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        use_tls: bool,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._use_tls = use_tls

    async def deliver_password_reset(self, payload: dict[str, object]) -> None:
        await asyncio.to_thread(self._send_sync, payload)

    def _send_sync(self, payload: dict[str, object]) -> None:
        recipient = str(payload["email"])
        reset_url = str(payload["reset_url"])
        expires_at = str(payload["expires_at"])

        message = EmailMessage()
        message["Subject"] = "Orbitto password reset"
        message["From"] = self._from_email
        message["To"] = recipient
        message.set_content(
            "Password reset was requested for your account.\n\n"
            f"Reset link: {reset_url}\n"
            f"Expires at: {expires_at}\n"
        )

        with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
            if self._use_tls:
                smtp.starttls()
            smtp.login(self._username, self._password)
            smtp.send_message(message)


def build_password_reset_delivery(settings: Settings) -> PasswordResetDelivery:
    if settings.app_env != APP_ENV_PRODUCTION:
        return LoggingResetDeliveryAdapter()

    if not all(
        [
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
            settings.smtp_from_email,
        ]
    ):
        raise ValueError("SMTP configuration is required when APP_ENV=production")

    return SmtpResetDeliveryAdapter(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        from_email=settings.smtp_from_email,
        use_tls=settings.smtp_use_tls,
    )
