from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, Identity, String, UUID as PG_UUID, Index
from sqlalchemy.dialects.postgresql import JSONB

from db.database import Base

class Event(Base):
    __tablename__ = "events"

    # db primary key
    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    # idempotency key (logical event id; producer generated)
    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
    )

    # redis stream delivery id
    redis_message_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    event_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    correlation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    schema_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="1.0.0",
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_events_payload_gin", "payload", postgresql_using="gin"),
    )