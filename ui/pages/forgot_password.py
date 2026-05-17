from nicegui import ui
import httpx
from components.err_toast import toast_err
from theme import primary_button, auth_card_wrapper, auth_card

FORGOT_URL = "http://api:8080/auth/forgot-password"


@ui.page("/forgot-password")
def forgot_page():
    container = auth_card_wrapper()
    with container:
        card = auth_card()
        render_form(card)


def render_form(card):
    card.clear()
    with card:
        ui.label("Recuperar senha").classes("text-h4 q-mb-md text-center")
        email = ui.input("Email") \
            .props("type=email filled autocomplete=email") \
            .classes("w-full q-mb-md")
        btn = primary_button("Enviar link", full_width=True)
        btn.on("click", lambda: handle_forgot(btn, email, card))
        email.on("keydown.enter", lambda: handle_forgot(btn, email, card))
        ui.link("Voltar ao login", "/login").classes("mt-4")


def render_success(card, email_value):
    card.clear()
    with card:
        ui.html('<i class="bi bi-envelope-check text-6xl text-positive" aria-hidden="true"></i>')
        ui.label("Verifique sua caixa de entrada").classes("text-h5 q-mt-md text-center")
        ui.label(
            f"Enviamos um link para {email_value}. "
            f"Verifique também o spam."
        ).classes("text-center q-mt-sm text-gray-600")
        primary_button("Voltar ao login", full_width=True) \
            .classes("q-mt-lg") \
            .on("click", lambda: ui.navigate.to("/login"))


async def handle_forgot(btn, email, card):
    if not email.value:
        toast_err("Email é obrigatório")
        return
    btn.props("loading disable")
    try:
        async with httpx.AsyncClient() as client:
            await client.post(FORGOT_URL, json={"email": email.value})
        render_success(card, email.value)
    finally:
        btn.props(remove="loading disable")
