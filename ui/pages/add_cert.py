from nicegui import ui
from components.sidebar import sidebar
from components.cert_form import cert_form

@ui.page("/add-cert")
def add_cert():
    with ui.row().classes("w-[85%]"):
        sidebar()
        with ui.column().classes("col-grow p-8"):
            cert_form()