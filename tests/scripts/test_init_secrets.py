from unittest.mock import patch

from scripts.init_secrets import ensure


class TestEnsure:
    """Tests for ensure function."""

    def test_ensure_creates_new_key(self, tmp_path):
        """Test that ensure creates a new key if file doesn't exist."""
        key_file = tmp_path / "test.key"

        with patch("scripts.init_secrets.Fernet") as mock_fernet:
            mock_fernet.generate_key.return_value = b"test_key"

            ensure(key_file)

            assert key_file.exists()
            assert key_file.read_bytes() == b"test_key"

    def test_ensure_skips_existing_file(self, tmp_path):
        """Test that ensure skips if file exists with content."""
        key_file = tmp_path / "test.key"
        key_file.write_bytes(b"existing_key")

        with patch("scripts.init_secrets.Fernet") as mock_fernet:
            mock_fernet.generate_key.return_value = b"new_key"

            ensure(key_file)

            # Should not overwrite existing key
            assert key_file.read_bytes() == b"existing_key"

    def test_ensure_creates_if_empty(self, tmp_path):
        """Test that ensure creates key if file is empty."""
        key_file = tmp_path / "test.key"
        key_file.write_bytes(b"")

        with patch("scripts.init_secrets.Fernet") as mock_fernet:
            mock_fernet.generate_key.return_value = b"new_key"

            ensure(key_file)

            assert key_file.read_bytes() == b"new_key"
