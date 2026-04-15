from fastapi_users import schemas
import uuid

class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str | None = None
    client_id: uuid.UUID

class UserCreate(schemas.BaseUserCreate):
    name: str | None = None
    client_id: uuid.UUID

class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None
    client_id: uuid.UUID