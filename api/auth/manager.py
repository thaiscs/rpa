import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.config import SECRET
from shared.db import get_db
from shared.models.user import User


class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_manager(
    session: AsyncSession = Depends(get_db)  # noqa: B008
):
    yield UserManager(SQLAlchemyUserDatabase(session, User))
