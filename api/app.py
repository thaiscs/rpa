import pika
import json
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from shared.db import save_client_cert
from shared.utils import get_person_type

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

app = FastAPI(title="RPA Backend", version="1.0.0")

# -----------------------------
# Models
# -----------------------------

class JobPayload(BaseModel):
    job_type: str
    data: dict


# -----------------------------
# Routes
# -----------------------------

@app.post("/upload-cert")
async def upload_cert(
    legal_name: str = Form(..., alias="razao_social"),
    tax_id: str = Form(..., alias="CNPJ_CPF"),
    cert_name: str = Form(...),
    cert_password: str = Form(...),
    cert_file: UploadFile = File(...)
):
    log.info("==== /upload-cert called ====")

    try:
        person_type = get_person_type(tax_id)
        log.info(f"Cliente: {legal_name} | CNPJ/CPF: {tax_id} | Certificado: {cert_name}")

        # read uploaded file
        file_bytes = await cert_file.read()

        # Step 3: Save + encrypt via shared module
        save_client_cert(
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

def publish_job(payload: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="jobs")

    channel.basic_publish(
        exchange="",
        routing_key="jobs",
        body=json.dumps(payload)
    )

    connection.close()

@app.post("/send-job")
async def send_job(payload: JobPayload):
    # publish_job(payload.dict())
    return {"status": "queued", "job": payload}


@app.get("/", response_class=PlainTextResponse)
async def home():
    return "Dashboard ativo — envie jobs via POST /send-job"