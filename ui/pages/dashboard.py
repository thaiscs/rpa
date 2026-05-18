from nicegui import ui

from components.shell import page_shell
from helpers.auth import protected
from theme import Color


@protected("/dashboard")
def dashboard():
    with page_shell(current="/dashboard"):
        with ui.column().classes("gap-1"):
            ui.label("Dashboard").classes("text-3xl font-bold")
            ui.label("Visão geral da sua operação").classes("text-gray-600")

        with ui.row().classes("gap-4 w-full flex-wrap"):
            for title, value, hint in [
                ("Certificados ativos", "—", "Aguardando dados"),
                ("Clientes cadastrados", "—", "Aguardando dados"),
                ("Jobs executados hoje", "—", "Aguardando dados"),
            ]:
                with ui.card().classes("p-6 min-w-[14rem] flex-grow"):
                    ui.label(title).classes("text-sm text-gray-500")
                    ui.label(value).classes(f"text-4xl font-bold text-[{Color.NAVY}]")
                    ui.label(hint).classes("text-xs text-gray-400 mt-1")
