from nicegui import ui

from helpers.parsing import parse_err
from theme import Color


def show_error_dialog(message: str, title: str = "Algo deu errado"):
    body = parse_err(message)
    with ui.dialog() as dialog:
        card = ui.card().classes("p-6 gap-4 max-w-md")
        card._props["role"] = "alert"
        with card:
            with ui.row().classes("items-start gap-3 w-full"):
                ui.html(
                    f'<i class="bi bi-exclamation-triangle-fill text-2xl '
                    f'text-[{Color.GOLD_DEEP}]" aria-hidden="true"></i>'
                )
                with ui.column().classes("gap-1 flex-grow min-w-0"):
                    ui.label(title).classes(f"text-lg font-bold text-[{Color.NAVY}]")
                    ui.label(body).classes(f"text-[{Color.INK_SOFT}]")
            with ui.row().classes("self-end gap-2"):
                ui.button("Fechar", on_click=dialog.close).props("flat")
    dialog.open()
