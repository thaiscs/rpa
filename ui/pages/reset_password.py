from nicegui import ui
import httpx
from helpers.parsing import parse_err
from components.err_toast import toast_err

API_URL = "http://api:8080/auth/reset-password"

@ui.page("/reset-password")
def reset_password(token: str):
    with ui.column().classes("items-center w-full max-w-md mx-auto mt-20"):
        ui.label("Alterar Senha").classes("text-h4 mb-4")

        new_password = ui.input("Nova Senha", password_toggle_button=True) \
            .props("type=password filled").classes("w-full")

        ui.button(
            "Alterar",
            on_click=lambda: submit_reset(new_password, token)
        ).classes("bg-[#CEB690] text-white w-full q-mt-md")

async def submit_reset(new_password, token):
    if not new_password.value:
        toast_err("Senha é obrigatória")
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_URL,
            json={"token": token, "password": new_password.value}
        )

    if response.status_code == 200:
        ui.notify("Senha alterada!", color="green")
        ui.open("/login")
    else:
        ui.notify(parse_err(response.json()), color="negative")