# --- User INIT ---
from fastapi_users import FastAPIUsers
import uuid

from api.auth.manager import get_user_manager
from api.auth.backend import auth_backend
from shared.models.user import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)