import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_admin
from api.auth.deps import current_superuser # for internal routes, we use superuser guard
from api.auth.schemas import UserRead as User
from api.services.queue_service import publish_job

from shared.db import get_db
from shared.crud import save_client_cert
from shared.utils import get_person_type

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(current_admin)]
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
    legal_name: str = Form(..., alias="razao_social"),
    tax_id: str = Form(..., alias="CNPJ_CPF"),
    cert_name: str = Form(...),
    cert_password: str = Form(...),
    cert_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
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
        raise HTTPException(status_code=500, detail=str(e))
    

# -----------------------------
# MODELS
# -----------------------------
from pydantic import BaseModel

class JobPayload(BaseModel):
    job_type: str
    data: dict


# -----------------------------
# JOB QUEUE (INTERNAL ROUTES)
# -----------------------------

@router.post("/admin/send-job")
async def send_job(
        payload: JobPayload,
        user: User = Depends(current_superuser)
    ):
    # publish_job(payload.dict())
    return {"status": "queued", "job": payload}
