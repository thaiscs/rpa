from nicegui import ui
from helpers.parsing import parse_err


def show_error_dialog(message: str, title: str = "Algo deu errado"):
    body = parse_err(message)
    with ui.dialog() as dialog:
        with ui.card().classes("q-pa-md p-6 gap-4 max-w-md"):
            with ui.row().classes("items-start gap-3 w-full"):
                ui.html(
                    '<i class="bi bi-exclamation-triangle-fill text-2xl '
                    'text-[#93713C]" aria-hidden="true"></i>'
                )
                with ui.column().classes("gap-1 flex-grow min-w-0"):
                    ui.label(title).classes("text-lg font-bold text-[#091E2F]")
                    ui.label(body).classes("text-gray-600")
            with ui.row().classes("self-end gap-2"):
                ui.button("Fechar", on_click=dialog.close).props("flat")
    dialog.open()
