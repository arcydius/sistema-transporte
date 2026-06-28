import flet as ft
import datetime

def MantenimientoView():
    # ==========================================
    # 1. DATOS SIMULADOS (MOCK DATA)
    # ==========================================
    datos_historial = [
        {"fecha": "20/06/2026", "unidad": "Mack (A123BC)", "tipo": "Preventivo", "tecnico": "Carlos Ruiz", "monto": "$150.00"},
        {"fecha": "15/06/2026", "unidad": "Remolque (X987YZ)", "tipo": "Neumáticos", "tecnico": "Luis Pérez", "monto": "$400.00"},
    ]

    opciones_unidades = [
        ft.dropdown.Option("Mack - A123BC (Chuto)"), 
        ft.dropdown.Option("Ford - B456 (Chuto)"),
        ft.dropdown.Option("Remolque 3 Ejes - X987YZ")
    ]
    
    opciones_tipos = [
        ft.dropdown.Option("Preventivo"),
        ft.dropdown.Option("Correctivo"),
        ft.dropdown.Option("Neumáticos"),
        ft.dropdown.Option("Fluidos y Filtros"),
        ft.dropdown.Option("Otro") 
    ]

    # ==========================================
    # 2. LÓGICA DEL FORMULARIO Y CALENDARIO
    # ==========================================
    padding_uniforme = ft.Padding.symmetric(vertical=10, horizontal=12)

    # --- Controles del Formulario (Sin parámetro 'dense') ---
    tf_fecha = ft.TextField(
        label="Fecha del Servicio", value=datetime.datetime.now().strftime("%d/%m/%Y"), 
        read_only=True, expand=1, content_padding=padding_uniforme
    )
    dd_unidad = ft.Dropdown(label="Unidad", options=opciones_unidades, expand=1, content_padding=padding_uniforme)
    tf_tecnico = ft.TextField(label="Técnico Responsable", expand=1, content_padding=padding_uniforme)
    tf_monto = ft.TextField(label="Costo ($)", input_filter=ft.NumbersOnlyInputFilter(), expand=1, content_padding=padding_uniforme)
    tf_descripcion = ft.TextField(label="Descripción del servicio", multiline=True, min_lines=3, max_lines=5)
    
    tf_otro_tipo = ft.TextField(label="Especifique el tipo de servicio", visible=False, expand=1, content_padding=padding_uniforme)

    def al_cambiar_tipo(e):
        if dd_tipo.value == "Otro":
            tf_otro_tipo.visible = True
        else:
            tf_otro_tipo.visible = False
            tf_otro_tipo.value = "" 
        tf_otro_tipo.update()

    dd_tipo = ft.Dropdown(label="Tipo de Servicio", options=opciones_tipos, expand=1, content_padding=padding_uniforme, on_select=al_cambiar_tipo)

    # --- Lógica del Calendario ---
    def fecha_seleccionada(e):
        if e.control.value:
            tf_fecha.value = e.control.value.strftime("%d/%m/%Y")
            tf_fecha.update()

    calendario = ft.DatePicker(on_change=fecha_seleccionada)
    
    def abrir_calendario(e):
        if calendario not in e.page.overlay:
            e.page.overlay.append(calendario)
        calendario.open = True
        e.page.update()

    # Botón del calendario incrustado
    tf_fecha.suffix = ft.Container(
        content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
        on_click=abrir_calendario, padding=0, margin=ft.Margin.only(right=5), tooltip="Seleccionar fecha"
    )

    # --- Lógica del Modal (Overlay) ---
    def abrir_modal_servicio(e):
        def cerrar(e_cerrar):
            modal.open = False
            e_cerrar.page.update()

        def guardar(e_guardar):
            print(f"[Simulación] Guardando servicio de {dd_unidad.value}...")
            cerrar(e_guardar)

        modal = ft.AlertDialog(
            title=ft.Text("Registrar Servicio de Taller"),
            content=ft.Container(
                width=600,
                content=ft.Column([
                    ft.Row([tf_fecha, dd_unidad]),
                    ft.Row([dd_tipo, tf_otro_tipo]), 
                    ft.Row([tf_tecnico, tf_monto]),
                    tf_descripcion
                ], tight=True)
            ),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Guardar Registro", on_click=guardar, bgcolor="#1976d2", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    # ==========================================
    # 3. CONSTRUCCIÓN DE LA TABLA
    # ==========================================
    filas_tabla = []
    for d in datos_historial:
        filas_tabla.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(d["fecha"])),
                ft.DataCell(ft.Text(d["unidad"], weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(d["tipo"])),
                ft.DataCell(ft.Text(d["tecnico"])),
                ft.DataCell(ft.Text(d["monto"], color="red")),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color="blue", tooltip="Ver Detalles"),
                ])),
            ])
        )

    tabla_servicios = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Tipo Servicio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Técnico", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Costo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=filas_tabla
    )

    # ==========================================
    # 4. ENSAMBLAJE FINAL (Simétrico a MaestrosView)
    # ==========================================
    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Mantenimiento y Taller", size=28, weight=ft.FontWeight.BOLD, color="black87"),
                ft.Divider(height=20, color="transparent"),

                # Barra de búsqueda y botón de agregar (Sin dense, idéntico a Maestros)
                ft.Row([
                    ft.TextField(hint_text="Buscar por placa, tipo o técnico...", prefix_icon=ft.Icons.SEARCH, expand=True),
                    ft.Button("Registrar Servicio", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_servicio)
                ]),
                
                # Tabla
                ft.Row([tabla_servicios], scroll=ft.ScrollMode.AUTO)
            ]
        )
    )