from fastapi import FastAPI

from api.routes import router as public_router
from api.admin.routes import router as admin_router

from api.auth.users import fastapi_users
from api.auth.backend import auth_backend
from api.auth.schemas import UserRead, UserCreate, UserUpdate

app = FastAPI(title="RPA Backend", version="1.0.0")

# -----------------------------
# AUTH ROUTES
# -----------------------------
# LOGIN
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# SIGNUP
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# FORGOT PASSWORD
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# USERS
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)

# VERIFY EMAIL
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# -----------------------------
# BUSINESS ROUTES
# -----------------------------
app.include_router(public_router, tags=["public"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])