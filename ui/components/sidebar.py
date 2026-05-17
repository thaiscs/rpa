from nicegui import ui

from helpers.auth import Auth
from theme import Color

NAV_ITEMS = [
    ("house", "Dashboard", "/dashboard"),
    ("file-earmark-lock", "Cadastrar Certificado", "/cadastrar-certificado"),
    ("shield-lock", "e-CAC", "/ecac"),
    ("people", "Clientes", "/clients"),
]


def sidebar_contents(current: str = "", on_navigate=None):
    """Nav content without an outer wrapper — used inside ui.left_drawer."""
    ui.add_head_html(
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">'
    )
    with ui.column().classes("p-6 gap-2 h-full"):
        with ui.row().classes("items-center gap-3 mb-4"):
            ui.html(f'<i class="bi bi-robot text-3xl text-[{Color.GOLD}]" aria-hidden="true"></i>')
            ui.label("Admin Panel").classes("text-xl font-bold text-white")

        ui.separator().classes("opacity-30 mb-2")

        for icon, label, url in NAV_ITEMS:
            active = current == url
            base = "items-center gap-3 px-3 py-2 rounded-md transition-all cursor-pointer w-full"
            bg = (
                f"bg-[{Color.NAVY_SOFT}] border-l-2 border-[{Color.GOLD}]"
                if active
                else f"hover:bg-[{Color.NAVY_SOFT}]"
            )
            row = ui.row().classes(f"{base} {bg}")
            row._props["tabindex"] = "0"
            row._props["data-nav-link"] = ""
            with row:
                ui.html(f'<i class="bi bi-{icon} text-xl text-[{Color.GOLD}]" aria-hidden="true"></i>')

                def _make_click(u, nav=on_navigate):
                    def _click():
                        if nav:
                            nav()
                        ui.navigate.to(u)
                    return _click

                ui.link(label, url).classes(
                    "text-gray-100 text-base no-underline hover:text-white flex-grow"
                )
                if on_navigate:
                    row.on("click", _make_click(url))

        ui.space()
        user = Auth.user() or {}
        with ui.column().classes("gap-1 mt-auto pt-4 border-t border-white/10"):
            if user.get("email"):
                ui.label(user["email"]).classes("text-sm text-gray-300 truncate")
            with ui.row().classes(
                f"items-center gap-2 px-3 py-2 rounded-md hover:bg-[{Color.NAVY_SOFT}] "
                "cursor-pointer w-full"
            ).on("click", lambda: (Auth.logout(), ui.navigate.to("/login"))):
                ui.html(f'<i class="bi bi-box-arrow-right text-lg text-[{Color.GOLD}]" aria-hidden="true"></i>')
                ui.label("Sair").classes("text-gray-100")


def sidebar(current: str = ""):
    """Full sidebar column — used on desktop layouts without a drawer."""
    with ui.column().classes(f"w-72 h-screen bg-[{Color.NAVY}] shadow-xl text-gray-300"):
        sidebar_contents(current=current)
