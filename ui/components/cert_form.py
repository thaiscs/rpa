import httpx
from nicegui import events, ui

from components.err_dialog import show_error_dialog
from components.err_toast import toast_err
from helpers.validation import validate_tax_id
from theme import Color, field, primary_button

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
            if state.get("refresh_chip"):
                state["refresh_chip"]()
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
    state: dict = {"file": None, "refresh_chip": None}

    def handle_upload(e: events.UploadEventArguments):
        state["file"] = e
        if state.get("refresh_chip"):
            state["refresh_chip"]()
        ui.notify(f"Arquivo '{e.name}' carregado", color="positive")

    def remove_file():
        state["file"] = None
        if state.get("refresh_chip"):
            state["refresh_chip"]()

    # Page header — matches the pattern used by dashboard/clients/ecac pages
    with ui.column().classes("gap-1"):
        ui.label("Cadastrar Cliente e Certificado").classes(
            f"text-3xl font-bold text-[{Color.INK}]"
        )
        ui.label("Preencha os dados do cliente e envie o arquivo .pfx").classes(
            f"text-sm text-[{Color.INK_SOFT}]"
        )

    # Form card — constrained max width, standard card styling (not q-pa-xl + centered)
    with ui.card().classes("w-full max-w-3xl p-6 sm:p-8 gap-4"):
        # Two-column on desktop, single column on mobile (responsive grid)
        with ui.element("div").classes(
            "grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-0 w-full"
        ):
            legal_name = field(
                "Razão Social",
                required=True,
                **{"Obrigatório": lambda v: bool(v and v.strip())},
            )

            tax_id = field(
                "CNPJ/CPF",
                required=True,
                **{
                    "Obrigatório": lambda v: bool(v and v.strip()),
                    "CNPJ/CPF inválido — deve conter 11 ou 14 dígitos":
                        lambda v: validate_tax_id(v or ""),
                },
            )

            cert_name = field(
                "Nome do certificado",
                required=True,
                **{"Obrigatório": lambda v: bool(v and v.strip())},
            )

            cert_password = field(
                "Senha do certificado",
                password=True,
                required=True,
                autocomplete="off",
                **{"Obrigatório": lambda v: bool(v and v.strip())},
            )

        # Upload section — labeled and visually distinct
        with ui.column().classes("w-full gap-2"):
            ui.label("Arquivo do certificado (.pfx)").classes(
                f"text-sm font-medium text-[{Color.INK}]"
            )
            ui.upload(
                on_upload=handle_upload,
                multiple=False,
            ).props('accept=".pfx" auto-upload flat bordered').classes("w-full")

            @ui.refreshable
            def file_chip():
                if not state["file"]:
                    ui.label("Nenhum arquivo selecionado").classes(
                        f"text-xs text-[{Color.INK_MUTE}]"
                    )
                    return
                with ui.row().classes(
                    f"items-center gap-2 p-2 rounded bg-[{Color.SURFACE_ALT}] w-fit"
                ):
                    ui.html(
                        f'<i class="bi bi-file-earmark-lock text-[{Color.NAVY}]" '
                        f'aria-hidden="true"></i>'
                    )
                    ui.label(state["file"].name).classes("font-mono text-sm")
                    ui.button(icon="close", on_click=remove_file) \
                        .props("flat round dense") \
                        .tooltip("Remover arquivo")

            state["refresh_chip"] = file_chip.refresh
            file_chip()

        # Submit row — right-aligned on desktop, full-width button on mobile
        with ui.row().classes("w-full justify-end mt-2"):
            send_btn = primary_button("Enviar certificado")

        send_btn.on(
            "click",
            lambda: submit_form(state, legal_name, tax_id, cert_name, cert_password, send_btn),
        )
        cert_password.on(
            "keydown.enter",
            lambda: submit_form(state, legal_name, tax_id, cert_name, cert_password, send_btn),
        )
