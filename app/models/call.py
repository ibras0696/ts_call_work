from __future__ import annotations
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, String
from ..core.db import Base


class CallStatus(StrEnum):
    created = "created"
    processing = "processing"
    ready = "ready"


class Call(Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    caller: Mapped[str] = mapped_column(String(32), nullable=False)  # E.164
    receiver: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[CallStatus] = mapped_column(Enum(CallStatus), default=CallStatus.created, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # one-to-one Recording
    recording: Mapped[Optional["Recording"]] = relationship(
        back_populates="call", uselist=False, cascade="all, delete-orphan"
    )
