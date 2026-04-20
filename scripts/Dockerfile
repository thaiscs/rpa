FROM python:3.12-slim

WORKDIR /app

RUN pip install cryptography

COPY scripts /scripts

CMD ["python", "/scripts/init-secrets.py"]