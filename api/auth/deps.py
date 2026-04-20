from api.auth.users import fastapi_users

# base user (authenticated)
current_admin = fastapi_users.current_user(active=True)

# internal / superuser guard
current_superuser = fastapi_users.current_user(superuser=True)