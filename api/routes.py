from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

router = APIRouter()

# -----------------------------
# PUBLIC HOME
# -----------------------------
@router.get("/", response_class=PlainTextResponse)
async def home():
    return "Dashboard ativo — envie jobs via POST /send-job"