from multiprocessing.dummy.connection import Client
import os
from flask import Flask, request, jsonify
import pika
import json
import logging
from shared.db import save_client_cert
from shared.utils import get_person_type

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

app = Flask(__name__)

@app.post("/upload-cert")
def upload_cert():
    log.info("==== /upload-cert called ====")

    try:
        # -----------------------------
        # Step 1: Read form fields
        # -----------------------------
        log.info("Reading form fields...")
        
        legal_name = request.form.get("razao_social")
        tax_id = request.form.get("CNPJ_CPF")
        cert_name = request.form.get("name")
        cert_file = request.files.get("cert_file")
        cert_password = request.form.get("cert_password")
        person_type = get_person_type(tax_id)
        # DEBUG: veja exatamente o que está indo pro DB
        print("DEBUG: values going to DB ->", tax_id, legal_name, person_type)
        print("DEBUG types:", type(tax_id), type(legal_name), type(person_type))
        if not legal_name or not tax_id or not cert_name or not cert_file or not cert_password:
            log.warning("Missing required fields.")
            return jsonify({"error": "Todos os campos são obrigatórios."}), 400

        log.info(f"Cliente: {legal_name} | CNPJ/CPF: {tax_id} | Certificado: {cert_name}")

        # -----------------------------
        # Step 2: Read certificate bytes
        # -----------------------------
        log.info("Reading certificate file bytes...")
        file_bytes = cert_file.read()

        # -----------------------------
        # Step 3: Delegate encrypt + DB save
        # -----------------------------
        save_client_cert(
            legal_name=legal_name,
            tax_id=tax_id,
            cert_name=cert_name,
            cert_bytes=file_bytes,
            cert_password=cert_password,
            person_type=str(person_type)
        )

        return jsonify({
            "message": "Cliente e certificado armazenados com sucesso.",
            "razao_social": legal_name,
            "cnpj_cpf": tax_id,
            "cert_name": cert_name
        }), 201

    except Exception as e:
        log.exception("Error in /upload-cert")
        return jsonify({"error": str(e)}), 500

def publish_job(payload):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("rabbitmq")
    )
    channel = connection.channel()
    channel.queue_declare(queue="jobs")

    channel.basic_publish(
        exchange="",
        routing_key="jobs",
        body=json.dumps(payload)
    )

    connection.close()

@app.post("/send-job")
def send_job():
    payload = request.json
    # publish_job(payload)
    return jsonify({"status": "queued", "job": payload})

# --------------------------------------------------
# Dashboard for monitoring jobs
# --------------------------------------------------
@app.get("/")
def home():
    return "Dashboard ativo — envie jobs via POST /send-job"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)