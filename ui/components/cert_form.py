import httpx
from nicegui import events, ui

from components.err_dialog import show_error_dialog
from components.err_toast import toast_err
from helpers.validation import validate_tax_id
from theme import Color

API_URL = "http://api:8080/upload-cert"


async def submit_form(state, legal_name, tax_id, cert_name, cert_password, btn=None):
    if not legal_name.value or not tax_id.value or not cert_name.value or not cert_password.value:
        toast_err("Todos os campos são obrigatórios")
        return

    if not state["file"]:
        toast_err("Envie um arquivo .pfx")
        return

    if not validate_tax_id(tax_id.value):
        toast_err("CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos.")
        return

    if btn:
        btn.props("loading disable")
    try:
        uploaded = state["file"]
        form_data = {
            "razao_social": legal_name.value,
            "CNPJ_CPF": tax_id.value,
            "cert_name": cert_name.value,
            "cert_password": cert_password.value,
        }
        file = {
            "cert_file": (
                uploaded.name,
                await uploaded.read(),
                uploaded.content_type or "application/x-pkcs12",
            )
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, data=form_data, files=file)

        if response.status_code == 200:
            with ui.dialog() as dialog, ui.card().classes("items-center p-6"):
                ui.button(icon="close", on_click=dialog.close) \
                    .props("flat round color=gray") \
                    .classes("self-end")
                ui.html('<i class="bi bi-check-circle-fill text-6xl text-positive" aria-hidden="true"></i>')
                ui.label(response.json().get("message", "Sucesso!")).classes("text-h6")
            dialog.open()
            state["file"] = None
        else:
            if response.status_code == 500:
                message = "Erro interno do servidor"
            else:
                try:
                    message = response.json().get("detail", "Erro desconhecido")
                except Exception:
                    message = "Erro desconhecido"
            show_error_dialog(message, title="Não foi possível enviar o certificado")
    finally:
        if btn:
            btn.props(remove="loading disable")


def cert_form():
    state = {"file": None}

    def handle_upload(e: events.UploadEventArguments):
        state["file"] = e
        ui.notify(f"Arquivo '{e.name}' carregado", color="positive")

    def remove_file():
        state["file"] = None
        file_chip.refresh()

    with ui.element("q-card").classes(
        "q-pa-xl shadow-3 rounded-borders bg-white w-full flex flex-col items-center"
    ):
        ui.label("Cadastrar Cliente e Certificado").classes("q-pa-lg text-h4 q-mb-md")

        legal_name = ui.input(
            "Razão Social *",
            validation={"Obrigatório": lambda v: bool(v and v.strip())},
        ).props("filled required lazy-rules").classes("w-full mb-3")

        tax_id = ui.input(
            "CNPJ/CPF *",
            validation={
                "Obrigatório": lambda v: bool(v and v.strip()),
                "CNPJ/CPF inválido — deve conter 11 ou 14 dígitos": lambda v: validate_tax_id(v or ""),
            },
        ).props("filled required lazy-rules").classes("w-full mb-3")

        cert_name = ui.input(
            "Nome do certificado *",
            validation={"Obrigatório": lambda v: bool(v and v.strip())},
        ).props("filled required lazy-rules").classes("w-full mb-3")

        cert_password = ui.input(
            "Senha do certificado *",
            password_toggle_button=True,
            validation={"Obrigatório": lambda v: bool(v and v.strip())},
        ).props("type=password filled required lazy-rules autocomplete=off").classes("w-full mb-3")

        ui.upload(
            label="Arquivo do certificado .pfx",
            on_upload=handle_upload,
            multiple=False,
        ).props('accept=".pfx" auto-upload').classes("w-full")

        @ui.refreshable
        def file_chip():
            if not state["file"]:
                return
            with ui.row().classes("items-center gap-2 p-2 rounded"):
                ui.icon("description")
                ui.label(state["file"].name).classes("font-mono text-sm")
                ui.button(icon="close", on_click=remove_file).props("flat round dense")

        file_chip()

        send_btn = ui.button("Enviar").props("flat").classes(
            f"bg-[{Color.NAVY}] text-white hover:bg-[{Color.GOLD_DEEP}] "
            "transition-all float-right q-pa-md rounded"
        )
        send_btn.on(
            "click",
            lambda: submit_form(state, legal_name, tax_id, cert_name, cert_password, send_btn),
        )
        cert_password.on(
            "keydown.enter",
            lambda: submit_form(state, legal_name, tax_id, cert_name, cert_password, send_btn),
        )
