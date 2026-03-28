from nicegui import ui

def sidebar():
    with ui.column().classes(
        'w-84 h-screen bg-[#091E2F] p-6 gap-4 shadow-xl text-gray-300'
    ):

        # --- Header with robot icon ---
        ui.add_head_html('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">')
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.html('<i class="bi bi-robot text-6xl text-[#CEB690]"></i>')
            ui.label('Admin Panel').classes('text-2xl font-bold text-white p-4')

        ui.separator().style("border-bottom-color: white;border-bottom-width: 1px;border-bottom-style: outset;")

        # --- Reusable nav link component ---
        def nav_link(icon_name, text, url):
            with ui.row().classes(
                'items-center gap-3 p-2 rounded-md '
                'hover:bg-[#7A7A7A] transition-all cursor-pointer'
            ):
                ui.html(f'<i class="bi bi-{icon_name} text-3xl text-[#CEB690]"></i>')
                ui.link(text, url).classes('text-gray-100 text-xl no-underline hover:text-white')

        # Home icon for Dashboard
        nav_link('house', 'Dashboard', '/')

        # Certificate/file icon for Add Cert
        nav_link('file-earmark-lock', 'Cadastrar Certificado', '/add-cert')

        # Notifications icon + e-CAC text
        with ui.row().classes(
            'items-center gap-3 p-2 rounded-md '
            'hover:bg-[#7A7A7A] transition-all cursor-pointer'
        ):
            ui.html('<i class="bi bi-bell text-3xl text-[#CEB690]"></i>')
            ui.link('e-CAC', '/ecac').classes('text-gray-100 text-xl no-underline hover:text-white')

        # Clients list icon
        nav_link('people', 'Clientes', '/clients')