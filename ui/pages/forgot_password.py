# pages/forgot_password.py
from nicegui import ui
import httpx
from helpers.parsing import parse_err
from components.err_toast import toast_err
from components.err_dialog import show_error_dialog

FORGOT_URL = "http://api:8080/auth/forgot-password"


@ui.page("/forgot-password")
def forgot_page():
    with ui.element("div").classes(
        "flex justify-center items-center min-h-screen w-full bg-[#091E2F]"
    ):
        with ui.element("q-card").classes(
            "q-pa-xl shadow-3 rounded-borders bg-white flex flex-col items-center "
            "w-full max-w-md"
        ):
            ui.label("Recuperar Senha").classes("text-h4 q-mb-md text-center")

            email = ui.input("Email").props("type=email filled").classes("w-full q-mb-md")

            ui.button(
                "Enviar Link de Recuperação",
                on_click=lambda: handle_forgot(email)
            ).props("flat").classes(
                "bg-[#CEB690] text-white hover:bg-[#93713C] "
                "transition-all q-pa-md rounded w-full"
            )

            ui.link("Voltar ao Login", "/login").classes("mt-4")


async def handle_forgot(email):
    if not email.value:
        toast_err("Email é obrigatório")
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(FORGOT_URL, json={"email": email.value})

    print("FORGOT RESP:", response.json(), response.status_code)

    if response.status_code == 202:
        ui.notify("Email enviado! Verifique sua caixa de entrada.", color="green")
    else:
        message = parse_err(response.json().get("detail"))
        show_error_dialog(message)
