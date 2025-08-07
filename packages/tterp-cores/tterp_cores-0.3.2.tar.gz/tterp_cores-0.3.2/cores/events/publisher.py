# cores/events/publisher.py
from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..outbox.models import OutboxEvent
from ..outbox.repository import OutboxRepository
from .interfaces import IEventPublisher
from .schemas.base_event import Event


class OutboxEventPublisher(IEventPublisher):
    """
    Triển khai IEventPublisher để ghi event vào bảng Outbox.
    Tự quản lý session riêng để đảm bảo event được commit sau khi transaction nghiệp vụ thành công.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @asynccontextmanager
    async def session_scope(self):
        """Cung cấp một scope session cho publisher."""
        self._session = self._session_factory()
        try:
            yield self._session
        except Exception:
            await self._session.rollback()
            raise
        finally:
            await self._session.close()
            self._session = None

    async def publish(self, event: Event):
        """Ghi một event vào bảng outbox."""
        if self._session is None:
            raise RuntimeError(
                "Publisher session is not active. Use 'async with publisher.session_scope()'."
            )

        outbox_repo = OutboxRepository(self._session)
        payload_dict = event.model_dump(mode="json").get("payload", {})

        outbox_event = OutboxEvent(
            aggregate_id=str(payload_dict.get("item_id") or event.event_id),
            topic=event.event_name,
            payload=payload_dict,
        )
        await outbox_repo.add_event(outbox_event)

    async def publish_many(self, events: list[Event]):
        """Ghi nhiều event vào bảng outbox."""
        for event in events:
            await self.publish(event)
