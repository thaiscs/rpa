import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet, InvalidToken

from shared.crypto import (
    load_fernet_key,
    encrypt,
    decrypt,
    extract_pfx_components,
    extract_cert_metadata
)


@pytest.fixture
def test_fernet_key():
    """Generate a valid Fernet key for testing."""
    return Fernet.generate_key()


@pytest.fixture
def test_pfx_bytes():
    """Sample PFX bytes for testing."""
    # This is a minimal valid PFX structure for testing
    # In real tests, you'd use an actual PFX file
    return b"mock_pfx_data"


@pytest.fixture
def test_pem_cert():
    """Sample PEM certificate for testing."""
    return b"""-----BEGIN CERTIFICATE-----
MIICljCCAX4CCQCKz8Vz8Vz8VzANBgkqhkiG9w0BAQsFADAxMQswCQYDVQQGEwJCUjET
MBEGA1UECAwKU2FvIFBhdWxvMRIwEAYDVQQHDAlTYW8gUGF1bG8wHhcNMjQwMTAxMDAw
MDAwWhcNMjUwMTAxMDAwMDAwWjAxMQswCQYDVQQGEwJCUjETMBEGA1UECAwKU2FvIFBh
dWxvMRIwEAYDVQQHDAlTYW8gUGF1bG8wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQC...
-----END CERTIFICATE-----"""


@pytest.fixture
def test_pem_key():
    """Sample PEM private key for testing."""
    return b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"""


class TestLoadFernetKey:
    """Tests for load_fernet_key function."""

    def test_load_valid_key(self, tmp_path, test_fernet_key, monkeypatch):
        """Test loading a valid Fernet key."""
        monkeypatch.setenv("SECRETS_DIR", str(tmp_path))
        key_file = tmp_path / "fernet.key"
        key_file.write_bytes(test_fernet_key)

        result = load_fernet_key()
        assert result == test_fernet_key

    def test_load_key_strips_whitespace(self, tmp_path, test_fernet_key, monkeypatch):
        """Test that whitespace is stripped from key."""
        monkeypatch.setenv("SECRETS_DIR", str(tmp_path))
        key_file = tmp_path / "fernet.key"
        key_file.write_text(f"  {test_fernet_key.decode()}  \n")

        result = load_fernet_key()
        assert result == test_fernet_key

    def test_load_key_missing_file(self, monkeypatch):
        """Test error when key file doesn't exist."""
        monkeypatch.setenv("SECRETS_DIR", "/nonexistent/path/that/does/not/exist")
        with pytest.raises(RuntimeError, match="Encryption key not found"):
            load_fernet_key()

    def test_load_key_invalid_format(self, tmp_path, monkeypatch):
        """Test error when key is not a valid Fernet key."""
        monkeypatch.setenv("SECRETS_DIR", str(tmp_path))
        key_file = tmp_path / "fernet.key"
        key_file.write_text("invalid_key")

        with pytest.raises(RuntimeError, match="not a valid Fernet key"):
            load_fernet_key()


class TestEncrypt:
    """Tests for encrypt function."""

    def test_encrypt_returns_dict_with_version(self, test_fernet_key):
        """Test that encrypt returns a dict with version field."""
        with patch("shared.crypto.fernet", Fernet(test_fernet_key)):
            data = b"test data"
            result = encrypt(data)

            assert isinstance(result, dict)
            assert "version" in result
            assert "ciphertext" in result
            assert result["version"] == 1

    def test_encrypt_decrypt_roundtrip(self, test_fernet_key):
        """Test that encrypt/decrypt roundtrip works."""
        with patch("shared.crypto.fernet", Fernet(test_fernet_key)):
            original = b"secret data"
            encrypted = encrypt(original)
            decrypted = decrypt(encrypted["ciphertext"])

            assert decrypted == original


class TestDecrypt:
    """Tests for decrypt function."""

    def test_decrypt_valid_ciphertext(self, test_fernet_key):
        """Test decrypting valid ciphertext."""
        fernet = Fernet(test_fernet_key)
        original = b"test data"
        ciphertext = fernet.encrypt(original).decode()

        with patch("shared.crypto.fernet", fernet):
            result = decrypt(ciphertext)
            assert result == original

    def test_decrypt_invalid_token(self, test_fernet_key):
        """Test error when ciphertext is invalid."""
        with patch("shared.crypto.fernet", Fernet(test_fernet_key)):
            with pytest.raises(RuntimeError, match="Invalid encryption token"):
                decrypt("invalid_ciphertext")


class TestExtractPfxComponents:
    """Tests for extract_pfx_components function."""

    @patch("shared.crypto.pkcs12")
    def test_extract_valid_pfx(self, mock_pkcs12, test_pem_key, test_pem_cert):
        """Test extracting components from valid PFX."""
        mock_private_key = MagicMock()
        mock_certificate = MagicMock()
        mock_private_key.private_bytes.return_value = test_pem_key
        mock_certificate.public_bytes.return_value = test_pem_cert

        mock_pkcs12.load_key_and_certificates.return_value = (
            mock_private_key,
            mock_certificate,
            None
        )

        private_key_pem, certificate_pem = extract_pfx_components(
            b"pfx_bytes",
            "password"
        )

        assert private_key_pem == test_pem_key
        assert certificate_pem == test_pem_cert

    @patch("shared.crypto.pkcs12")
    def test_extract_invalid_password(self, mock_pkcs12):
        """Test error when password is invalid."""
        mock_pkcs12.load_key_and_certificates.side_effect = ValueError("Invalid password")

        with pytest.raises(ValueError, match="Invalid password"):
            extract_pfx_components(b"pfx_bytes", "wrong_password")

    @patch("shared.crypto.pkcs12")
    def test_extract_missing_components(self, mock_pkcs12):
        """Test error when PFX is missing key or cert."""
        mock_pkcs12.load_key_and_certificates.return_value = (None, None, None)

        with pytest.raises(ValueError, match="Não foi possível extrair"):
            extract_pfx_components(b"pfx_bytes", "password")


class TestExtractCertMetadata:
    """Tests for extract_cert_metadata function."""

    @patch("shared.crypto.x509")
    def test_extract_metadata(self, mock_x509):
        """Test extracting certificate metadata."""
        mock_cert = MagicMock()
        mock_cert.issuer.rfc4514_string.return_value = "CN=Test CA"
        mock_cert.not_valid_before_utc = "2024-01-01T00:00:00Z"
        mock_cert.not_valid_after_utc = "2025-01-01T00:00:00Z"

        mock_x509.load_pem_x509_certificate.return_value = mock_cert

        issuer, valid_from, valid_to = extract_cert_metadata(b"pem_cert")

        assert issuer == "CN=Test CA"
        assert valid_from == "2024-01-01T00:00:00Z"
        assert valid_to == "2025-01-01T00:00:00Z"
