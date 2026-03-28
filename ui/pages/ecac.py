from nicegui import ui
from components.sidebar import sidebar

@ui.page("/ecac")
def ecac():
    with ui.row().classes("w-full"):
        sidebar()
        with ui.column().classes("p-8"):
            ui.label("e-CAC").classes("text-3xl mb-4")
            ui.label("Bem vindo às suas notificações.")