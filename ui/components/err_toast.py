from nicegui import ui

def toast_err(message: str, duration: int = 3000):
    ui.notify(
        message,
        color="negative",
        position="top",
        timeout=duration,
        transition_show="slide-down",
        transition_hide="slide-up"
    )
