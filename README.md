## ToDo

- UI for uploading certificate
- Deploy
- Armazenar a chave de criptografia em um KMS (AWS KMS, HashiCorp Vault, Azure Key Vault).

## Overview

This repository contains a small RPA (Robotic Process Automation) project with:

- `api/`: Flask API service
- `worker/`: Background worker service
- `shared/`: Shared utilities (database, crypto, etc.)
- `docker-compose.yml`: Orchestrates the services

## Quick Start

### Run with Docker Compose

```bash
docker compose up --build
```

### Other useful commands
```bash
docker compose down --remove-orphans
docker compose stop postgres
docker compose rm -f postgres
docker system prune -f
docker compose build --no-cache web
docker compose up --build --force-recreate
docker compose up
docker compose up --force-recreate
docker compose ps -a
docker compose images
docker compose logs -f api
docker compose exec api sh
OR
docker compose start
OR
docker start rpa-api-1
docker logs rpa-api-1
POSTGRES
sudo lsof -i :5432
sudo systemctl stop postgresql
docker compose start postgres
openssl rand 32 > ./aes_key.key
```

The above command builds and starts the `api` and `worker` services.

### Accessing the API

By default, the API will be available at:

```text
http://localhost:5000
```

## Development Notes

### API

The API service is defined in `api/app.py` and has its own `requirements.txt`.

### Worker

The worker service is defined in `worker/worker.py` and has its own `requirements.txt`.

## Useful Commands

### Run API locally without Docker

```bash
cd api
python app.py
```

### Run Worker locally without Docker

```bash
cd worker
python worker.py
```

## Helpful Markup Blocks

### Code Block Example

```python
def hello():
		print("Hello from the RPA project!")
```

### JSON Example

```json
{
	"status": "ok",
	"message": "This is a sample markup block."
}
```

