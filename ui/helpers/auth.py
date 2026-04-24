from nicegui import app, ui
import time
import httpx

USER_URL = "http://api:8080/auth/users/me"

class Auth:

    @staticmethod
    def token():
        return app.storage.user.get("token")

    @staticmethod
    async def fetch_user(token: str):
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    USER_URL,
                    headers={"Authorization": f"Bearer {token}"}
                )
                if r.status_code == 200:
                    user = app.storage.user
                    user["user"] = r.json()

            except Exception as e:
                print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def login(token: str):
        user = app.storage.user
        user["token"] = token
        print("STORAGE login => :", app.storage.user)
    
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

            print("User logged in, redirecting to route")
            if not Auth.is_logged_in():
                ui.navigate.to("/login")
                ui.notify("Login required", color="negative")
                return

            user = Auth.user()

            # if not user:
            #     ui.navigate.to("/login")
            #     return

            # if user.get("exp", 0) < time.time():
            #     ui.notify("Session expired", color="negative")
            #     return

            if superuser and not user.get("is_superuser"):
                ui.notify("Admins only", color="negative")
                return

            result = func()
            if hasattr(result, "__await__"):
                await result

        return wrapper

    return decorator