from nicegui import ui
from components.shell import page_shell
from helpers.auth import protected
from components.err_toast import toast_err
from theme import primary_button


@protected("/clients")
def clients():
    with page_shell(current="/clients"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-1"):
                ui.label("Clientes").classes("text-3xl font-bold")
                ui.label("Gerencie os clientes cadastrados").classes("text-gray-600")
            primary_button("Adicionar cliente").on("click", lambda: toast_err("Em breve"))

        with ui.card().classes("w-full p-8 items-center"):
            ui.html('<i class="bi bi-people text-6xl text-gray-300" aria-hidden="true"></i>')
            ui.label("Nenhum cliente cadastrado").classes("text-xl text-gray-500 mt-4")
            ui.label("Adicione um cliente para começar").classes("text-gray-400")
