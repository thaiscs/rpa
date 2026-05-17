# Test Suite

Tests for the RPA certificate management system, covering the shared library, API, UI helpers, worker, and initialization scripts.

**167 tests** across 20 files — all passing.

---

## Quick start

```bash
# Install dependencies
pip install -r requirements-test.txt

# Tests require Fernet and JWT keys on disk.
# Point SECRETS_DIR at a directory that contains fernet.key and auth.key.
# For local runs, generate them once:
mkdir -p /tmp/test-secrets
python -c "from cryptography.fernet import Fernet; open('/tmp/test-secrets/fernet.key','w').write(Fernet.generate_key().decode())"
echo "any-string-at-least-32-chars-long" > /tmp/test-secrets/auth.key

# Run everything
SECRETS_DIR=/tmp/test-secrets pytest

# Common flags
SECRETS_DIR=/tmp/test-secrets pytest -v                        # verbose per-test output
SECRETS_DIR=/tmp/test-secrets pytest --no-cov                  # skip coverage (faster)
SECRETS_DIR=/tmp/test-secrets pytest tests/api/                # one directory
SECRETS_DIR=/tmp/test-secrets pytest tests/shared/test_crypto.py  # one file
SECRETS_DIR=/tmp/test-secrets pytest -k "upload_cert"          # tests matching a name
SECRETS_DIR=/tmp/test-secrets pytest -m "not slow"             # exclude slow tests
```

### Coverage report

Running `pytest` (without `--no-cov`) generates an HTML report in `htmlcov/`:

```bash
# Generate and open in one step
SECRETS_DIR=/tmp/test-secrets pytest && open htmlcov/index.html        # macOS
SECRETS_DIR=/tmp/test-secrets pytest && xdg-open htmlcov/index.html   # Linux
SECRETS_DIR=/tmp/test-secrets pytest && start htmlcov/index.html       # Windows

# Or serve it locally if your browser can't open file:// paths directly
python -m http.server 8080 --directory htmlcov
# then visit http://localhost:8080
```

The terminal output already shows a `--cov-report=term-missing` summary after each run — the `Missing` column lists the exact line numbers not covered, so you usually don't need to open the HTML unless you want to click through the source.

### Why SECRETS_DIR is required

`shared/shared/crypto.py` and `api/auth/config.py` load real key files at **import time** (module-level globals). There is no lazy loading, so the keys must exist before any test module is collected. In CI, the GitHub Actions workflow creates them as part of the setup step.

### Docker

```bash
docker compose run test-runner pytest
docker compose run test-runner pytest --cov=. --cov-report=html
```

---

## Directory layout

```
tests/
├── conftest.py                      # Shared fixtures (keys, mock sessions, sample data)
│
├── api/                             # FastAPI backend
│   ├── test_admin_routes.py         # Endpoint tests for /admin/upload-cert and /admin/send-job
│   ├── test_auth_backend.py         # JWT strategy and bearer transport config
│   ├── test_auth_config.py          # Secret file loading
│   ├── test_auth_deps.py            # Auth dependency guards (unit + HTTP enforcement)
│   ├── test_auth_manager.py         # UserManager setup
│   ├── test_auth_schemas.py         # Pydantic UserRead / UserCreate / UserUpdate
│   ├── test_auth_users.py           # fastapi_users instance
│   ├── test_main.py                 # App creation and route registration
│   └── test_queue_service.py        # RabbitMQ publish_job
│
├── shared/                          # Shared library
│   ├── test_crypto.py               # Fernet encrypt/decrypt, PFX extraction, cert metadata
│   ├── test_crud.py                 # save_client_cert and fetch_client_cert
│   ├── test_db.py                   # Engine, session factory, get_db generator
│   ├── test_models.py               # SQLAlchemy Client, Certificate, User models
│   ├── test_triggers.py             # PostgreSQL updated_at trigger creation
│   └── test_utils.py                # get_person_type (CPF / CNPJ classification)
│
├── ui/                              # NiceGUI frontend helpers and components
│   ├── test_cert_form.py            # handle_upload and submit_form logic
│   ├── test_helpers_auth.py         # Auth class methods + @protected decorator behavior
│   ├── test_helpers_parsing.py      # parse_err error formatting
│   ├── test_helpers_secret.py       # Secrets.storage_key file loading
│   └── test_helpers_validation.py   # validate_tax_id (CPF / CNPJ format)
│
├── worker/                          # Background RPA worker
│   ├── conftest.py                  # Adds worker/ to sys.path so worker.py is importable
│   └── test_worker.py               # run_rpa and process_job
│
└── scripts/
    └── test_init_secrets.py         # ensure() key generation and idempotency
```

---

## What each module tests

### `tests/shared/`

| File | Source | Key scenarios |
|------|--------|---------------|
| `test_crypto.py` | `shared/crypto.py` | `load_fernet_key` (valid, whitespace-stripped, missing file); `encrypt`/`decrypt` round-trip; `decrypt` with tampered token; `extract_pfx_components` (valid PFX, wrong password, missing key/cert); `extract_cert_metadata` field extraction |
| `test_crud.py` | `shared/crud.py` | `save_client_cert` creates client + cert, passes correct args to `extract_pfx_components`, raises on invalid password; `fetch_client_cert` happy path, raises when client has no cert |
| `test_db.py` | `shared/db.py` | `DATABASE_URL` format, `engine` and `AsyncSessionLocal` existence, `Base` declarative metadata, `get_db` yields an `AsyncSession` |
| `test_models.py` | `shared/models/` | `Client` table name, columns, `PersonTypeEnum` values; `Certificate` columns and FK to `Client`; `User` extends FastAPI-Users base with `name` and `client_id` |
| `test_triggers.py` | `shared/triggers.py` | `create_updated_at_trigger` executes two SQL statements (function + trigger) against the DB session |
| `test_utils.py` | `shared/utils.py` | 11-digit → `"PF"`, 14-digit → `"PJ"`, wrong length raises, formatted strings (`.`/`/`/`-`) stripped before check, non-numeric raises |

### `tests/api/`

| File | Source | Key scenarios |
|------|--------|---------------|
| `test_admin_routes.py` | `api/admin/routes.py` | **upload-cert**: 200 with correct body, save called with all form fields, error from save → 500 + detail, no token → 401; **send-job**: 200 + queued status, payload echoed, non-superuser → 403, no token → 401, missing `data` field → 422 |
| `test_auth_backend.py` | `api/auth/backend.py` | `bearer_transport` type, `get_jwt_strategy` returns `JWTStrategy` with correct secret and 8-hour lifetime, `auth_backend` name and wiring |
| `test_auth_config.py` | `api/auth/config.py` | `load_secret` reads and strips the key file, raises `RuntimeError` when file is absent |
| `test_auth_deps.py` | `api/auth/deps.py` | `current_admin` and `current_superuser` are callable; HTTP-level: upload-cert without token → 401, send-job without token → 401, send-job with non-superuser → 403 |
| `test_auth_manager.py` | `api/auth/manager.py` | `UserManager` has correct secret attributes, `get_user_manager` yields a `UserManager` backed by the SQLAlchemy DB |
| `test_auth_schemas.py` | `api/auth/schemas.py` | `UserRead` valid with and without `client_id`; `UserCreate` valid and invalid email; `UserUpdate` with name, with password, empty |
| `test_auth_users.py` | `api/auth/users.py` | `fastapi_users` is a `FastAPIUsers` instance and exposes `current_user` |
| `test_main.py` | `api/main.py` | App title and version, all router prefixes registered (auth, users, admin) |
| `test_queue_service.py` | `api/services/queue_service.py` | `publish_job` connects, publishes correct JSON body, raises on connection error |

### `tests/ui/`

| File | Source | Key scenarios |
|------|--------|---------------|
| `test_cert_form.py` | `ui/components/cert_form.py` | `handle_upload`: sets `uploaded_file` global, notification includes filename and is "positive"; `submit_form` validation: each empty field, missing file, invalid tax_id, API never called on failure; `submit_form` API: correct POST body, 200 opens dialog + resets file, 500 uses generic message (no dialog), 4xx calls `show_error_dialog` with detail |
| `test_helpers_auth.py` | `ui/helpers/auth.py` | `Auth` class: `token` (valid, expired, absent), `_is_expired`, `fetch_user` (200 stores user, exception is swallowed), `login` stores token + expiry, `logout` clears all keys, `is_logged_in`, `is_superuser`, `user`; `@protected` decorator: no token → redirect + "Login required", expired token → redirect + "expired", logged-in → page called, logged-in non-superuser on `superuser=True` page → blocked + "Admins only", superuser → page called, async page function → awaited |
| `test_helpers_parsing.py` | `ui/helpers/parsing.py` | `parse_err` for dict, nested list of dicts, plain string, `None`, and all normalisation paths (lowercase, strip, capitalise) |
| `test_helpers_secret.py` | `ui/helpers/secret.py` | `Secrets.storage_key` reads and strips the key file, raises when absent |
| `test_helpers_validation.py` | `ui/helpers/validation.py` | `validate_tax_id`: valid CPF, valid CNPJ, too short, too long, formatted strings, non-numeric |

### `tests/worker/`

| File | Source | Key scenarios |
|------|--------|---------------|
| `test_worker.py` | `worker/worker.py` | `run_rpa`: writes cert + key bytes to separate temp files, closes handles before subprocess, passes correct paths and flags (`check=True`, `capture_output=True`) to subprocess, deletes both files on success, deletes both files even when subprocess raises; `process_job`: empty/None `client_id` raises, happy path creates DB session and calls `fetch_client_cert(db, client_id)` then dispatches `run_rpa` via executor, fetch error propagates, executor error propagates |

### `tests/scripts/`

| File | Source | Key scenarios |
|------|--------|---------------|
| `test_init_secrets.py` | `scripts/init_secrets.py` | `ensure` creates new key file, skips when file already has content, overwrites when file is empty |

---

## Shared fixtures (`conftest.py`)

| Fixture | Type | Purpose |
|---------|------|---------|
| `test_fernet_key` | `bytes` | Fresh `Fernet.generate_key()` for crypto tests |
| `test_jwt_secret` | `str` | Static string for auth config tests |
| `sample_user_data` | `dict` | Regular user fields (not superuser) |
| `sample_superuser_data` | `dict` | Same structure with `is_superuser=True` |
| `sample_client_data` | `dict` | Client with a CNPJ tax_id |
| `sample_certificate_data` | `dict` | Certificate with pre-encrypted field stubs |
| `mock_db_session` | `AsyncMock` | Async SQLAlchemy session with `.begin()` context |
| `mock_httpx_client` | `AsyncMock` | HTTP client for UI tests |
| `mock_app_storage` | `MagicMock` | NiceGUI `app.storage` with a writable `.user` dict |
| `sample_pfx_bytes` | `bytes` | Placeholder PFX bytes |
| `sample_pem_cert` | `bytes` | Placeholder PEM certificate block |
| `sample_pem_key` | `bytes` | Placeholder PEM private key block |

---

## Test types

### Unit tests
Pure function tests where all I/O and external dependencies are mocked. Used for:
- Crypto (`encrypt`, `decrypt`, `extract_pfx_components`)
- Validation (`get_person_type`, `validate_tax_id`)
- Error parsing (`parse_err`)
- Secret loading (`load_fernet_key`, `load_secret`, `Secrets.storage_key`)
- Worker functions (`run_rpa`, `process_job`)
- UI form logic (`handle_upload`, `submit_form`)

### Integration tests (light)
Real FastAPI request/response cycle using `TestClient`, with auth and DB dependencies overridden. The HTTP stack — routing, middleware, request parsing, response serialisation — runs for real. Used for:
- All admin route tests
- Auth enforcement tests in `test_auth_deps.py`

Auth is bypassed by replacing `current_admin` / `current_superuser` with `lambda: mock_user` via `app.dependency_overrides`. The DB session is replaced with an `AsyncMock` via the same mechanism.

### Behaviour / contract tests
The inner logic of a decorator or class method is exercised by injecting controlled state, without a running framework. Used for:
- `@protected` decorator — `ui.page` is mocked as a pass-through so the `wrapper` function can be called and inspected directly
- `Auth` class methods — `app.storage.user` is replaced with a plain dict

---

## Mocking strategy

| External dependency | Approach |
|--------------------|----------|
| PostgreSQL / SQLAlchemy | `AsyncMock` session; real DB never touched |
| Fernet key on disk | `SECRETS_DIR` env var points at a temp dir with generated keys |
| RabbitMQ / aio-pika | `patch("api.services.queue_service.pika")` / `patch("worker.aio_pika")` |
| NiceGUI (`ui`, `app`) | `patch("ui.helpers.auth.ui", MagicMock())` etc.; NiceGUI is installed but its server is never started |
| httpx HTTP calls | `patch("ui.helpers.auth.httpx.AsyncClient", ...)` with a mock context manager |
| Subprocess (bot.py) | `patch("worker.subprocess.run")` |
| Temp files | `patch("worker.tempfile.NamedTemporaryFile")` + `patch("worker.os.remove")` |
| UI-internal imports (`helpers.*`, `components.*`) | Stubbed in `sys.modules` before `cert_form` is imported (those bare imports only resolve when run from the `ui/` directory) |

---

## CI/CD

Tests run automatically on GitHub Actions (`.github/workflows/tests.yml`) on every push and pull request to `main` or `develop`.

The workflow:
1. Starts a PostgreSQL 16 service container
2. Sets up Python 3.11
3. Generates `fernet.key` and `auth.key` in a temp directory
4. Installs `requirements-test.txt`
5. Runs `pytest --cov=. --cov-report=xml`
6. Uploads coverage to Codecov and archives the HTML report

---

## Known gaps

| Area | Status |
|------|--------|
| UI pages (`login.py`, `signup.py`, password reset, etc.) | Not tested — NiceGUI pages require a running server; would need Playwright or similar |
| UI components (`sidebar.py`, `err_toast.py`, `err_dialog.py`) | Not tested — pure rendering, no testable logic |
| Worker main loop (`worker()`) | Not tested — infinite loop; individual handlers (`process_job`, `run_rpa`) are covered instead |
| PostgreSQL triggers (real execution) | `test_triggers.py` mocks the DB call; actual trigger firing on UPDATE is not verified |
| Database migrations (`alembic/`) | Not tested |
