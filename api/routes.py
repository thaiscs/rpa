from fastapi import APIRouter, Depends, HTTPException, Form

router = APIRouter()

# -----------------------------
# LOGIN
# -----------------------------
from api.auth.users import fastapi_users, auth_backend
from api.auth.manager import get_user_manager

router = APIRouter()

@router.post("/login", tags=["auth"])
async def custom_login(
    email: str = Form(...),
    password: str = Form(...),
    user_db = Depends(get_user_manager),
):
    login_result = await auth_backend.login(
        {"username": email, "password": password},
        user_db,
    )

    if login_result is None:
        print("Login failed:", login_result)  # Debug log
        raise HTTPException(status_code=400, detail="LOGIN_BAD_CREDENTIALS")

    # login_result contains access token info
    return {
        "access_token": login_result["access_token"],
        "token_type": "bearer",
        "user": {
            "email": email,
        }
    }