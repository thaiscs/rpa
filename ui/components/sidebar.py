from nicegui import ui

from helpers.auth import Auth
from theme import Color

NAV_ITEMS = [
    ("house", "Dashboard", "/dashboard"),
    ("file-earmark-lock", "Cadastrar Certificado", "/cadastrar-certificado"),
    ("shield-lock", "e-CAC", "/ecac"),
    ("people", "Clientes", "/clients"),
]


_NAV_ACTIVE_CSS = """
[data-nav-link].nav-active {
    background: rgba(17, 50, 76, 0.9);
    border-left: 2px solid #CEB690;
    color: #CEB690 !important;
}
[data-nav-link].nav-active a { color: #CEB690 !important; }
"""

_NAV_ACTIVE_JS = """
(function () {
    function applyActive() {
        var path = window.location.pathname;
        document.querySelectorAll('[data-nav-link]').forEach(function (el) {
            if (el.getAttribute('data-nav-href') === path) {
                el.classList.add('nav-active');
            } else {
                el.classList.remove('nav-active');
            }
        });
    }
    applyActive();
    document.addEventListener('click', function (ev) {
        var el = ev.target.closest('[data-nav-link]');
        if (!el) return;
        document.querySelectorAll('[data-nav-link]').forEach(function (e) {
            e.classList.remove('nav-active');
        });
        el.classList.add('nav-active');
    });
})();
"""


def install_nav_assets():
    """Register sidebar's shared CSS/JS once at app startup. Call from main.py."""
    ui.add_head_html(
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">',
        shared=True,
    )
    ui.add_css(_NAV_ACTIVE_CSS, shared=True)
    ui.add_body_html(f"<script>{_NAV_ACTIVE_JS}</script>", shared=True)


def sidebar_contents(current: str = "", on_navigate=None):
    """Nav content without an outer wrapper — used inside ui.left_drawer."""

    with ui.column().classes("p-6 gap-2 h-full"):
        with ui.row().classes("items-center gap-3 mb-4"):
            ui.html(f'<i class="bi bi-robot text-3xl text-[{Color.GOLD}]" aria-hidden="true"></i>')
            ui.label("Admin Panel").classes("text-xl font-bold text-white")

        ui.separator().classes("opacity-30 mb-2")

        for icon, label, url in NAV_ITEMS:
            base = (
                "items-center gap-3 px-3 py-2 rounded-md transition-all "
                f"cursor-pointer w-full hover:bg-[{Color.NAVY_SOFT}]"
            )
            # Python sets initial active state (SSR); JS keeps it correct on click
            initial = "nav-active" if current == url else ""
            row = ui.row().classes(f"{base} {initial}")
            row._props["tabindex"] = "0"
            row._props["data-nav-link"] = ""
            row._props["data-nav-href"] = url
            with row:
                ui.html(
                    f'<i class="bi bi-{icon} text-xl text-[{Color.GOLD}]"'
                    ' aria-hidden="true"></i>'
                )
                ui.label(label).classes("text-gray-100 text-base flex-grow")
            row.on("click", lambda u=url: (on_navigate() if on_navigate else None, ui.navigate.to(u)))

        ui.space()
        user = Auth.user() or {}
        with ui.column().classes("gap-1 mt-auto pt-4 border-t border-white/10"):
            if user.get("email"):
                ui.label(user["email"]).classes("text-sm text-gray-300 truncate")
            with ui.row().classes(
                f"items-center gap-2 px-3 py-2 rounded-md hover:bg-[{Color.NAVY_SOFT}] "
                "cursor-pointer w-full"
            ).on("click", lambda: (Auth.logout(), ui.navigate.to("/login"))):
                ui.html(
                    f'<i class="bi bi-box-arrow-right text-lg text-[{Color.GOLD}]"'
                    ' aria-hidden="true"></i>'
                )
                ui.label("Sair").classes("text-gray-100")


def sidebar_spa_contents(current: str = "", on_nav_click=None):
    """Nav content for SPA — uses click handlers instead of <a href> links."""

    with ui.column().classes("p-6 gap-2 h-full"):
        with ui.row().classes("items-center gap-3 mb-4"):
            ui.html(f'<i class="bi bi-robot text-3xl text-[{Color.GOLD}]" aria-hidden="true"></i>')
            ui.label("Admin Panel").classes("text-xl font-bold text-white")

        ui.separator().classes("opacity-30 mb-2")

        for icon, label, url in NAV_ITEMS:
            base = (
                "items-center gap-3 px-3 py-2 rounded-md transition-all "
                f"cursor-pointer w-full hover:bg-[{Color.NAVY_SOFT}]"
            )
            initial = "nav-active" if current == url else ""
            row = ui.row().classes(f"{base} {initial}")
            row._props["tabindex"] = "0"
            row._props["data-nav-link"] = ""
            row._props["data-nav-href"] = url
            with row:
                ui.html(
                    f'<i class="bi bi-{icon} text-xl text-[{Color.GOLD}]"'
                    ' aria-hidden="true"></i>'
                )
                ui.label(label).classes("text-gray-100 text-base flex-grow")
            if on_nav_click:
                async def _click(u=url):
                    await on_nav_click(u)
                row.on("click", _click)

        ui.space()
        user = Auth.user() or {}
        with ui.column().classes("gap-1 mt-auto pt-4 border-t border-white/10"):
            if user.get("email"):
                ui.label(user["email"]).classes("text-sm text-gray-300 truncate")
            with ui.row().classes(
                f"items-center gap-2 px-3 py-2 rounded-md hover:bg-[{Color.NAVY_SOFT}] "
                "cursor-pointer w-full"
            ).on("click", lambda: (Auth.logout(), ui.navigate.to("/login"))):
                ui.html(
                    f'<i class="bi bi-box-arrow-right text-lg text-[{Color.GOLD}]"'
                    ' aria-hidden="true"></i>'
                )
                ui.label("Sair").classes("text-gray-100")


def sidebar(current: str = ""):
    """Full sidebar column — used on desktop layouts without a drawer."""
    with ui.column().classes(f"w-72 h-screen bg-[{Color.NAVY}] shadow-xl text-gray-300"):
        sidebar_contents(current=current)
