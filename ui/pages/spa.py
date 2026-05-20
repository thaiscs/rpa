from nicegui import app, ui

import pages.add_cert as _add_cert
import pages.clients as _clients
import pages.dashboard as _dashboard
import pages.ecac as _ecac
from components.sidebar import sidebar_spa_contents
from helpers.auth import Auth
from theme import Color

_TITLES = {
    "/dashboard": "Dashboard",
    "/cadastrar-certificado": "Cadastrar Certificado",
    "/ecac": "e-CAC",
    "/clients": "Clientes",
}

_RENDERERS = {
    "/dashboard": _dashboard.render,
    "/cadastrar-certificado": _add_cert.render,
    "/ecac": _ecac.render,
    "/clients": _clients.render,
}

_DEFAULT = "/dashboard"


@ui.page("/")
async def _root():
    ui.navigate.to(_DEFAULT)


@ui.page("/{path:path}")
async def spa(path: str):
    current_path = f"/{path}" if path else _DEFAULT
    if current_path not in _RENDERERS:
        current_path = _DEFAULT

    had_token = bool(app.storage.user.get("token"))
    expired = had_token and Auth._is_expired()
    if not Auth.is_logged_in():
        msg = "Sessão expirada — entre novamente" if expired else "Login necessário"
        ui.notify(msg, color="negative")
        ui.navigate.to("/login")
        return

    user = Auth.user()
    if user is None:
        user = await Auth.fetch_user(Auth.token())

    current = [current_path]
    # Mutable ref so sidebar click handler resolves _navigate after it's defined below
    nav_ref = [None]

    drawer = (
        ui.left_drawer(value=True, bordered=False, fixed=True)
        .props("breakpoint=1024 width=288 show-if-above")
        .classes(f"bg-[{Color.NAVY}] !p-0")
    )
    with drawer:
        sidebar_spa_contents(
            current=current[0],
            on_nav_click=lambda p: nav_ref[0](p),
        )

    with ui.header().classes(f"lg:hidden bg-[{Color.NAVY}] text-white items-center px-4"):
        ui.button(icon="menu", on_click=drawer.toggle).props("flat color=white")
        ui.html(f'<i class="bi bi-robot text-xl text-[{Color.GOLD}]" aria-hidden="true"></i>')
        ui.label("Admin Panel").classes("text-lg font-bold ml-2")

    outer = ui.column().classes("w-full min-w-0 flex-grow gap-0")

    # Topbar: use ui.element("div") + explicit style to avoid Quasar's .row class
    # overriding Tailwind's `hidden` class (specificity tie broken by load order).
    name = (user or {}).get("name") or ""
    email = (user or {}).get("email", "")
    display_name = name.strip() or email
    # Initials: prefer first letters of name parts, else first 2 chars of email,
    # else a generic person icon — never show a literal "?".
    if name.strip():
        parts = [p for p in name.strip().split() if p]
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
    elif email:
        initials = email[:2].upper() if len(email) >= 2 else email[0].upper()
    else:
        initials = ""

    with outer, ui.element("div").style(
        f"display:flex; align-items:center; justify-content:space-between; "
        f"padding:12px 24px; background:{Color.GOLD}; "
        f"border-bottom:1px solid {Color.LINE}; flex-shrink:0;"
    ).classes("w-full"):
        title_label = ui.label(_TITLES.get(current[0], "")).classes(
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

    with outer:
        content_col = ui.column().classes("w-full p-4 sm:p-6 lg:p-8 gap-6")
        with content_col:
            @ui.refreshable
            def content():
                _RENDERERS[current[0]]()

            content()

    async def _navigate(new_path: str):
        current[0] = new_path
        title_label.set_text(_TITLES.get(new_path, ""))
        await ui.run_javascript(f"history.pushState({{}}, '', '{new_path}')")
        content.refresh()

    nav_ref[0] = _navigate
