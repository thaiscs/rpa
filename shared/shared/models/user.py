import uuid
from sqlalchemy import Column, String, Boolean, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, Mapped, mapped_column, mapped_column, relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from shared.db import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # FastAPI Users already includes: id, email, hashed_password, is_active, is_superuser, is_verified
    # If you want custom fields, add them below:
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=True)