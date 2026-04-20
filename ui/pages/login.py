from nicegui import ui, app
import httpx
from components.cert_form import API_URL, parse_err, toast_err

LOGIN_URL = "http://api:8080/auth/jwt/login"  # FastAPI Users endpoint

@ui.page("/login")
def login_form():
  with ui.element('div').classes('flex justify-center items-center min-h-screen w-full bg-[#091E2F]'):

    with ui.element('q-card').classes(
        'q-pa-xl shadow-3 rounded-borders bg-white flex flex-col items-center w-full max-w-md'
    ):
        ui.label("Cadastrar Cliente e Certificado").classes("text-h4 q-mb-md text-center")

        email = ui.input("Email").props("type=email filled").classes("w-full q-mb-md")
        password = ui.input("Senha", password_toggle_button=True).props("type=password filled").classes("w-full q-mb-md")

        ui.button(
            "Login",
            on_click=lambda: submit_form(email, password)
        ).props("flat").classes(
            "bg-[#CEB690] text-white hover:bg-[#93713C] transition-all q-pa-md rounded w-full"
        )
      # ui.link("Forgot password?", "/forgot-password")
      # ui.link("Sign Up", "/signup")


async def submit_form(email, password):
    if not email.value or not password.value:
      toast_err("Todos os campos são obrigatórios")
      return

    form_data = {
                "email": email.value,
                "password": password.value
            }

    async with httpx.AsyncClient() as client:
      response = await client.post(LOGIN_URL, data=form_data)
    print("RESP: ==>", response.json(), response.status_code)
    if response.status_code == 200:
        data = response.json()
        ui.notify("Logged in successfully!", color="green")
        ui.open("/")
        
        # store session
        app.storage.user = {
            "email": email.value,
            "access_token": data["access_token"],
            "token_type": data["token_type"],
        }
    else:
        # extract to error dialog component/helper
        message = response.json().get("detail", "Erro desconhecido")
        with ui.dialog() as dialog:
          with ui.card().classes("q-pa-md").style("align-items: flex-end;"):
            ui.button().props("icon=close color=gray flat round").on("click", lambda: dialog.close())
            ui.label("ERRO: " + parse_err(message)).classes("text-negative text-h6 q-pb-lg")
            dialog.open()
