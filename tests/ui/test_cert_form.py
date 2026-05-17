import sys
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

# Install stub modules for UI-service internal imports before cert_form is imported.
# cert_form.py uses bare `from helpers.x import y` and `from components.x import y`
# which only resolve when the `ui/` directory is on sys.path (as in the running service).
# Stubbing them here lets us import and test the module's logic in isolation.
for _mod in ["helpers", "helpers.validation", "components", "components.err_toast", "components.err_dialog"]:
    sys.modules.setdefault(_mod, MagicMock())

import ui.components.cert_form as cert_form_module
from ui.components.cert_form import handle_upload, submit_form


def _field(value):
    """Build a mock NiceGUI input element with a given .value."""
    f = MagicMock()
    f.value = value
    return f


class TestHandleUpload:
    def setup_method(self):
        cert_form_module.uploaded_file = None

    def test_sets_global_uploaded_file(self):
        mock_file = MagicMock()
        mock_file.name = "test.pfx"
        event = MagicMock()
        event.file = mock_file

        with patch("ui.components.cert_form.ui"):
            handle_upload(event)

        assert cert_form_module.uploaded_file is mock_file

    def test_notifies_with_filename(self):
        mock_file = MagicMock()
        mock_file.name = "empresa.pfx"
        event = MagicMock()
        event.file = mock_file

        with patch("ui.components.cert_form.ui") as mock_ui:
            handle_upload(event)

        notify_msg = mock_ui.notify.call_args[0][0]
        assert "empresa.pfx" in notify_msg

    def test_notification_is_positive(self):
        mock_file = MagicMock()
        mock_file.name = "cert.pfx"
        event = MagicMock()
        event.file = mock_file

        with patch("ui.components.cert_form.ui") as mock_ui:
            handle_upload(event)

        assert mock_ui.notify.call_args[1].get("color") == "positive"


class TestSubmitFormValidation:
    def setup_method(self):
        cert_form_module.uploaded_file = None

    async def test_empty_legal_name_shows_required_toast(self):
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                _field(""), _field("12345678000190"), _field("cert"), _field("pass"), MagicMock()
            )
        mock_toast.assert_called_once()
        assert "obrigatórios" in mock_toast.call_args[0][0]

    async def test_empty_tax_id_shows_required_toast(self):
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                _field("Empresa"), _field(""), _field("cert"), _field("pass"), MagicMock()
            )
        mock_toast.assert_called_once()
        assert "obrigatórios" in mock_toast.call_args[0][0]

    async def test_empty_cert_name_shows_required_toast(self):
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                _field("Empresa"), _field("12345678000190"), _field(""), _field("pass"), MagicMock()
            )
        mock_toast.assert_called_once()

    async def test_empty_password_shows_required_toast(self):
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                _field("Empresa"), _field("12345678000190"), _field("cert"), _field(""), MagicMock()
            )
        mock_toast.assert_called_once()

    async def test_missing_file_shows_pfx_toast(self):
        # All fields filled, but no file uploaded
        cert_form_module.uploaded_file = None
        with patch("ui.components.cert_form.toast_err") as mock_toast:
            await submit_form(
                _field("Empresa"), _field("12345678000190"), _field("cert"), _field("pass"), MagicMock()
            )
        mock_toast.assert_called_with("Envie um arquivo .pfx")

    async def test_invalid_tax_id_shows_cnpj_toast(self):
        cert_form_module.uploaded_file = MagicMock()
        with patch("ui.components.cert_form.toast_err") as mock_toast, \
             patch("ui.components.cert_form.validate_tax_id", return_value=False):
            await submit_form(
                _field("Empresa"), _field("123"), _field("cert"), _field("pass"), MagicMock()
            )
        mock_toast.assert_called_once()
        assert "CNPJ" in mock_toast.call_args[0][0]

    async def test_validation_does_not_call_api_on_failure(self):
        cert_form_module.uploaded_file = None
        mock_client_cls = MagicMock()

        with patch("ui.components.cert_form.toast_err"), \
             patch("ui.components.cert_form.httpx.AsyncClient", mock_client_cls):
            await submit_form(
                _field(""), _field("12345678000190"), _field("cert"), _field("pass"), MagicMock()
            )

        mock_client_cls.assert_not_called()


class TestSubmitFormApiCall:
    def setup_method(self):
        cert_form_module.uploaded_file = None

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
        cert_form_module.uploaded_file = self._make_uploaded_file()
        mock_cls, mock_inner = self._make_httpx_client()

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                _field("Empresa"), _field("12345678000190"), _field("certificado"), _field("senha"), MagicMock()
            )

        mock_inner.post.assert_called_once()
        _, kw = mock_inner.post.call_args
        assert kw["data"]["razao_social"] == "Empresa"
        assert kw["data"]["CNPJ_CPF"] == "12345678000190"
        assert kw["data"]["cert_name"] == "certificado"
        assert kw["data"]["cert_password"] == "senha"

    async def test_successful_response_opens_success_dialog(self):
        cert_form_module.uploaded_file = self._make_uploaded_file()
        mock_cls, _ = self._make_httpx_client(200, {"message": "Salvo!"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui") as mock_ui:
            await submit_form(
                _field("E"), _field("12345678000190"), _field("c"), _field("p"), MagicMock()
            )

        mock_ui.dialog.assert_called()

    async def test_successful_response_resets_uploaded_file(self):
        cert_form_module.uploaded_file = self._make_uploaded_file()
        mock_cls, _ = self._make_httpx_client(200)

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                _field("E"), _field("12345678000190"), _field("c"), _field("p"), MagicMock()
            )

        assert cert_form_module.uploaded_file is None

    async def test_500_response_shows_server_error(self):
        cert_form_module.uploaded_file = self._make_uploaded_file()
        mock_cls, _ = self._make_httpx_client(500, {"detail": "Internal error"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.show_error_dialog") as mock_dialog, \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                _field("E"), _field("12345678000190"), _field("c"), _field("p"), MagicMock()
            )

        # 500 branch shows a generic message, not show_error_dialog
        mock_dialog.assert_not_called()

    async def test_non_500_error_calls_show_error_dialog(self):
        cert_form_module.uploaded_file = self._make_uploaded_file()
        mock_cls, _ = self._make_httpx_client(400, {"detail": "Bad cert password"})

        with patch("ui.components.cert_form.httpx.AsyncClient", mock_cls), \
             patch("ui.components.cert_form.validate_tax_id", return_value=True), \
             patch("ui.components.cert_form.show_error_dialog") as mock_dialog, \
             patch("ui.components.cert_form.ui"):
            await submit_form(
                _field("E"), _field("12345678000190"), _field("c"), _field("p"), MagicMock()
            )

        mock_dialog.assert_called_once_with("Bad cert password")
