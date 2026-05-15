# Tests

This directory contains the test suite for the RPA certificate management system.

## Running Tests

### Locally

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific module
pytest tests/shared/test_crypto.py

# Run with verbose output
pytest -v

# Run only fast tests (skip slow ones)
pytest -m "not slow"
```

### With Docker Compose

```bash
# Run tests in container
docker compose run test-runner pytest

# Run with coverage
docker compose run test-runner pytest --cov=. --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── shared/                     # Shared module tests
│   ├── test_crypto.py         # Encryption/decryption tests
│   ├── test_utils.py          # Utility function tests
│   ├── test_crud.py           # Database operation tests
│   ├── test_db.py             # Database connection tests
│   └── test_models.py         # SQLAlchemy model tests
├── api/                        # API module tests
│   ├── test_auth_backend.py   # Authentication backend tests
│   ├── test_auth_manager.py   # User manager tests
│   ├── test_auth_deps.py      # Authentication dependencies tests
│   ├── test_auth_schemas.py   # Pydantic schema tests
│   ├── test_auth_config.py    # Configuration tests
│   ├── test_auth_users.py     # FastAPI Users setup tests
│   ├── test_admin_routes.py   # Admin route tests
│   └── test_main.py           # FastAPI app tests
├── ui/                         # UI module tests
│   ├── test_helpers_auth.py   # Auth helper tests
│   ├── test_helpers_validation.py  # Validation helper tests
│   └── test_helpers_secret.py     # Secret helper tests
└── scripts/                    # Script tests
    └── test_init_secrets.py   # Secrets initialization tests
```

## Fixtures

Shared fixtures are defined in `conftest.py`:

- `test_fernet_key`: Valid Fernet key for encryption tests
- `test_jwt_secret`: Valid JWT secret for auth tests
- `sample_user_data`: Sample user data
- `sample_superuser_data`: Sample superuser data
- `sample_client_data`: Sample client data
- `sample_certificate_data`: Sample certificate data
- `mock_db_session`: Mock async SQLAlchemy session
- `mock_httpx_client`: Mock httpx client for UI tests
- `mock_app_storage`: Mock NiceGUI app.storage
- `sample_pfx_bytes`: Sample PFX file bytes
- `sample_pem_cert`: Sample PEM certificate
- `sample_pem_key`: Sample PEM private key

## CI/CD

Tests run automatically on GitHub Actions for:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

The workflow:
1. Sets up Python 3.11
2. Installs dependencies
3. Runs tests with PostgreSQL service
4. Uploads coverage to Codecov
5. Archives coverage reports

## Coverage

Coverage reports are generated in `htmlcov/` directory after running tests with `--cov-report=html`.

## Notes

- Tests use mocking for external services (RabbitMQ, NiceGUI)
- Tests use a separate test database (`certsdb_test`)
- Worker module tests are excluded (as requested)
- UI component tests are minimal due to NiceGUI complexity
