import json
from unittest.mock import MagicMock, patch

import pytest

from api.services.queue_service import publish_job


class TestPublishJob:
    """Tests for publish_job function."""

    @patch("api.services.queue_service.pika.BlockingConnection")
    @patch("api.services.queue_service.pika.ConnectionParameters")
    def test_publish_job_success(self, mock_connection_params, mock_blocking_connection):
        """Test successful job publishing."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_blocking_connection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        payload = {"job_type": "test", "data": {"key": "value"}}
        publish_job(payload)

        # Verify connection was created
        mock_connection_params.assert_called_once_with("rabbitmq")
        mock_blocking_connection.assert_called_once()

        # Verify queue was declared
        mock_channel.queue_declare.assert_called_once_with(queue="jobs")

        # Verify message was published
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        assert call_args[1]["routing_key"] == "jobs"
        assert json.loads(call_args[1]["body"]) == payload

        # Verify connection was closed
        mock_connection.close.assert_called_once()

    @patch("api.services.queue_service.pika.BlockingConnection")
    @patch("api.services.queue_service.pika.ConnectionParameters")
    def test_publish_job_serializes_payload(self, mock_connection_params, mock_blocking_connection):
        """Test that payload is serialized to JSON."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_blocking_connection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        payload = {"job_type": "test", "data": {"key": "value"}}
        publish_job(payload)

        # Get the published body
        call_args = mock_channel.basic_publish.call_args
        body = call_args[1]["body"]

        # Verify it's valid JSON
        parsed = json.loads(body)
        assert parsed == payload

    @patch("api.services.queue_service.pika.BlockingConnection")
    @patch("api.services.queue_service.pika.ConnectionParameters")
    def test_publish_job_connection_error(self, mock_connection_params, mock_blocking_connection):
        """Test that connection errors are raised."""
        mock_blocking_connection.side_effect = Exception("Connection failed")

        payload = {"job_type": "test", "data": {"key": "value"}}

        with pytest.raises(Exception, match="Connection failed"):
            publish_job(payload)
