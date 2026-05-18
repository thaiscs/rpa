from nicegui import ui

from components.err_toast import toast_err
from components.shell import page_shell
from helpers.auth import protected
from theme import primary_button


@protected("/ecac")
def ecac():
    with page_shell(current="/ecac"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-1"):
                ui.label("Suas notificações e-CAC").classes("text-3xl font-bold")
                ui.label("Acompanhe as notificações fiscais dos seus clientes").classes(
                    "text-gray-600"
                )
            primary_button("Conectar conta e-CAC").on("click", lambda: toast_err("Em breve"))

        with ui.card().classes("w-full p-8 items-center"):
            ui.html('<i class="bi bi-shield-lock text-6xl text-gray-300" aria-hidden="true"></i>')
            ui.label("Nenhuma notificação").classes("text-xl text-gray-500 mt-4")
            ui.label("Conecte uma conta e-CAC para ver as notificações").classes("text-gray-400")
