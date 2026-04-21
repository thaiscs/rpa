from fastapi_users import schemas
from uuid import UUID
from typing import Optional

class UserRead(schemas.BaseUser[UUID]):
    name: str | None = None
    client_id: Optional[UUID] = None

class UserCreate(schemas.BaseUserCreate):
    name: str | None = None
    client_id: Optional[UUID] = None

class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None
    client_id: Optional[UUID] = None