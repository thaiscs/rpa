import uuid
from sqlalchemy import Column, String, Boolean, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, Mapped, mapped_column, mapped_column, relationship
from shared.db import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    encrypted_pfx = Column(JSONB, nullable=False)
    encrypted_pfx_password = Column(JSONB, nullable=False)
    encrypted_cert = Column(JSONB, nullable=False)
    encrypted_key = Column(JSONB, nullable=False)

    issuer = Column(String)
    valid_from = Column(TIMESTAMP(timezone=True))
    valid_to = Column(TIMESTAMP(timezone=True))
    expired = Column(Boolean, default=False, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client = relationship("Client", back_populates="certificates")
