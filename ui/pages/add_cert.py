from nicegui import ui
from helpers.auth import protected
from components.sidebar import sidebar
from components.cert_form import cert_form


@protected("/cadastrar-certificado")
def add_cert():
    with ui.row().classes("w-full"):
        sidebar(current="/cadastrar-certificado")
        with ui.column().classes("col-grow p-8 min-w-0"):
            cert_form()
