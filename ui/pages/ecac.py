from nicegui import ui
from components.sidebar import sidebar
from helpers.auth import protected
from components.err_toast import toast_err


@protected("/ecac")
def ecac():
    with ui.row().classes("w-full"):
        sidebar(current="/ecac")
        with ui.column().classes("col-grow p-8 gap-6 min-w-0"):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.column().classes("gap-1"):
                    ui.label("Suas notificações e-CAC").classes("text-3xl font-bold")
                    ui.label("Acompanhe as notificações fiscais dos seus clientes").classes(
                        "text-gray-600"
                    )
                ui.button("Conectar conta e-CAC", on_click=lambda: toast_err("Em breve")) \
                    .props("flat").classes(
                        "bg-[#CEB690] text-white hover:bg-[#93713C] q-pa-md rounded"
                    )

            with ui.card().classes("w-full p-8 items-center"):
                ui.html('<i class="bi bi-shield-lock text-6xl text-gray-300" aria-hidden="true"></i>')
                ui.label("Nenhuma notificação").classes("text-xl text-gray-500 mt-4")
                ui.label("Conecte uma conta e-CAC para ver as notificações").classes("text-gray-400")
