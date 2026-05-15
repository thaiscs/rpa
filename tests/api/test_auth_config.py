import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from api.auth.config import load_secret, SECRET


class TestLoadSecret:
    """Tests for load_secret function."""

    def test_load_secret_from_file(self, tmp_path):
        """Test loading secret from file."""
        secret_file = tmp_path / "auth.key"
        secret_file.write_text("test_secret_key")

        with patch("api.auth.config.Path", return_value=secret_file):
            result = load_secret()
            assert result == "test_secret_key"

    def test_load_secret_strips_whitespace(self, tmp_path):
        """Test that whitespace is stripped from secret."""
        secret_file = tmp_path / "auth.key"
        secret_file.write_text("  test_secret_key  \n")

        with patch("api.auth.config.Path", return_value=secret_file):
            result = load_secret()
            assert result == "test_secret_key"

    def test_load_secret_missing_file(self):
        """Test error when secret file doesn't exist."""
        with patch("api.auth.config.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            with pytest.raises(RuntimeError, match="Authentication key not found"):
                load_secret()


class TestSecret:
    """Tests for SECRET constant."""

    def test_secret_is_loaded(self):
        """Test that SECRET is loaded at module import."""
        # SECRET is loaded at import time, so we can't easily test it
        # without mocking the file system
        assert SECRET is not None
