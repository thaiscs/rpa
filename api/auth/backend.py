from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    BearerTransport,
)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

from api.auth.config import SECRET

SESSION_LIFETIME_SECONDS = 8 * 60 * 60


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=SESSION_LIFETIME_SECONDS)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)