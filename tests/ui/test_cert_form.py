import sys
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

# Install stub modules for UI-service internal imports before cert_form is imported.
for _mod in [
    "helpers", "helpers.validation",
    "components", "components.err_toast", "components.err_dialog",
    "theme",
]:
    sys.modules.setdefault(_mod, MagicMock())

from ui.components.cert_form import submit_form


def _field(value):
    """Build a mock NiceGUI input element with a given .value."""
    f = MagicMock()
    f.value = value
    return f


class TestSubmitFormValidation:
    async def test_empty_legal_name_shows_required_toast(self):
        state = {"file": None}
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                state, _field(""), _field("12345678000190"), _field("cert"), _field("pass")
            )
        mock_toast.assert_called_once()
        assert "obrigatórios" in mock_toast.call_args[0][0]

    async def test_empty_tax_id_shows_required_toast(self):
        state = {"file": None}
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                state, _field("Empresa"), _field(""), _field("cert"), _field("pass")
            )
        mock_toast.assert_called_once()
        assert "obrigatórios" in mock_toast.call_args[0][0]

    async def test_empty_cert_name_shows_required_toast(self):
        state = {"file": None}
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                state, _field("Empresa"), _field("12345678000190"), _field(""), _field("pass")
            )
        mock_toast.assert_called_once()

    async def test_empty_password_shows_required_toast(self):
        state = {"file": None}
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                state, _field("Empresa"), _field("12345678000190"), _field("cert"), _field("")
            )
        mock_toast.assert_called_once()

    async def test_missing_file_shows_pfx_toast(self):
        state = {"file": None}
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                state, _field("Empresa"), _field("12345678000190"), _field("cert"), _field("pass")
            )
        mock_toast.assert_called_with("Envie um arquivo .pfx")

    async def test_invalid_tax_id_shows_cnpj_toast(self):
        state = {"file": MagicMock()}
        with patch("ui.components.cert_form.toast_err") as mock_toast, \
             patch("ui.components.cert_form.validate_tax_id", return_value=False):
            await submit_form(
                state, _field("Empresa"), _field("123"), _field("cert"), _field("pass")
            )
        mock_toast.assert_called_once()
        assert "CNPJ" in mock_toast.call_args[0][0]

    async def test_validation_does_not_call_api_on_failure(self):
        state = {"file": None}
        mock_client_cls = MagicMock()

        with patch("ui.components.cert_form.toast_err"), \
             patch("ui.components.cert_form.httpx.AsyncClient", mock_client_cls):
            await submit_form(
                state, _field(""), _field("12345678000190"), _field("cert"), _field("pass")
            )

        mock_client_cls.assert_not_called()


class TestSubmitFormApiCall:
    def _make_uploaded_file(self, name="cert.pfx", content=b"pfx_bytes"):
        f = AsyncMock()
        f.name = name
        f.read = AsyncMock(return_value=content)
        f.content_type = "application/x-pkcs12"
        return f

    def _make_httpx_client(self, status_code=200, json_body=None):
        if json_body is None:
            json_body = {"message": "Sucesso!"}
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_body

        inner = AsyncMock()
        inner.post = AsyncMock(return_value=mock_response)

        cls = MagicMock()
        cls.return_value.__aenter__ = AsyncMock(return_value=inner)
        cls.return_value.__aexit__ = AsyncMock(return_value=False)
        return cls, inner

    async def test_successful_post_sends_all_form_fields(self):
        state = {"file": self._make_uploaded_file()}
        mock_cls, mock_inner = self._make_httpx_client()

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                state, _field("Empresa"), _field("12345678000190"), _field("certificado"), _field("senha")
            )

        mock_inner.post.assert_called_once()
        _, kw = mock_inner.post.call_args
        assert kw["data"]["razao_social"] == "Empresa"
        assert kw["data"]["CNPJ_CPF"] == "12345678000190"
        assert kw["data"]["cert_name"] == "certificado"
        assert kw["data"]["cert_password"] == "senha"

    async def test_successful_response_opens_success_dialog(self):
        state = {"file": self._make_uploaded_file()}
        mock_cls, _ = self._make_httpx_client(200, {"message": "Salvo!"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui") as mock_ui:
            await submit_form(
                state, _field("E"), _field("12345678000190"), _field("c"), _field("p")
            )

        mock_ui.dialog.assert_called()

    async def test_successful_response_resets_state_file(self):
        state = {"file": self._make_uploaded_file()}
        mock_cls, _ = self._make_httpx_client(200)

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                state, _field("E"), _field("12345678000190"), _field("c"), _field("p")
            )

        assert state["file"] is None

    async def test_500_response_calls_show_error_dialog(self):
        state = {"file": self._make_uploaded_file()}
        mock_cls, _ = self._make_httpx_client(500, {"detail": "Internal error"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.show_error_dialog") as mock_dialog, \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                state, _field("E"), _field("12345678000190"), _field("c"), _field("p")
            )

        mock_dialog.assert_called_once_with(
            "Erro interno do servidor",
            title="Não foi possível enviar o certificado",
        )

    async def test_non_500_error_calls_show_error_dialog(self):
        state = {"file": self._make_uploaded_file()}
        mock_cls, _ = self._make_httpx_client(400, {"detail": "Bad cert password"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.show_error_dialog") as mock_dialog, \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                state, _field("E"), _field("12345678000190"), _field("c"), _field("p")
            )

        mock_dialog.assert_called_once_with(
            "Bad cert password",
            title="Não foi possível enviar o certificado",
        )
