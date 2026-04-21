from nicegui import ui
from helpers.parsing import parse_err

def show_error_dialog(message):
    with ui.dialog() as dialog:
        with ui.card().classes("q-pa-md").style("align-items:flex-end;"):
            ui.button().props("icon=close color=gray flat round").on("click", dialog.close)
            ui.label("ERRO: " + parse_err(message)).classes("text-negative text-h6 q-pb-lg")
            dialog.open()