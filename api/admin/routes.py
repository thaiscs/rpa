import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import (
    current_admin,
    current_superuser,  # for internal routes, we use superuser guard
)
from api.auth.schemas import UserRead as User
from shared.crud import save_client_cert
from shared.db import get_db
from shared.utils import get_person_type

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(current_admin)]  # noqa: B008
)

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

# -----------------------------
# ADMIN ROUTES
# -----------------------------

@router.post("admin/upload-cert")
async def upload_cert(
    legal_name: str = Form(..., alias="razao_social"),  # noqa: B008
    tax_id: str = Form(..., alias="CNPJ_CPF"),  # noqa: B008
    cert_name: str = Form(...),  # noqa: B008
    cert_password: str = Form(...),  # noqa: B008
    cert_file: UploadFile = File(...),  # noqa: B008
    db: AsyncSession = Depends(get_db)  # noqa: B008
):
    log.info("==== /upload-cert called ====")

    try:
        person_type = get_person_type(tax_id)

        # Read uploaded file
        file_bytes = await cert_file.read()

        # Save + encrypt via shared module
        await save_client_cert(
            db=db,
            legal_name=legal_name,
            tax_id=tax_id,
            cert_name=cert_name,
            cert_bytes=file_bytes,
            cert_password=cert_password,
            person_type=str(person_type)
        )

        return {
            "message": "Cliente e certificado armazenados com sucesso.",
            "razao_social": legal_name,
            "cnpj_cpf": tax_id,
            "cert_name": cert_name
        }

    except Exception as e:
        log.exception("Error in /upload-cert")
        raise HTTPException(status_code=500, detail=str(e)) from e


# -----------------------------
# MODELS
# -----------------------------

class JobPayload(BaseModel):
    job_type: str
    data: dict


# -----------------------------
# JOB QUEUE (INTERNAL ROUTES)
# -----------------------------

@router.post("/admin/send-job")
async def send_job(
        payload: JobPayload,
        user: User = Depends(current_superuser)  # noqa: B008
    ):
    # publish_job(payload.dict())
    return {"status": "queued", "job": payload}
