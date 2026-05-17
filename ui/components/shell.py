from nicegui import ui
from components.sidebar import sidebar_contents


def page_shell(current: str):
    """Responsive page shell: left_drawer on desktop, hamburger header on mobile."""
    drawer = ui.left_drawer(value=True, bordered=False, fixed=True) \
        .props("breakpoint=1024 width=288 behavior=desktop") \
        .classes("bg-[#091E2F] !p-0")
    with drawer:
        sidebar_contents(current=current, on_navigate=drawer.hide)

    with ui.header().classes("lg:hidden bg-[#091E2F] text-white items-center px-4"):
        ui.button(icon="menu", on_click=drawer.toggle).props("flat color=white")
        ui.html('<i class="bi bi-robot text-xl text-[#CEB690]" aria-hidden="true"></i>')
        ui.label("Admin Panel").classes("text-lg font-bold ml-2")

    return ui.column().classes("w-full p-4 sm:p-6 lg:p-8 gap-6 min-w-0")
