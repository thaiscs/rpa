from nicegui import ui
from helpers.auth import Auth

NAV_ITEMS = [
    ("house", "Dashboard", "/dashboard"),
    ("file-earmark-lock", "Cadastrar Certificado", "/cadastrar-certificado"),
    ("shield-lock", "e-CAC", "/ecac"),
    ("people", "Clientes", "/clients"),
]


def sidebar(current: str = ""):
    ui.add_head_html(
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">'
    )
    with ui.column().classes(
        "w-72 h-screen bg-[#091E2F] p-6 gap-2 shadow-xl text-gray-300"
    ):
        with ui.row().classes("items-center gap-3 mb-4"):
            ui.html('<i class="bi bi-robot text-3xl text-[#CEB690]" aria-hidden="true"></i>')
            ui.label("Admin Panel").classes("text-xl font-bold text-white")

        ui.separator().classes("opacity-30 mb-2")

        for icon, label, url in NAV_ITEMS:
            active = current == url
            base = "items-center gap-3 px-3 py-2 rounded-md transition-all cursor-pointer w-full"
            bg = "bg-[#11324C] border-l-2 border-[#CEB690]" if active else "hover:bg-[#11324C]"
            with ui.row().classes(f"{base} {bg}"):
                ui.html(f'<i class="bi bi-{icon} text-xl text-[#CEB690]" aria-hidden="true"></i>')
                ui.link(label, url).classes(
                    "text-gray-100 text-base no-underline hover:text-white flex-grow"
                )

        ui.space()
        user = Auth.user() or {}
        with ui.column().classes("gap-1 mt-auto pt-4 border-t border-white/10"):
            if user.get("email"):
                ui.label(user["email"]).classes("text-sm text-gray-300 truncate")
            with ui.row().classes(
                "items-center gap-2 px-3 py-2 rounded-md hover:bg-[#11324C] "
                "cursor-pointer w-full"
            ).on("click", lambda: (Auth.logout(), ui.navigate.to("/login"))):
                ui.html('<i class="bi bi-box-arrow-right text-lg text-[#CEB690]" aria-hidden="true"></i>')
                ui.label("Sair").classes("text-gray-100")
