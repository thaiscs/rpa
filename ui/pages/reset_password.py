import httpx
from nicegui import ui

from components.err_dialog import show_error_dialog
from components.err_toast import toast_err
from helpers.parsing import parse_err
from theme import auth_card, auth_card_wrapper, primary_button

API_URL = "http://api:8080/auth/reset-password"


@ui.page("/reset-password")
def reset_password(token: str):
    with auth_card_wrapper(), auth_card():
        ui.label("Alterar senha").classes("text-h4 q-mb-md text-center")

        new_password = ui.input("Nova senha", password_toggle_button=True) \
                .props("type=password filled autocomplete=new-password") \
                .classes("w-full q-mb-md")

        confirm = ui.input("Confirmar nova senha", password_toggle_button=True) \
                .props("type=password filled autocomplete=new-password") \
                .classes("w-full q-mb-md")

        submit_btn = primary_button("Alterar", full_width=True)
        submit_btn.on("click", lambda: submit_reset(submit_btn, new_password, confirm, token))
        confirm.on("keydown.enter", lambda: submit_reset(submit_btn, new_password, confirm, token))


async def submit_reset(btn, new_password, confirm, token):
    if not new_password.value:
        toast_err("Senha é obrigatória")
        return
    if new_password.value != confirm.value:
        toast_err("Senhas não coincidem")
        return

    btn.props("loading disable")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL, json={"token": token, "password": new_password.value}
            )
        if response.status_code == 200:
            ui.notify("Senha alterada", color="green")
            ui.navigate.to("/login")
        else:
            show_error_dialog(parse_err(response.json()))
    finally:
        btn.props(remove="loading disable")
