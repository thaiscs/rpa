from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine import Connection

from shared.triggers import create_updated_at_trigger


class TestCreateUpdatedAtTrigger:
    """Tests for create_updated_at_trigger function."""

    @patch("shared.triggers.text")
    def test_creates_trigger_function(self, mock_text):
        """Test that trigger function is created."""
        mock_conn = MagicMock(spec=Connection)
        mock_text.return_value = MagicMock()

        create_updated_at_trigger(mock_conn)

        # Verify that conn.execute was called
        assert mock_conn.execute.call_count >= 2

    @patch("shared.triggers.text")
    def test_attaches_triggers_to_tables(self, mock_text):
        """Test that triggers are attached to tables with updated_at."""
        mock_conn = MagicMock(spec=Connection)
        mock_text.return_value = MagicMock()

        create_updated_at_trigger(mock_conn)

        # Verify SQL was executed
        assert mock_conn.execute.called

    @patch("shared.triggers.text")
    def test_handles_connection_error(self, mock_text):
        """Test that connection errors are handled."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute.side_effect = Exception("Connection error")
        mock_text.return_value = MagicMock()

        with pytest.raises(Exception, match="Connection error"):
            create_updated_at_trigger(mock_conn)
