import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from cryptography.fernet import Fernet


@pytest.fixture
def test_fernet_key():
    """Generate a valid Fernet key for testing."""
    return Fernet.generate_key()


@pytest.fixture
def test_jwt_secret():
    """Generate a valid JWT secret for testing."""
    return "test_jwt_secret_key_for_testing_purposes"


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "name": "Test User",
        "client_id": None
    }


@pytest.fixture
def sample_superuser_data():
    """Sample superuser data for testing."""
    return {
        "id": uuid.uuid4(),
        "email": "admin@example.com",
        "hashed_password": "hashed_password",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "name": "Admin User",
        "client_id": None
    }


@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return {
        "id": uuid.uuid4(),
        "legal_name": "Test Company Ltd",
        "tax_id": "12345678000190",
        "person_type": "company"
    }


@pytest.fixture
def sample_certificate_data():
    """Sample certificate data for testing."""
    return {
        "id": uuid.uuid4(),
        "client_id": uuid.uuid4(),
        "name": "test_cert",
        "encrypted_pfx": {"version": 1, "ciphertext": "encrypted_pfx"},
        "encrypted_pfx_password": {"version": 1, "ciphertext": "encrypted_password"},
        "encrypted_cert": {"version": 1, "ciphertext": "encrypted_cert"},
        "encrypted_key": {"version": 1, "ciphertext": "encrypted_key"},
        "issuer": "CN=Test CA",
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": "2025-01-01T00:00:00Z",
        "expired": False
    }


@pytest.fixture
def mock_db_session():
    """Create a mock async session for testing."""
    session = AsyncMock()
    session.begin = MagicMock(return_value=AsyncMock())
    return session


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx.AsyncClient for UI tests."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_app_storage():
    """Create a mock NiceGUI app.storage for UI tests."""
    storage = MagicMock()
    storage.user = {}
    return storage


@pytest.fixture
def sample_pfx_bytes():
    """Sample PFX bytes for testing."""
    return b"mock_pfx_data_for_testing"


@pytest.fixture
def sample_pem_cert():
    """Sample PEM certificate for testing."""
    return b"""-----BEGIN CERTIFICATE-----
MIICljCCAX4CCQCKz8Vz8Vz8VzANBgkqhkiG9w0BAQsFADAxMQswCQYDVQQGEwJCUjET
MBEGA1UECAwKU2FvIFBhdWxvMRIwEAYDVQQHDAlTYW8gUGF1bG8wHhcNMjQwMTAxMDAw
MDAwWhcNMjUwMTAxMDAwMDAwWjAxMQswCQYDVQQGEwJCUjETMBEGA1UECAwKU2FvIFBh
dWxvMRIwEAYDVQQHDAlTYW8gUGF1bG8wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQC...
-----END CERTIFICATE-----"""


@pytest.fixture
def sample_pem_key():
    """Sample PEM private key for testing."""
    return b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"""
