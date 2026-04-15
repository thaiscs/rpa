import uuid
import enum
from sqlalchemy import Column, String, Boolean, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, Mapped, mapped_column, mapped_column, relationship
from shared.db import Base

class PersonTypeEnum(str, enum.Enum):
    individual = "individual"
    company = "company"
    mei = "mei"
    other = "other"


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(String, nullable=False)
    tax_id = Column(String, nullable=False, unique=True)

    person_type = Column(
        PG_ENUM(
            PersonTypeEnum,
            name="person_type_enum",
            create_type=False
        ),
        nullable=False,
        default=PersonTypeEnum.company
    )

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    certificates = relationship("Certificate", back_populates="client", cascade="all, delete-orphan")
