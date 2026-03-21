FROM python:3.11-slim

WORKDIR /app

# Instalar dependências básicas de build (psycopg2 precisa de libpq, gcc, etc)
# RUN apt-get update && apt-get install -y \
#    gcc \
#   libpq-dev \
#  && rm -rf /var/lib/apt/lists/*

COPY shared/shared/ shared/
COPY worker/ worker/
COPY worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Garantir que /app está no PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python", "worker/worker.py"]