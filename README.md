# RPA — Certificate Management System

Robotic Process Automation platform for managing digital certificates (PFX/A1) used for Brazilian tax authority (e-CAC) integrations.

## Architecture

```
rpa/
├── api/        FastAPI backend — JWT auth, certificate upload, job dispatch
├── ui/         NiceGUI admin panel — client and certificate management
├── worker/     Async RPA job processor — decrypts certs, runs automation bots
├── shared/     Shared library — DB models, Fernet encryption, CRUD operations
└── alembic/    Database migrations
```

**Services at a glance**

| Service | Stack | Port |
|---------|-------|------|
| `api` | FastAPI + fastapi-users + SQLAlchemy | 8080 |
| `ui` | NiceGUI | 3000 |
| `postgres` | PostgreSQL 16 | 5432 |
| `rabbitmq` | RabbitMQ | 5672 / 15672 (management UI) |

Certificate data (PFX, password, key, cert) is encrypted at rest using Fernet symmetric encryption before being stored in PostgreSQL.

## Quick start

```bash
docker compose up --build
```

The API will be at `http://localhost:8080` and the admin panel at `http://localhost:3000`.

### Stop and clean up

```bash
docker compose down --remove-orphans   # stop, keep volumes
docker compose down -v                 # stop and delete volumes
```

## Development

### Run services individually

```bash
# API
cd api && python main.py

# UI
cd ui && python main.py
```

### Useful Docker commands

```bash
docker compose down --remove-orphans
docker compose down -v
docker volume rm rpa_secrets-store
docker compose stop postgres
docker compose rm -f postgres
docker system prune -f
docker compose build --no-cache web
docker compose up --build --force-recreate
docker compose up --force-recreate
docker compose ps -a
docker compose images
docker compose logs -f api
docker compose run migrations sh
```

### Database access

```bash
docker exec -it rpa-postgres-1 psql -U postgres -d certsdb

sudo lsof -i :5432
sudo systemctl stop postgresql
```

```sql
SELECT * FROM clients;
SELECT * FROM certificates LIMIT 1;
\dt          -- list tables
\d+ clients  -- describe table
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply via Docker
docker compose run migrations

# Rollback one step
alembic downgrade -1

# View history
alembic history --verbose
```

## Testing

### With Docker (recommended)

The `test-runner` service uses the `test` profile so it doesn't start with the normal stack:

```bash
# Run all tests
docker compose --profile test run test-runner pytest

# With coverage report
docker compose --profile test run test-runner pytest --cov=. --cov-report=html
```

### Locally

```bash
pip install -r requirements-test.txt

# Generate test secrets once
mkdir -p /tmp/test-secrets
python -c "from cryptography.fernet import Fernet; open('/tmp/test-secrets/fernet.key','w').write(Fernet.generate_key().decode())"
echo "any-string-at-least-32-chars-long" > /tmp/test-secrets/auth.key

# Run all tests
SECRETS_DIR=/tmp/test-secrets pytest

# With HTML coverage report
SECRETS_DIR=/tmp/test-secrets pytest && open htmlcov/index.html
```

167 tests across api, shared, ui, worker, and scripts. See [`tests/README.md`](tests/README.md) for full documentation.

## Deployment checklist

- [ ] Enable HTTPS — see [NiceGUI deployment docs](https://nicegui.io/documentation/section_configuration_deployment#server_hosting)
- [ ] Harden Dockerfiles with a non-root user
- [ ] Remove docker volumes
- [ ] Rotate Fernet and auth keys and store them in a KMS (AWS KMS, HashiCorp Vault, or Azure Key Vault) instead of a secrets volume
- [ ] Review input sanitisation (Pydantic handles API schemas; UI forms have client-side validation)

## Backlog

- Change `encrypted_*` certificate columns from JSONB to BYTEA for better storage efficiency
- Role-based access and client tenancy in the UI
- Certificate expiry health check job
- RabbitMQ worker re-enable and end-to-end RPA flow testing
