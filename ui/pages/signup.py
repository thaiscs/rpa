from nicegui import ui, app
import httpx
from helpers.parsing import parse_err
from components.err_dialog import show_error_dialog
from components.err_toast import toast_err

SIGNUP_URL = "http://api:8080/auth/register"   # FastAPI Users register endpoint


@ui.page("/signup")
def signup_page():
    with ui.element("div").classes(
        "flex justify-center items-center min-h-screen w-full bg-[#091E2F]"
    ):
        with ui.element("q-card").classes(
            "q-pa-xl shadow-3 rounded-borders bg-white flex flex-col items-center "
            "w-full max-w-md"
        ):
            ui.label("Sign Up").classes("text-h4 q-mb-md text-center")

            email = ui.input("Email").props("type=email filled").classes("w-full q-mb-md")
            password = (
                ui.input("Senha", password_toggle_button=True)
                .props("type=password filled")
                .classes("w-full q-mb-md")
            )
            confirm = (
                ui.input("Confirmar Senha", password_toggle_button=True)
                .props("type=password filled")
                .classes("w-full q-mb-md")
            )

            ui.button(
                "Criar Conta",
                on_click=lambda: handle_signup(email, password, confirm)
            ).props("flat").classes(
                "bg-[#CEB690] text-white hover:bg-[#93713C] "
                "transition-all q-pa-md rounded w-full"
            )

            ui.link("Já tem conta? Faça login", "/login").classes("mt-4")


async def handle_signup(email, password, confirm):
    if not email.value or not password.value or not confirm.value:
        toast_err("Todos os campos são obrigatórios")
        return

    if password.value != confirm.value:
        toast_err("Senhas não coincidem")
        return

    payload = {
        "email": email.value,
        "password": password.value,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(SIGNUP_URL, json=payload)

    print("SIGNUP RESP:", response.json(), response.status_code)

    if response.status_code == 201:
        ui.notify("Conta criada com sucesso!", color="green")
        ui.timer(0.5, lambda: ui.navigate.to("/cadastrar-certificado"))

    else:
        message = parse_err(response.json().get("detail"))
        show_error_dialog(message)
