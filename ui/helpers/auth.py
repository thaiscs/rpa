import logging
import time

import httpx
from nicegui import app, ui

log = logging.getLogger(__name__)

USER_URL = "http://api:8080/auth/users/me"
SESSION_LIFETIME_SECONDS = 8 * 60 * 60


class Auth:

    @staticmethod
    def token():
        if Auth._is_expired():
            Auth.logout()
            return None
        return app.storage.user.get("token")

    @staticmethod
    def _is_expired() -> bool:
        expires_at = app.storage.user.get("expires_at")
        if not expires_at:
            return False
        return time.time() >= expires_at

    @staticmethod
    async def fetch_user(token: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    USER_URL,
                    headers={"Authorization": f"Bearer {token}"},
                )
                if r.status_code == 200:
                    app.storage.user["user"] = r.json()
                    return r.json()
            except Exception as e:
                log.warning("fetch_user failed: %s", e)
        return None

    @staticmethod
    async def login(token: str) -> dict | None:
        app.storage.user["token"] = token
        app.storage.user["expires_at"] = time.time() + SESSION_LIFETIME_SECONDS
        return await Auth.fetch_user(token)

    @staticmethod
    def logout():
        for key in ("token", "expires_at", "user"):
            app.storage.user.pop(key, None)

    @staticmethod
    def is_logged_in():
        return Auth.token() is not None

    @staticmethod
    def is_superuser():
        user = Auth.user()
        return bool(user and user.get("is_superuser"))

    @staticmethod
    def user():
        return app.storage.user.get("user")


def protected(route: str, superuser: bool = False):
    def decorator(func):

        @ui.page(route)
        async def wrapper():
            had_token = bool(app.storage.user.get("token"))
            expired = had_token and Auth._is_expired()

            if not Auth.is_logged_in():
                msg = "Sessão expirada — entre novamente" if expired else "Login necessário"
                ui.notify(msg, color="negative")
                ui.navigate.to("/login")
                return

            user = Auth.user()
            if user is None:
                user = await Auth.fetch_user(Auth.token())

            if superuser and not (user and user.get("is_superuser")):
                ui.notify("Acesso restrito a administradores", color="negative")
                ui.navigate.to("/dashboard")
                return

            result = func()
            if hasattr(result, "__await__"):
                await result

        return wrapper

    return decorator
