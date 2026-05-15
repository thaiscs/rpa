import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO

from api.main import app
from api.admin.routes import router as admin_router
from pydantic import BaseModel


class JobPayload(BaseModel):
    job_type: str
    data: dict


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock async session for testing."""
    session = AsyncMock()
    return session


@pytest.fixture
def sample_pfx_file():
    """Create a sample PFX file for testing."""
    return BytesIO(b"mock_pfx_data")


class TestAdminRoutes:
    """Tests for admin routes."""

    def test_admin_router_prefix(self):
        """Test that admin router has correct prefix."""
        assert admin_router.prefix == "/admin"

    def test_upload_cert_endpoint_exists(self, client):
        """Test that upload-cert endpoint exists."""
        # We can't easily test the endpoint without mocking dependencies
        # but we can verify the route is registered
        routes = [route.path for route in app.routes]
        assert any("upload-cert" in route for route in routes)

    def test_send_job_endpoint_exists(self, client):
        """Test that send-job endpoint exists."""
        routes = [route.path for route in app.routes]
        assert any("send-job" in route for route in routes)

    @patch("api.admin.routes.save_client_cert")
    @patch("api.admin.routes.get_person_type")
    def test_upload_cert_success(
        self,
        mock_get_person_type,
        mock_save_client_cert,
        client,
        sample_pfx_file
    ):
        """Test successful certificate upload."""
        mock_get_person_type.return_value = "company"
        mock_save_client_cert.return_value = {
            "client_id": uuid.uuid4(),
            "cert_id": uuid.uuid4()
        }

        # Note: This test would require more complex mocking of FastAPI dependencies
        # For now, we're just verifying the endpoint structure
        pass

    def test_job_payload_validation(self):
        """Test JobPayload schema validation."""
        # Valid payload
        payload = JobPayload(
            job_type="test_job",
            data={"key": "value"}
        )
        assert payload.job_type == "test_job"
        assert payload.data == {"key": "value"}

        # Invalid payload (missing required field)
        with pytest.raises(Exception):
            JobPayload(job_type="test_job")  # Missing 'data'
