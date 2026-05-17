from nicegui import ui
import httpx
from components.err_toast import toast_err

FORGOT_URL = "http://api:8080/auth/forgot-password"


@ui.page("/forgot-password")
def forgot_page():
    container = ui.element("div").classes(
        "flex justify-center items-center min-h-screen w-full bg-[#091E2F]"
    )
    with container:
        card = ui.element("q-card").classes(
            "q-pa-md sm:q-pa-xl shadow-3 rounded-borders bg-white flex flex-col "
            "items-center w-full max-w-md mx-4"
        )
        render_form(card)


def render_form(card):
    card.clear()
    with card:
        ui.label("Recuperar senha").classes("text-h4 q-mb-md text-center")
        email = ui.input("Email") \
            .props("type=email filled autocomplete=email") \
            .classes("w-full q-mb-md")
        btn = ui.button("Enviar link").props("flat").classes(
            "bg-[#CEB690] text-white hover:bg-[#93713C] q-pa-md rounded w-full"
        )
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
        ui.button("Voltar ao login", on_click=lambda: ui.navigate.to("/login")) \
            .props("flat").classes(
                "bg-[#CEB690] text-white hover:bg-[#93713C] q-pa-md rounded w-full q-mt-lg"
            )


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
