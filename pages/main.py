from nicegui import ui, events
import httpx
from utils import validate_tax_id

API_URL = "http://api:8080/upload-cert"  # docker compose api service name

uploaded_file = None

def handle_upload(e: events.UploadEventArguments):
    global uploaded_file
    uploaded_file = e.file
    ui.notify(f"Arquivo '{uploaded_file.name}' carregado com sucesso!", color="positive")

def show_err(message: str, duration: int = 3000):
    ui.notify(
        message,
        color="negative",
        position="top",
        timeout=duration,
        transition_show="slide-down",
        transition_hide="slide-up"
    )

def parse_err(message: str):
    if "invalid" in message.lower():
        return "Arquivo ou senha do certificado inválidos."
    elif "missing" in message.lower():
        return "Todos os campos são obrigatórios."
    elif "cnpj/cpf" in message.lower():
        return "CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos."
    else:
        return message  # fallback to original message

async def submit_form(legal_name, tax_id, cert_name, cert_password, cert_file):
    # Validation
    # TODO: hide senha, validate file type
  
    print("DEBUG: form values ->", legal_name.value, tax_id.value, cert_name.value, cert_password.value)
    if not legal_name.value or not tax_id.value or not cert_name.value or not cert_password.value:
        show_err("Todos os campos são obrigatórios")
        return
    
    global uploaded_file
    if not uploaded_file:
        show_err("Envie um arquivo .pfx")
        return

    if not validate_tax_id(tax_id.value):
        show_err("CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos.")
        return

    form_data = {
        "razao_social": legal_name.value,
        "CNPJ_CPF": tax_id.value,
        "cert_name": cert_name.value,
        "cert_password": cert_password.value,
    }

    file = {
        "cert_file": (
            uploaded_file.name, 
            await uploaded_file.read(), 
            uploaded_file.content_type or "application/x-pkcs12"
        )
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, data=form_data, files=file)

    if response.status_code == 200:
      dlg = ui.dialog().props(
          'persistent',             # prevents clicking outside to close
          'max-width=500px',
          'position=top'
      ).classes('q-pa-md')

      dlg.add(ui.label(response.json().get("message", "Sucesso!")).classes("text-positive text-h6"))
      dlg.open()
      uploaded_file = None  # reset
    else:
        message = response.json().get("error", "Erro desconhecido")
        with ui.dialog() as dialog:
          with ui.card().classes("bg-red-3 q-pa-md"):  # red background + padding
            ui.button().classes("float-right").props("icon=close color=white flat round").on("click", lambda: dialog.close())
            ui.label("Erro ao enviar: " + parse_err(message)).classes("text-negative text-h6")
            dialog.open()

with ui.element('q-card').classes('q-pa-lg shadow-3 rounded-borders bg-white'):
    ui.label("Cadastrar Cliente e Certificado").classes("text-h5 q-mb-md")

    legal_name = ui.input("Razão Social*").props("filled").classes("mb-2")
    tax_id = ui.input("CNPJ/CPF").props("filled").classes("mb-2")
    cert_name = ui.input("Nome do certificado").props("filled").classes("mb-2")
    cert_password = ui.input("Senha do certificado").props("filled").classes("mb-2")

    cert_file = ui.upload(
        label="Certificado .pfx",
        on_upload=handle_upload,
        multiple=False
    ).props('accept=".pfx" auto-upload').classes("mb-4")

    ui.button(
        "Enviar",
        color="primary",
        on_click=lambda: submit_form(legal_name, tax_id, cert_name, cert_password, cert_file)
    )

ui.run(host="0.0.0.0", port=3000)