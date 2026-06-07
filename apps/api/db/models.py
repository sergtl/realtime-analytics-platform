from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    String,
    UUID as PG_UUID,
    Index,
    UniqueConstraint,
)
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

    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_events_project", ondelete="CASCADE"),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="events")

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "event_id",
            name="uq_events_project_event_id",
        ),
        Index("ix_events_payload_gin", "payload", postgresql_using="gin"),
        Index("ix_events_project_timestamp", "project_id", "timestamp"),
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # orm rel attributes for convenience
    events: Mapped[list["Event"]] = relationship(back_populates="project")
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="project")
    memberships: Mapped[list["ProjectMembership"]] = relationship(
        back_populates="project"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_api_keys_project", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project: Mapped["Project"] = relationship(back_populates="api_keys")

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    prefix: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    key_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        Identity(),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")


class ProjectMembership(Base):
    __tablename__ = "project_memberships"

    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", name="fk_project_memberships_user", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_project_memberships_project", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="memberships")
    project: Mapped["Project"] = relationship(back_populates="memberships")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", name="fk_sessions_user", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True, # this already creates an index. we need that bc every authenticated req will hit the db
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
