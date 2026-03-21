import pika
import json
import os
import time
import tempfile
import subprocess
import logging
from pika.exceptions import AMQPConnectionError

from shared.db import fetch_client_cert

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RPA worker")

# --------------------------------------------------
# Execução RPA usando PEM temporários
# --------------------------------------------------
def run_rpa(job, cert_bytes, key_bytes):
    logger.info(f"Starting RPA for job: {job}")

    # Cria PEM temporários
    cert_tmp = tempfile.NamedTemporaryFile(delete=False)
    key_tmp = tempfile.NamedTemporaryFile(delete=False)

    cert_tmp.write(cert_bytes)
    key_tmp.write(key_bytes)

    cert_tmp.close()
    key_tmp.close()

    cert_path = cert_tmp.name
    key_path = key_tmp.name

    logger.info(f"Temporary cert paths: {cert_path}, {key_path}")

    try:
        # Aqui entra a automação real
        # Exemplo: acessar gov.br, eCAC, SEFAZ, etc
        subprocess.run(
            ["python3", "automation/bot.py", cert_path, key_path],
            check=True,
            capture_output=True
        )

        logger.info("RPA completed successfully.")

    finally:
        # Remove arquivos imediatamente
        os.remove(cert_path)
        os.remove(key_path)

        # Limpa da memória
        del cert_bytes
        del key_bytes

        logger.info("Temporary certificates securely destroyed.")

# --------------------------------------------------
# Processamento
# --------------------------------------------------
def process_job(job):
    client_id = job.get("client_id")
    if not client_id:
        raise RuntimeError("Job missing client_id")

    # 1. Buscar cert criptografado
    cert_bytes, key_bytes = fetch_client_cert(client_id)

    # 2. Executar automação real
    run_rpa(job, cert_bytes, key_bytes)

# --------------------------------------------------
# Callback do RabbitMQ
# --------------------------------------------------
def callback(ch, method, properties, body):
    try:
        job = json.loads(body)
        process_job(job)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logger.error("Invalid JSON received. Rejecting permanently.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        logger.exception(f"Job failed: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# --------------------------------------------------
# Conexão resiliente ao RabbitMQ
# --------------------------------------------------
def connect_rabbitmq():
    retry = 0
    delay = 2

    while True:
        try:
            logger.info(f"Connecting to RabbitMQ (attempt {retry+1})...")
            return pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))

        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            time.sleep(delay)
            retry += 1
            delay = min(delay * 2, 30)  # cap 30s

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    logger.info("Secure worker is starting…")

    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue="jobs", durable=True)

    channel.basic_consume(queue="jobs", on_message_callback=callback)

    logger.info("Worker ready. Listening for messages…")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.warning("Worker interrupted manually.")
    # finally:
        # connection.close()


if __name__ == "__main__":
    main()  