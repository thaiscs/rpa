import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from shared.crud import save_client_cert, fetch_client_cert
from shared.models.client import Client, PersonTypeEnum
from shared.models.certificate import Certificate


@pytest.fixture
async def db_session():
    """Create a mock async session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.begin = MagicMock(return_value=AsyncMock())
    return session


@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return {
        "legal_name": "Test Company Ltd",
        "tax_id": "12345678000190",
        "person_type": "company"
    }


@pytest.fixture
def sample_cert_data():
    """Sample certificate data for testing."""
    return {
        "cert_name": "test_cert",
        "cert_bytes": b"pfx_data",
        "cert_password": "password123"
    }


class TestSaveClientCert:
    """Tests for save_client_cert function."""

    @patch("shared.crud.extract_pfx_components")
    @patch("shared.crud.encrypt")
    @patch("shared.crud.extract_cert_metadata")
    async def test_save_new_client_and_cert(
        self,
        mock_extract_metadata,
        mock_encrypt,
        mock_extract_pfx,
        db_session,
        sample_client_data,
        sample_cert_data
    ):
        """Test saving a new client and certificate."""
        # Setup mocks
        mock_extract_pfx.return_value = (b"private_key", b"certificate")
        mock_encrypt.side_effect = lambda x: {"version": 1, "ciphertext": x.decode()}
        mock_extract_metadata.return_value = ("CN=Test", "2024-01-01", "2025-01-01")

        # Mock database execution — first call returns client_id, second returns cert_id
        client_id = uuid.uuid4()
        cert_id = uuid.uuid4()

        db_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalar_one_or_none=MagicMock(return_value=client_id)),
            AsyncMock(scalar_one_or_none=MagicMock(return_value=cert_id)),
        ])

        result = await save_client_cert(
            db=db_session,
            **sample_client_data,
            **sample_cert_data
        )

        assert result["client_id"] == client_id
        assert result["cert_id"] == cert_id

    @patch("shared.crud.extract_pfx_components")
    async def test_extract_pfx_called_with_correct_args(
        self,
        mock_extract_pfx,
        db_session,
        sample_client_data,
        sample_cert_data
    ):
        """Test that extract_pfx_components is called with correct arguments."""
        mock_extract_pfx.return_value = (b"private_key", b"certificate")

        # Mock other dependencies
        with patch("shared.crud.encrypt", return_value={"version": 1, "ciphertext": "encrypted"}), \
             patch("shared.crud.extract_cert_metadata", return_value=("CN=Test", "2024-01-01", "2025-01-01")):

            # Mock database execution
            db_session.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=AsyncMock(return_value=uuid.uuid4())))

            await save_client_cert(
                db=db_session,
                **sample_client_data,
                **sample_cert_data
            )

            mock_extract_pfx.assert_called_once_with(
                sample_cert_data["cert_bytes"],
                sample_cert_data["cert_password"]
            )

    @patch("shared.crud.extract_pfx_components")
    async def test_invalid_pfx_password_raises_error(
        self,
        mock_extract_pfx,
        db_session,
        sample_client_data,
        sample_cert_data
    ):
        """Test that invalid PFX password raises an error."""
        mock_extract_pfx.side_effect = ValueError("Invalid password")

        with pytest.raises(ValueError, match="Invalid password"):
            await save_client_cert(
                db=db_session,
                **sample_client_data,
                **sample_cert_data
            )


class TestFetchClientCert:
    """Tests for fetch_client_cert function."""

    @patch("shared.crud.decrypt")
    async def test_fetch_valid_client_cert(self, mock_decrypt, db_session):
        """Test fetching a valid client certificate."""
        client_id = uuid.uuid4()

        # Mock certificate
        mock_cert = MagicMock()
        mock_cert.encrypted_cert = {"nonce": "nonce1", "ciphertext": "cert_cipher"}
        mock_cert.encrypted_key = {"nonce": "nonce2", "ciphertext": "key_cipher"}

        # Mock database query — use MagicMock so scalars().first() is synchronous
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_cert
        db_session.execute = AsyncMock(return_value=mock_result)

        # Mock decrypt
        mock_decrypt.side_effect = lambda ciphertext: b"decrypted_data"

        cert_bytes, key_bytes = await fetch_client_cert(db_session, str(client_id))

        assert cert_bytes == b"decrypted_data"
        assert key_bytes == b"decrypted_data"

    async def test_fetch_nonexistent_client_raises_error(self, db_session):
        """Test that fetching non-existent client raises error."""
        client_id = uuid.uuid4()

        # Mock empty result — use MagicMock so scalars().first() is synchronous
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        db_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(RuntimeError, match="does not have stored certificates"):
            await fetch_client_cert(db_session, str(client_id))
