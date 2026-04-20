import pika
import json

# -----------------------------
# RABBITMQ SERVICE
# -----------------------------
def publish_job(payload: dict):
    # connecting to shared/worker thru aio-pika async??

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
