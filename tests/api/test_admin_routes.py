import io
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.main import app
from api.auth.deps import current_admin, current_superuser
from shared.db import get_db


def _find_route(keyword):
    return next(
        (r.path for r in app.routes if hasattr(r, "path") and keyword in r.path),
        None,
    )


def make_mock_user(is_superuser=False):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.is_active = True
    user.is_superuser = is_superuser
    return user


@pytest.fixture
def admin_client():
    mock_user = make_mock_user(is_superuser=False)
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[current_admin] = lambda: mock_user
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def superuser_client():
    mock_user = make_mock_user(is_superuser=True)
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[current_admin] = lambda: mock_user
    app.dependency_overrides[current_superuser] = lambda: mock_user
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def non_superuser_client():
    """Authenticated as regular user but superuser dep raises 403."""
    mock_user = make_mock_user(is_superuser=False)
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    def raise_forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    app.dependency_overrides[current_admin] = lambda: mock_user
    app.dependency_overrides[current_superuser] = raise_forbidden
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


class TestAdminRouterConfig:
    def test_admin_router_prefix(self):
        from api.admin.routes import router as admin_router
        assert admin_router.prefix == "/admin"

    def test_upload_cert_endpoint_registered(self):
        assert _find_route("upload-cert") is not None

    def test_send_job_endpoint_registered(self):
        assert _find_route("send-job") is not None

    def test_job_payload_valid(self):
        from api.admin.routes import JobPayload
        payload = JobPayload(job_type="ecac", data={"client_id": "123"})
        assert payload.job_type == "ecac"
        assert payload.data == {"client_id": "123"}

    def test_job_payload_missing_data_raises(self):
        from api.admin.routes import JobPayload
        with pytest.raises(Exception):
            JobPayload(job_type="ecac")


class TestUploadCertEndpoint:
    @patch("api.admin.routes.save_client_cert", new_callable=AsyncMock)
    @patch("api.admin.routes.get_person_type", return_value="PJ")
    def test_success_returns_200_with_fields(self, _mock_ptype, mock_save, admin_client):
        mock_save.return_value = {
            "client_id": str(uuid.uuid4()),
            "cert_id": str(uuid.uuid4()),
        }
        response = admin_client.post(
            _find_route("upload-cert"),
            data={
                "razao_social": "Empresa Teste LTDA",
                "CNPJ_CPF": "12345678000190",
                "cert_name": "certificado",
                "cert_password": "senha123",
            },
            files={"cert_file": ("test.pfx", io.BytesIO(b"pfx_bytes"), "application/x-pkcs12")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["razao_social"] == "Empresa Teste LTDA"
        assert body["cnpj_cpf"] == "12345678000190"
        assert body["cert_name"] == "certificado"

    @patch("api.admin.routes.save_client_cert", new_callable=AsyncMock)
    @patch("api.admin.routes.get_person_type", return_value="PJ")
    def test_calls_save_with_correct_args(self, _mock_ptype, mock_save, admin_client):
        mock_save.return_value = {"client_id": str(uuid.uuid4()), "cert_id": str(uuid.uuid4())}
        admin_client.post(
            _find_route("upload-cert"),
            data={
                "razao_social": "Empresa",
                "CNPJ_CPF": "12345678000190",
                "cert_name": "cert",
                "cert_password": "pass",
            },
            files={"cert_file": ("test.pfx", io.BytesIO(b"data"), "application/x-pkcs12")},
        )
        mock_save.assert_called_once()
        kw = mock_save.call_args.kwargs
        assert kw["legal_name"] == "Empresa"
        assert kw["tax_id"] == "12345678000190"
        assert kw["cert_name"] == "cert"
        assert kw["cert_password"] == "pass"
        assert kw["cert_bytes"] == b"data"

    @patch("api.admin.routes.save_client_cert", new_callable=AsyncMock)
    @patch("api.admin.routes.get_person_type", return_value="PJ")
    def test_save_error_returns_500_with_detail(self, _mock_ptype, mock_save, admin_client):
        mock_save.side_effect = ValueError("Invalid PFX password")
        response = admin_client.post(
            _find_route("upload-cert"),
            data={
                "razao_social": "Empresa",
                "CNPJ_CPF": "12345678000190",
                "cert_name": "cert",
                "cert_password": "wrong",
            },
            files={"cert_file": ("test.pfx", io.BytesIO(b"data"), "application/x-pkcs12")},
        )
        assert response.status_code == 500
        assert "Invalid PFX password" in response.json()["detail"]

    def test_unauthenticated_returns_401(self, unauthenticated_client):
        response = unauthenticated_client.post(
            _find_route("upload-cert"),
            data={
                "razao_social": "E",
                "CNPJ_CPF": "12345678000190",
                "cert_name": "c",
                "cert_password": "p",
            },
            files={"cert_file": ("t.pfx", io.BytesIO(b"d"), "application/x-pkcs12")},
        )
        assert response.status_code == 401


class TestSendJobEndpoint:
    def test_superuser_success_returns_queued(self, superuser_client):
        response = superuser_client.post(
            _find_route("send-job"),
            json={"job_type": "ecac_notifications", "data": {"client_id": "abc"}},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "queued"

    def test_superuser_response_includes_payload(self, superuser_client):
        response = superuser_client.post(
            _find_route("send-job"),
            json={"job_type": "rpa_task", "data": {"key": "val"}},
        )
        assert response.status_code == 200
        assert response.json()["job"]["job_type"] == "rpa_task"

    def test_non_superuser_returns_403(self, non_superuser_client):
        response = non_superuser_client.post(
            _find_route("send-job"),
            json={"job_type": "ecac", "data": {}},
        )
        assert response.status_code == 403

    def test_unauthenticated_returns_401(self, unauthenticated_client):
        response = unauthenticated_client.post(
            _find_route("send-job"),
            json={"job_type": "ecac", "data": {}},
        )
        assert response.status_code == 401

    def test_missing_data_field_returns_422(self, superuser_client):
        response = superuser_client.post(
            _find_route("send-job"),
            json={"job_type": "ecac"},
        )
        assert response.status_code == 422
