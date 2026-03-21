from multiprocessing.dummy.connection import Client
import os
from flask import Flask, request, jsonify
import pika
import json
import logging
from shared.db import save_client_cert  # método que fará encrypt + DB insert

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
        
        razao_social = request.form.get("razao_social")
        cnpj_cpf = request.form.get("CNPJ_CPF")
        cert_name = request.form.get("name")
        cert_file = request.files.get("cert_file")

        if not razao_social or not cnpj_cpf or not cert_name or not cert_file:
            log.warning("Missing required fields.")
            return jsonify({"error": "Todos os campos são obrigatórios."}), 400

        log.info(f"Cliente: {razao_social} | CNPJ/CPF: {cnpj_cpf} | Certificado: {cert_name}")

        # -----------------------------
        # Step 2: Read certificate bytes
        # -----------------------------
        log.info("Reading certificate file bytes...")
        file_bytes = cert_file.read()

        # -----------------------------
        # Step 3: Delegate encrypt + DB save
        # -----------------------------
        save_client_cert(
            razao_social=razao_social,
            cnpj_cpf=cnpj_cpf,
            cert_name=cert_name,
            cert_bytes=file_bytes
        )

        return jsonify({
            "message": "Cliente e certificado armazenados com sucesso.",
            "razao_social": razao_social,
            "cnpj_cpf": cnpj_cpf,
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