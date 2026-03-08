import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.events import (
    PASSWORD_RESET_REQUESTED_EVENT_TYPE,
    PASSWORD_RESET_REQUESTED_EVENT_VERSION,
)
from src.application.ports import OutboxMessage, OutboxRepository, PasswordResetDelivery
from src.infrastructure.observability.logger import log


OutboxRepositoryFactory = Callable[[AsyncSession], OutboxRepository]


@dataclass
class OutboxDispatcherHandle:
    stop_event: asyncio.Event
    task: asyncio.Task[None]


class OutboxDispatcher:
    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession],
        outbox_repo_factory: OutboxRepositoryFactory,
        password_reset_delivery: PasswordResetDelivery,
        batch_size: int = 10,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self._session_factory = session_factory
        self._outbox_repo_factory = outbox_repo_factory
        self._password_reset_delivery = password_reset_delivery
        self._batch_size = batch_size
        self._poll_interval_seconds = poll_interval_seconds

    async def run(self, stop_event: asyncio.Event) -> None:
        while not stop_event.is_set():
            processed = await self.dispatch_once()
            if processed:
                continue

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self._poll_interval_seconds)
            except asyncio.TimeoutError:
                continue

    async def dispatch_once(self) -> int:
        async with self._session_factory() as session:
            repo = self._outbox_repo_factory(session)
            messages = await repo.reserve_pending(limit=self._batch_size)
            await session.commit()

        for message in messages:
            await self._deliver_message(message)

        return len(messages)

    async def _deliver_message(self, message: OutboxMessage) -> None:
        try:
            await self._dispatch_payload(message)
        except Exception as exc:
            retry_at = datetime.now(timezone.utc) + timedelta(
                seconds=min(60, max(1, 2 ** min(message.attempt_count, 5)))
            )
            async with self._session_factory() as session:
                repo = self._outbox_repo_factory(session)
                await repo.mark_failed(message.id, str(exc), retry_at)
                await session.commit()
            log.exception(
                "outbox_delivery_failed",
                message_id=message.id,
                event_type=message.event_type,
                attempt_count=message.attempt_count,
            )
            return

        async with self._session_factory() as session:
            repo = self._outbox_repo_factory(session)
            await repo.mark_delivered(message.id)
            await session.commit()
        log.info(
            "outbox_delivery_succeeded",
            message_id=message.id,
            event_type=message.event_type,
            attempt_count=message.attempt_count,
        )

    async def _dispatch_payload(self, message: OutboxMessage) -> None:
        if (
            message.event_type == PASSWORD_RESET_REQUESTED_EVENT_TYPE
            and message.event_version == PASSWORD_RESET_REQUESTED_EVENT_VERSION
        ):
            await self._password_reset_delivery.deliver_password_reset(
                {
                    **message.payload,
                    "event_version": message.event_version,
                    "event_type": message.event_type,
                }
            )
            return

        raise ValueError(f"Unsupported outbox event: {message.event_type}@{message.event_version}")


async def start_outbox_dispatcher(
    dispatcher: OutboxDispatcher,
) -> OutboxDispatcherHandle:
    stop_event = asyncio.Event()
    task = asyncio.create_task(dispatcher.run(stop_event))
    return OutboxDispatcherHandle(stop_event=stop_event, task=task)


async def stop_outbox_dispatcher(handle: OutboxDispatcherHandle | None) -> None:
    if not handle:
        return
    handle.stop_event.set()
    await handle.task
