import asyncio
import json
import os
import tempfile
import subprocess
import logging
import aio_pika

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
# Execução RPA usando PEM temporários (sync)
# --------------------------------------------------
def run_rpa(job, cert_bytes, key_bytes):
    logger.info(f"Starting RPA for job: {job}")

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
        subprocess.run(
            ["python3", "automation/bot.py", cert_path, key_path],
            check=True,
            capture_output=True
        )
        logger.info("RPA completed successfully.")

    finally:
        os.remove(cert_path)
        os.remove(key_path)

        del cert_bytes
        del key_bytes

        logger.info("Temporary certificates securely destroyed.")

# --------------------------------------------------
# Process job (sync)
# --------------------------------------------------
def process_job(job):
    client_id = job.get("client_id")
    if not client_id:
        raise RuntimeError("Job missing client_id")

    cert_bytes, key_bytes = fetch_client_cert(client_id)
    run_rpa(job, cert_bytes, key_bytes)

# --------------------------------------------------
# Async wrapper so sync tasks don't block event loop
# --------------------------------------------------
async def process_job_async(job):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, process_job, job)

# --------------------------------------------------
# Main worker loop
# --------------------------------------------------
async def worker():
    logger.info("Secure async worker is starting…")

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/"
    )

    channel = await connection.channel()
    queue = await channel.declare_queue("jobs", durable=True)

    logger.info("Worker ready. Listening for messages…")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(ignore_processed=True):
                try:
                    job = json.loads(message.body)
                    await process_job_async(job)

                except json.JSONDecodeError:
                    logger.error("Invalid JSON received → rejecting permanently.")
                    await message.reject(requeue=False)

                except Exception as e:
                    logger.exception(f"Job failed: {e}")
                    await message.reject(requeue=True)

# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(worker())
    except KeyboardInterrupt:
        logger.warning("Worker interrupted manually.")