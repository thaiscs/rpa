from nicegui import app, ui
import time
import httpx

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
    async def fetch_user(token: str):
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    USER_URL,
                    headers={"Authorization": f"Bearer {token}"},
                )
                if r.status_code == 200:
                    app.storage.user["user"] = r.json()
            except Exception as e:
                print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def login(token: str):
        user = app.storage.user
        user["token"] = token
        user["expires_at"] = time.time() + SESSION_LIFETIME_SECONDS

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
                msg = "Session expired, please log in again" if expired else "Login required"
                ui.notify(msg, color="negative")
                ui.navigate.to("/login")
                return

            user = Auth.user()

            if superuser and not (user and user.get("is_superuser")):
                ui.notify("Admins only", color="negative")
                return

            result = func()
            if hasattr(result, "__await__"):
                await result

        return wrapper

    return decorator
