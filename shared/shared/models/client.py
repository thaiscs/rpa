from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.models.certificate import Certificate

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared.db import Base


class PersonTypeEnum(str, enum.Enum):
    individual = "individual"
    company = "company"
    mei = "mei"
    other = "other"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name: Mapped[str] = mapped_column(String)
    tax_id: Mapped[str] = mapped_column(String, unique=True)

    person_type: Mapped[PersonTypeEnum] = mapped_column(
        PG_ENUM(PersonTypeEnum, name="person_type_enum", create_type=False),
        default=PersonTypeEnum.company,
    )

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    certificates: Mapped[list[Certificate]] = relationship("Certificate", back_populates="client", cascade="all, delete-orphan")
