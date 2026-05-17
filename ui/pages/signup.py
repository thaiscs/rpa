from nicegui import ui
import httpx
from helpers.parsing import parse_err
from components.err_dialog import show_error_dialog
from components.err_toast import toast_err
from theme import primary_button, auth_card_wrapper, auth_card

SIGNUP_URL = "http://api:8080/auth/register"


@ui.page("/signup")
def signup_page():
    with auth_card_wrapper():
        with auth_card():
            ui.label("Criar conta").classes("text-h4 q-mb-md text-center")

            email = ui.input("Email") \
                .props("type=email filled autocomplete=email") \
                .classes("w-full q-mb-md")

            password = ui.input("Senha", password_toggle_button=True) \
                .props("type=password filled autocomplete=new-password") \
                .classes("w-full q-mb-sm")

            @ui.refreshable
            def password_rules():
                v = password.value or ""
                rules = [
                    ("Pelo menos 8 caracteres", len(v) >= 8),
                    ("Contém um número", any(c.isdigit() for c in v)),
                    ("Contém uma letra", any(c.isalpha() for c in v)),
                ]
                with ui.column().classes("gap-1 mt-1 mb-2 text-sm"):
                    for label, ok in rules:
                        color = "text-green-600" if ok else "text-gray-500"
                        icon = "check-circle-fill" if ok else "circle"
                        ui.html(
                            f'<span class="{color}">'
                            f'<i class="bi bi-{icon}" aria-hidden="true"></i> {label}'
                            f'</span>'
                        )

            password.on("update:model-value", password_rules.refresh)
            password_rules()

            confirm = ui.input("Confirmar Senha", password_toggle_button=True) \
                .props("type=password filled autocomplete=new-password") \
                .classes("w-full q-mb-md")

            signup_btn = primary_button("Criar Conta", full_width=True)
            signup_btn.on("click", lambda: handle_signup(signup_btn, email, password, confirm))
            confirm.on("keydown.enter", lambda: handle_signup(signup_btn, email, password, confirm))

            ui.link("Já tem conta? Faça login", "/login").classes("mt-4")


async def handle_signup(btn, email, password, confirm):
    if not email.value or not password.value or not confirm.value:
        toast_err("Todos os campos são obrigatórios")
        return

    if password.value != confirm.value:
        toast_err("Senhas não coincidem")
        return

    btn.props("loading disable")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SIGNUP_URL, json={
                "email": email.value,
                "password": password.value,
            })

        if response.status_code == 201:
            ui.notify("Conta criada com sucesso!", color="green")
            ui.timer(0.5, lambda: ui.navigate.to("/cadastrar-certificado"))
        else:
            message = parse_err(response.json().get("detail"))
            show_error_dialog(message)
    finally:
        btn.props(remove="loading disable")
