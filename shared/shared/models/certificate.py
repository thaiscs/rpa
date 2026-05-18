from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shared.models.client import Client

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared.db import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)

    encrypted_pfx: Mapped[dict[str, Any]] = mapped_column(JSONB)
    encrypted_pfx_password: Mapped[dict[str, Any]] = mapped_column(JSONB)
    encrypted_cert: Mapped[dict[str, Any]] = mapped_column(JSONB)
    encrypted_key: Mapped[dict[str, Any]] = mapped_column(JSONB)

    issuer: Mapped[str | None] = mapped_column(String)
    valid_from: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    valid_to: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    expired: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    client: Mapped[Client] = relationship("Client", back_populates="certificates")
