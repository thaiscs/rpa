import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.main import app
from api.admin.routes import router as admin_router


class JobPayload(BaseModel):
    job_type: str
    data: dict


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestAdminRoutes:
    """Tests for admin routes."""

    def test_admin_router_prefix(self):
        """Test that admin router has correct prefix."""
        assert admin_router.prefix == "/admin"

    def test_upload_cert_endpoint_exists(self, client):
        """Test that upload-cert endpoint exists."""
        routes = [route.path for route in app.routes]
        assert any("upload-cert" in route for route in routes)

    def test_send_job_endpoint_exists(self, client):
        """Test that send-job endpoint exists."""
        routes = [route.path for route in app.routes]
        assert any("send-job" in route for route in routes)

    def test_job_payload_validation(self):
        """Test JobPayload schema validation."""
        payload = JobPayload(job_type="test_job", data={"key": "value"})
        assert payload.job_type == "test_job"
        assert payload.data == {"key": "value"}

        with pytest.raises(Exception):
            JobPayload(job_type="test_job")  # Missing 'data'
