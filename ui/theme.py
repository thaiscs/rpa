"""Design tokens and component helpers. Single source of truth for visuals."""
from nicegui import ui


class Color:
    NAVY        = "#091E2F"
    NAVY_SOFT   = "#11324C"
    NAVY_DEEP   = "#061421"
    GOLD        = "#CEB690"
    GOLD_DEEP   = "#93713C"
    INK         = "#0B1A26"
    INK_SOFT    = "#3A4854"
    INK_MUTE    = "#6B7682"
    SURFACE     = "#FFFFFF"
    SURFACE_ALT = "#F2EEE6"
    LINE        = "#E3DDD0"


class Radius:
    SM = "rounded"
    MD = "rounded-md"
    LG = "rounded-lg"


def primary_button(text: str, *, full_width: bool = False) -> ui.button:
    btn = ui.button(text).props("flat unelevated")
    classes = (
        f"bg-[{Color.GOLD}] text-white hover:bg-[{Color.GOLD_DEEP}] "
        f"transition-all q-pa-md {Radius.MD}"
    )
    if full_width:
        classes += " w-full"
    btn.classes(classes)
    return btn


def field(label: str, *, password: bool = False, required: bool = True,
          autocomplete: str | None = None, **validation) -> ui.input:
    inp = ui.input(label, password_toggle_button=password, validation=validation or None)
    props = ["filled", "lazy-rules"]
    if required:
        props.append("required")
    if password:
        props.append("type=password")
    if autocomplete:
        props.append(f"autocomplete={autocomplete}")
    inp.props(" ".join(props))
    inp.classes("w-full mb-3")
    return inp


def auth_card_wrapper():
    return ui.element("div").classes(
        f"flex justify-center items-center min-h-screen w-full bg-[{Color.NAVY}]"
    )


def auth_card():
    return ui.element("q-card").classes(
        "shadow-3 rounded-borders bg-white flex flex-col items-center "
        "w-full max-w-md mx-4 p-6 sm:p-10"
    )
