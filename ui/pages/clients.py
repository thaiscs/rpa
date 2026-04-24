from nicegui import ui
from components.sidebar import sidebar
from helpers.auth import protected

@protected("/clients")
def clients():
    with ui.row().classes("w-full"):
        sidebar()
        with ui.column().classes("p-8"):
            ui.label("Clientes").classes("text-3xl mb-4")
            ui.label("Bem vindo ao painel administrativo.")