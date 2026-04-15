import uuid
from fastapi import Depends
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import User
from shared.db import get_db
from api.auth.config import SECRET

class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_manager(
    session: AsyncSession = Depends(get_db)
):
    yield UserManager(SQLAlchemyUserDatabase(session, User))