from nicegui import ui

from theme import Color


def render():
    with ui.column().classes("gap-1"):
        ui.label("Dashboard").classes("text-3xl font-bold")
        ui.label("Visão geral da sua operação").classes("text-gray-600")

    with ui.row().classes("gap-4 w-full flex-wrap"):
        for title, value, hint, warn in [
            ("Certificados ativos", "—", "Aguardando dados", False),
            ("Clientes cadastrados", "—", "Aguardando dados", False),
            ("Expirando em 30d", "—", "Aguardando dados", True),
            ("Tarefas e-CAC", "—", "Aguardando dados", False),
        ]:
            with ui.card().classes("p-6 min-w-[14rem] flex-grow"):
                ui.label(title).classes("text-sm text-gray-500")
                value_color = "[#854F0B]" if warn else f"[{Color.NAVY}]"
                ui.label(value).classes(f"text-4xl font-bold text-{value_color}")
                ui.label(hint).classes("text-xs text-gray-400 mt-1")

    with ui.card().classes("w-full overflow-hidden p-0"):
        ui.label("Certificados recentes").classes(
            "text-sm font-medium px-4 py-3 border-b border-gray-100"
        )
        columns = [
            {"name": "razao_social", "label": "Razão Social", "field": "razao_social", "align": "left"},
            {"name": "cnpj", "label": "CNPJ", "field": "cnpj", "align": "left"},
            {"name": "validade", "label": "Validade", "field": "validade", "align": "left"},
            {"name": "status", "label": "Status", "field": "status", "align": "left"},
        ]
        ui.table(columns=columns, rows=[], row_key="cnpj").classes("w-full").props("flat")
