from nicegui import ui

from components.sidebar import sidebar_contents
from helpers.auth import Auth
from theme import Color

_TITLES = {
    "/dashboard": "Dashboard",
    "/cadastrar-certificado": "Cadastrar Certificado",
    "/ecac": "e-CAC",
    "/clients": "Clientes",
}


def page_shell(current: str):
    """Responsive page shell: left_drawer on desktop, hamburger header on mobile."""
    drawer = (
        ui.left_drawer(value=True, bordered=False, fixed=True)
        .props("breakpoint=1024 width=288 show-if-above")
        .classes(f"bg-[{Color.NAVY}] !p-0")
    )
    with drawer:
        sidebar_contents(current=current, on_navigate=drawer.hide)

    user = Auth.user() or {}
    email = user.get("email", "")

    with ui.header().classes(f"lg:hidden bg-[{Color.NAVY}] text-white items-center px-4"):
        ui.button(icon="menu", on_click=drawer.toggle).props("flat color=white")
        ui.html(f'<i class="bi bi-robot text-xl text-[{Color.GOLD}]" aria-hidden="true"></i>')
        ui.label("Admin Panel").classes("text-lg font-bold ml-2")
        ui.space()
        if email:
            ui.label(email).classes("text-xs text-gray-300 truncate max-w-[10rem]")
        ui.button(icon="logout", on_click=lambda: (Auth.logout(), ui.navigate.to("/login"))) \
            .props("flat round dense color=white") \
            .tooltip("Sair")

    # Outer column holds topbar + page content (both sit in the main scroll area)
    outer = ui.column().classes("w-full min-w-0 flex-grow gap-0")
    with outer:
        _topbar(current)

    # Inner padded column is what pages write into — returned as the context target
    with outer:
        inner = ui.column().classes("w-full p-4 sm:p-6 lg:p-8 gap-6")

    return inner


def _topbar(current: str):
    user = Auth.user() or {}
    name = (user.get("name") or "").strip()
    email = user.get("email", "")
    display_name = name or email

    if name:
        parts = [p for p in name.split() if p]
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
    elif email:
        initials = email[:2].upper() if len(email) >= 2 else email[0].upper()
    else:
        initials = ""

    with ui.row().classes(
        f"hidden lg:flex w-full items-center justify-between px-6 py-3 "
        f"bg-[{Color.GOLD}] border-b border-[{Color.LINE}] flex-shrink-0"
    ):
        ui.label(_TITLES.get(current, "")).classes(
            f"text-sm font-semibold text-[{Color.NAVY}]"
        )
        with ui.row().classes("items-center gap-3"):
            if display_name:
                ui.label(display_name).classes(
                    f"text-xs text-[{Color.NAVY}] truncate max-w-[14rem]"
                )
            if initials:
                ui.html(
                    f'<div style="width:30px;height:30px;border-radius:50%;'
                    f'background:{Color.NAVY};display:flex;align-items:center;'
                    f'justify-content:center;font-size:11px;font-weight:600;'
                    f'color:{Color.GOLD}" aria-label="{display_name}" '
                    f'title="{display_name}">{initials}</div>'
                )
            else:
                ui.html(
                    f'<div style="width:30px;height:30px;border-radius:50%;'
                    f'background:{Color.NAVY};display:flex;align-items:center;'
                    f'justify-content:center;color:{Color.GOLD}" '
                    f'aria-label="Usuário"><i class="bi bi-person" '
                    f'style="font-size:16px;"></i></div>'
                )
