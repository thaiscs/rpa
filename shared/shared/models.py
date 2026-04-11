import uuid
import enum
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.db import Base


class PersonTypeEnum(str, enum.Enum):
    individual = "individual"
    company = "company"
    mei = "mei"
    other = "other"


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(Text, nullable=False)
    tax_id = Column(Text, nullable=False, unique=True)

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


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)

    encrypted_pfx = Column(JSON, nullable=False)
    encrypted_pfx_password = Column(JSON, nullable=False)
    encrypted_cert = Column(JSON, nullable=False)
    encrypted_key = Column(JSON, nullable=False)

    issuer = Column(Text)
    valid_from = Column(TIMESTAMP(timezone=True))
    valid_to = Column(TIMESTAMP(timezone=True))
    expired = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="certificates")