from nicegui import ui, events
import httpx
from utils import validate_tax_id

API_URL = "http://api:8080/upload-cert"  # docker compose api service name

uploaded_file = None

def handle_upload(e: events.UploadEventArguments):
    global uploaded_file
    uploaded_file = e.file
    ui.notify(f"Arquivo '{uploaded_file.name}' carregado com sucesso!", color="positive")

def toast_err(message: str, duration: int = 3000):
    ui.notify(
        message,
        color="negative",
        position="top",
        timeout=duration,
        transition_show="slide-down",
        transition_hide="slide-up"
    )

def parse_err(message: str | dict) -> str:
    # If message is a dict, try to extract a meaningful string
    if isinstance(message, dict):
        # Common key 'detail', fallback to first value or empty string
        message_text = message.get("detail") or next(iter(message.values()), "")
    else:
        message_text = message

    # Normalize to lowercase for keyword checks
    lower_msg = message_text.lower()

    if "invalid" in lower_msg:
        return "Arquivo ou senha do certificado inválidos."
    elif "missing" in lower_msg:
        return "Todos os campos são obrigatórios."
    elif "cnpj/cpf" in lower_msg:
        return "CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos."
    
    return message_text  # fallback

async def submit_form(legal_name, tax_id, cert_name, cert_password, cert_file):
    # Validation
    # TODO: extract form modules
    print("DEBUG: form values ->", legal_name.value)

    if not legal_name.value or not tax_id.value or not cert_name.value or not cert_password.value:
        toast_err("Todos os campos são obrigatórios")
        return
    
    global uploaded_file
    if not uploaded_file:
        toast_err("Envie um arquivo .pfx")
        return

    if not validate_tax_id(tax_id.value):
        toast_err("CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos.")
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
    print("RESP: ==>", response.json(), response.status_code)
    if response.status_code == 200:
        # extract to success dialog component/helper
        with ui.dialog() as dialog:
          with ui.card().style("align-items: center; padding: 24px;"):
            ui.button().props("icon=close color=gray flat round").style("align-self: flex-end;").on("click", lambda: dialog.close())
            ui.label(response.json().get("message", "Sucesso!")).classes("text-h6 q-pb-lg")
            ui.html(f'<i class="bi bi-check-circle-fill text-6xl text-positive"></i>')
            dialog.open()
          uploaded_file = None  # reset
    else:
        message = response.json().get("detail", "Erro desconhecido")
        # extract to failure dialog component/helper
        with ui.dialog() as dialog:
          with ui.card().classes("q-pa-md").style("align-items: flex-end;"):
            ui.button().props("icon=close color=gray flat round").on("click", lambda: dialog.close())
            ui.label("ERRO: " + parse_err(message)).classes("text-negative text-h6 q-pb-lg")
            dialog.open()

def cert_form():
    with ui.element("q-card").classes("q-pa-xl shadow-3 rounded-borders bg-white w-full display-flex flex-column items-center"):
        ui.label("Cadastrar Cliente e Certificado").classes("q-pa-lg text-h4 q-mb-md")
        # TODO: COLOR THEMING https://nicegui.io/documentation/section_styling_appearance
        ui.add_css("""
        .q-field--filled q-field__control::after {
            color: #CEB690 !important;          /* gold text */
            border-bottom: 2px solid #CEB690 !important;  /* gold underline */
            font-size: 60px !important;
        }
        .q-field__control {
            color: #091E2F !important;  /* gold text for filled fields */
        }
        .q-uploader__header {
            background-color: #CEB690 !important;  /* dark blue header */
        }
        .q-field {
            font-size: 20px !important;
        }
        """, shared=True)
        legal_name = ui.input("Razão Social *") \
            .props("filled flat") \
            .classes(
                "m-4 w-[80%] text-gray-100 placeholder-gray-300 bg-white hover:bg-[#0B2A43] focus:bg-[#0B2A43] focus:text-white focus:placeholder-gray-400 transition-all rounded"
            )
        tax_id = ui.input("CNPJ/CPF *").props("filled").classes("m-4 w-[80%] rounded")
        cert_name = ui.input("Nome do certificado *").props("filled").classes("m-4 w-[80%] rounded")
        cert_password = (
            ui.input("Senha do certificado *", password_toggle_button=True)
            .props("type=password filled")
            .classes("m-4 w-[80%] rounded")
        )
        cert_file = ui.upload(
            label="Arquivo do certificado .pfx",
            on_upload=handle_upload,
            multiple=False
        ).props('accept=".pfx" auto-upload').classes("m-4 text-center text-h6")

        with cert_file.add_slot('list'):
            ui.icon('cloud_upload').classes("text-6xl text-[#CEB690]")
        
        ui.button(
            "Enviar",
            on_click=lambda: submit_form(legal_name, tax_id, cert_name, cert_password, cert_file)
        ).props("flat").classes("bg-[#091E2F] text-white hover:bg-[#93713C] transition-all float-right q-pa-md rounded text-subtitle-1")
