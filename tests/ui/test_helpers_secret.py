import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ui.helpers.secret import Secrets


class TestSecrets:
    """Tests for Secrets class."""

    def test_storage_key_loads_from_file(self, tmp_path):
        """Test that storage_key loads from file."""
        key_file = tmp_path / "storage.key"
        key_file.write_text("test_storage_key")

        with patch("ui.helpers.secret.Path", return_value=key_file):
            result = Secrets.storage_key()
            assert result == "test_storage_key"

    def test_storage_key_strips_whitespace(self, tmp_path):
        """Test that storage_key strips whitespace."""
        key_file = tmp_path / "storage.key"
        key_file.write_text("  test_storage_key  \n")

        with patch("ui.helpers.secret.Path", return_value=key_file):
            result = Secrets.storage_key()
            assert result == "test_storage_key"

    def test_storage_key_missing_file(self):
        """Test error when storage key file doesn't exist."""
        with patch("ui.helpers.secret.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            with pytest.raises(RuntimeError, match="Storage key not found"):
                Secrets.storage_key()
