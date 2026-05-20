from nicegui import ui

from components.err_toast import toast_err
from theme import Color, primary_button


def render():
    with ui.row().classes("items-center justify-between w-full"):
        with ui.column().classes("gap-1"):
            ui.label("e-CAC — Notificações").classes("text-3xl font-bold")
            ui.label("Acompanhe as notificações fiscais dos seus clientes").classes(
                "text-gray-600"
            )
        primary_button("Conectar conta e-CAC").on("click", lambda: toast_err("Em breve"))

    notifications = []  # populated from API in future

    if not notifications:
        with ui.card().classes("w-full p-8 items-center"):
            ui.html(
                '<i class="bi bi-shield-lock text-6xl text-gray-300" aria-hidden="true"></i>'
            )
            ui.label("Nenhuma notificação").classes("text-xl text-gray-500 mt-4")
            ui.label("Conecte uma conta e-CAC para ver as notificações").classes(
                "text-gray-400"
            )
    else:
        with ui.column().classes("gap-2 w-full"):
            for notif in notifications:
                _notification_row(notif)


def _notification_row(notif: dict):
    unread = notif.get("unread", False)
    dot_color = f"[{Color.GOLD}]" if unread else "gray-300"
    with ui.card().classes("w-full p-4"), ui.row().classes("items-start gap-3 w-full"):
        ui.html(
            f'<div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0 '
            f'bg-{dot_color}"></div>'
        )
        with ui.column().classes("gap-0.5 flex-grow min-w-0"):
            ui.label(notif.get("text", "")).classes("text-sm leading-relaxed")
            ui.label(notif.get("time", "")).classes("text-xs text-gray-400")
