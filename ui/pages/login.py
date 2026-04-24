from nicegui import ui, app
import httpx
from helpers.parsing import parse_err
from components.err_toast import toast_err
from helpers.auth import Auth

LOGIN_URL = "http://api:8080/auth/jwt/login"


@ui.page("/login")
def login_page():
    with ui.element("div").classes(
        "flex justify-center items-center min-h-screen w-full bg-[#091E2F]"
    ):
        with ui.element("q-card").classes(
            "q-pa-xl shadow-3 rounded-borders bg-white flex flex-col items-center "
            "w-full max-w-md"
        ):
            ui.label("Login").classes("text-h4 q-mb-md text-center")

            email = (
                ui.input("Email")
                .props("type=email filled")
                .classes("w-full q-mb-md")
            )

            password = (
                ui.input("Senha", password_toggle_button=True)
                .props("type=password filled")
                .classes("w-full q-mb-md")
            )

            ui.button(
                "Login",
                on_click=lambda: handle_login(email, password),
            ).props("flat").classes(
                "bg-[#CEB690] text-white hover:bg-[#93713C] "
                "transition-all q-pa-md rounded w-full"
            )

            ui.link("Forgot password?", "/forgot-password").classes("mt-4")
            ui.link("Sign Up", "/signup").classes("mt-1")


async def handle_login(email, password):
    """Send credentials → store token → redirect"""
    if not email.value or not password.value:
        toast_err("Todos os campos são obrigatórios")
        return

    payload = {
        "username": email.value,
        "password": password.value,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(LOGIN_URL, data=payload)

        print("RESP ==> ", response, response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("DATA ==> ", data)
        Auth.login(data["access_token"])
        print(f"Auth.is_logged_in(): {Auth.is_logged_in()}")
        ui.notify("Logged in successfully!", color="green")

        # Trigger redirect AFTER the notify
        ui.timer(0.5, lambda: ui.navigate.to("/cadastrar-certificado"))
    else:
        err = response.json().get("detail")
        message = parse_err(err)

        with ui.dialog() as dialog:
            with ui.card().classes("q-pa-md").style("align-items: flex-end;"):
                ui.button().props("icon=close color=gray flat round").on(
                    "click", dialog.close
                )
                ui.label("ERRO: " + parse_err(message)).classes("text-negative text-h6 q-pb-lg")
                dialog.open()