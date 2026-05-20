import re

import httpx
from nicegui import ui

from components.err_dialog import show_error_dialog
from components.err_toast import toast_err
from helpers.parsing import parse_err
from theme import Color, auth_card, auth_card_wrapper, primary_button

SIGNUP_URL = "http://api:8080/auth/register"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@ui.page("/signup")
def signup_page():
    with auth_card_wrapper(), auth_card():
        ui.label("Criar conta").classes(
            f"text-h4 text-center text-[{Color.NAVY}] q-mb-xs"
        )
        ui.label("Comece a gerenciar seus certificados digitais.").classes(
            f"text-center text-[{Color.INK_SOFT}] text-sm q-mb-lg"
        )

        with ui.column().classes("gap-4 w-full"):
            email = (
                ui.input("Email")
                .props("type=email filled autocomplete=email")
                .classes("w-full")
            )

            password = (
                ui.input("Senha", password_toggle_button=True)
                .props("type=password filled autocomplete=new-password")
                .classes("w-full")
            )

            @ui.refreshable
            def password_rules():
                v = password.value or ""
                touched = bool(v)
                rules = [
                    ("Pelo menos 8 caracteres", len(v) >= 8),
                    ("Contém um número", any(c.isdigit() for c in v)),
                    ("Contém uma letra", any(c.isalpha() for c in v)),
                ]
                with ui.column().classes("gap-1 text-sm -mt-2"):
                    for label, ok in rules:
                        if not touched:
                            color = f"text-[{Color.INK_MUTE}]"
                            icon = "circle"
                        elif ok:
                            color = "text-green-600"
                            icon = "check-circle-fill"
                        else:
                            color = f"text-[{Color.INK_MUTE}]"
                            icon = "circle"
                        ui.html(
                            f'<span class="{color} inline-flex items-center gap-2 '
                            f'transition-all duration-150">'
                            f'<i class="bi bi-{icon}" aria-hidden="true"></i>'
                            f'<span>{label}</span>'
                            f'</span>'
                        )

            password.on_value_change(lambda _: password_rules.refresh())
            password_rules()

            confirm = (
                ui.input("Confirmar Senha", password_toggle_button=True)
                .props("type=password filled autocomplete=new-password")
                .classes("w-full")
            )

            @ui.refreshable
            def confirm_status():
                pw = password.value or ""
                cf = confirm.value or ""
                if not cf:
                    return
                if pw == cf:
                    ui.html(
                        '<span class="text-green-600 inline-flex items-center gap-2 '
                        'text-sm -mt-2 transition-all duration-150">'
                        '<i class="bi bi-check-circle-fill" aria-hidden="true"></i>'
                        '<span>Senhas coincidem</span>'
                        '</span>'
                    )
                else:
                    ui.html(
                        '<span class="text-red-600 inline-flex items-center gap-2 '
                        'text-sm -mt-2 transition-all duration-150">'
                        '<i class="bi bi-x-circle-fill" aria-hidden="true"></i>'
                        '<span>Senhas não coincidem</span>'
                        '</span>'
                    )

            confirm.on_value_change(lambda _: confirm_status.refresh())
            password.on_value_change(lambda _: confirm_status.refresh())
            confirm_status()

            signup_btn = primary_button("Criar Conta", full_width=True)
            signup_btn.classes("q-mt-sm")

        submit = lambda: handle_signup(signup_btn, email, password, confirm)  # noqa: E731
        signup_btn.on("click", submit)
        email.on("keydown.enter", submit)
        password.on("keydown.enter", submit)
        confirm.on("keydown.enter", submit)

        with ui.row().classes("items-center justify-center gap-1 mt-4 text-sm w-full"):
            ui.label("Já tem conta?").classes(f"text-[{Color.INK_SOFT}]")
            ui.link("Faça login", "/login").classes(
                f"text-[{Color.GOLD_DEEP}] font-medium hover:underline"
            )


async def handle_signup(btn, email, password, confirm):
    if not email.value or not password.value or not confirm.value:
        toast_err("Todos os campos são obrigatórios")
        return

    if not EMAIL_RE.match(email.value.strip()):
        toast_err("Informe um email válido")
        return

    pw = password.value
    if len(pw) < 8 or not any(c.isdigit() for c in pw) or not any(c.isalpha() for c in pw):
        toast_err("A senha não atende aos requisitos")
        return

    if password.value != confirm.value:
        toast_err("Senhas não coincidem")
        return

    btn.props("loading disable")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(SIGNUP_URL, json={
                "email": email.value.strip(),
                "password": password.value,
            })

        if response.status_code == 201:
            ui.notify("Conta criada com sucesso!", type="positive", position="top")
            ui.timer(0.8, lambda: ui.navigate.to("/cadastrar-certificado"), once=True)
        else:
            message = parse_err(response.json().get("detail"))
            show_error_dialog(message, title="Não foi possível criar a conta")
    finally:
        btn.props(remove="loading disable")
