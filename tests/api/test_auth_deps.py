import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.auth.deps import current_admin, current_superuser


class TestCurrentAdmin:
    def test_is_not_none(self):
        assert current_admin is not None

    def test_is_callable(self):
        assert callable(current_admin)


class TestCurrentSuperuser:
    def test_is_not_none(self):
        assert current_superuser is not None

    def test_is_callable(self):
        assert callable(current_superuser)


class TestAuthEnforcement:
    """HTTP-level tests verifying auth guards actually block requests."""

    @pytest.fixture
    def client(self):
        from api.main import app
        return TestClient(app, raise_server_exceptions=False)

    @pytest.fixture
    def upload_cert_path(self):
        from api.main import app
        return next(
            (r.path for r in app.routes if hasattr(r, "path") and "upload-cert" in r.path),
            None,
        )

    @pytest.fixture
    def send_job_path(self):
        from api.main import app
        return next(
            (r.path for r in app.routes if hasattr(r, "path") and "send-job" in r.path),
            None,
        )

    def test_upload_cert_without_token_returns_401(self, client, upload_cert_path):
        import io
        response = client.post(
            upload_cert_path,
            data={
                "razao_social": "Empresa",
                "CNPJ_CPF": "12345678000190",
                "cert_name": "cert",
                "cert_password": "pass",
            },
            files={"cert_file": ("t.pfx", io.BytesIO(b"d"), "application/x-pkcs12")},
        )
        assert response.status_code == 401

    def test_send_job_without_token_returns_401(self, client, send_job_path):
        response = client.post(
            send_job_path,
            json={"job_type": "ecac", "data": {}},
        )
        assert response.status_code == 401

    def test_send_job_non_superuser_returns_403(self, send_job_path):
        from api.main import app
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.is_superuser = False

        def raise_forbidden():
            raise HTTPException(status_code=403, detail="Forbidden")

        app.dependency_overrides[current_admin] = lambda: mock_user
        app.dependency_overrides[current_superuser] = raise_forbidden
        c = TestClient(app, raise_server_exceptions=False)

        try:
            response = c.post(send_job_path, json={"job_type": "ecac", "data": {}})
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
