from nicegui import ui, app
import httpx
from helpers.parsing import parse_err
from components.err_toast import toast_err
from components.err_dialog import show_error_dialog
from helpers.auth import Auth

LOGIN_URL = "http://api:8080/auth/jwt/login"


@ui.page("/login")
def login_page():
    with ui.element("div").classes(
        "flex justify-center items-center min-h-screen w-full bg-[#091E2F]"
    ):
        with ui.element("q-card").classes(
            "q-pa-md sm:q-pa-xl shadow-3 rounded-borders bg-white flex flex-col "
            "items-center w-full max-w-md mx-4"
        ):
            ui.label("Entrar").classes("text-h4 q-mb-md text-center")

            email = (
                ui.input("Email")
                .props("type=email filled autocomplete=email")
                .classes("w-full q-mb-md")
            )

            password = (
                ui.input("Senha", password_toggle_button=True)
                .props("type=password filled autocomplete=current-password")
                .classes("w-full q-mb-md")
            )

            login_btn = ui.button("Entrar").props("flat").classes(
                "bg-[#CEB690] text-white hover:bg-[#93713C] "
                "transition-all q-pa-md rounded w-full"
            )
            login_btn.on("click", lambda: handle_login(login_btn, email, password))
            password.on("keydown.enter", lambda: handle_login(login_btn, email, password))

            ui.link("Esqueceu a senha?", "/forgot-password").classes("mt-4")
            ui.link("Criar conta", "/signup").classes("mt-1")


async def handle_login(btn, email, password):
    if not email.value or not password.value:
        toast_err("Todos os campos são obrigatórios")
        return

    btn.props("loading disable")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(LOGIN_URL, data={
                "username": email.value,
                "password": password.value,
            })

        if response.status_code == 200:
            data = response.json()
            await Auth.login(data["access_token"])
            ui.notify("Sessão iniciada", color="green")
            ui.timer(0.5, lambda: ui.navigate.to("/cadastrar-certificado"))
        else:
            err = response.json().get("detail")
            show_error_dialog(parse_err(err), title="Não foi possível entrar")
    finally:
        btn.props(remove="loading disable")
