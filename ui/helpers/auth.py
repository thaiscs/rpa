from nicegui import ui, app

def require_login():
    if not app.storage.user:
        ui.navigate.to('/login')
        return False
    return True


def require_superuser():
    user = app.storage.user
    if not user or not user.get("is_superuser"):
        ui.notify("Access denied", color="negative")
        ui.navigate.to('/login')
        return False
    return True

def admin_page(route: str):
    def decorator(func):
        @ui.page(route)
        def wrapper():
            if not require_login() or not require_superuser():
                return
            return func()
        return wrapper
    return decorator