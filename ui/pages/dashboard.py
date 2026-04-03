from nicegui import ui
from components.sidebar import sidebar

@ui.page("/dashboard")
def dashboard():
    with ui.row().classes("w-full"):
        sidebar()
        with ui.column().classes("p-8"):
            ui.label("Dashboard").classes("text-3xl mb-4")
            ui.label("Bem vindo ao painel administrativo.")