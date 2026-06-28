import flet as ft
import datetime

def FletesView():
    # ==========================================
    # 1. DATOS SIMULADOS (MOCK DATA)
    # ==========================================
    opciones_clientes = [ft.dropdown.Option("Empresa Polar"), ft.dropdown.Option("Construcciones C.A.")]
    opciones_rutas = [
        ft.dropdown.Option(key="R1", text="Maracaibo - Caracas", data=500), 
        ft.dropdown.Option(key="R2", text="Maracaibo - Valencia", data=400)
    ]
    opciones_choferes = [ft.dropdown.Option("Ricardo Montenegro"), ft.dropdown.Option("Saúl Vera")]
    opciones_camiones = [ft.dropdown.Option("Mack - A123 (Optimus)"), ft.dropdown.Option("Ford - B456 (Rayo)")]

    # ==========================================
    # 2. LÓGICA DE INTERACTIVIDAD Y CALENDARIO
    # ==========================================
    def recalcular_total(e):
        costo_ruta = 0
        if ruta_dd.value:
            opcion_seleccionada = next((opt for opt in ruta_dd.options if opt.key == ruta_dd.value), None)
            if opcion_seleccionada:
                costo_ruta = opcion_seleccionada.data
                txt_costo_ruta.value = f"Costo Ruta: ${costo_ruta:.2f}"

        mora = float(mora_tf.value) if mora_tf.value != "" else 0
        total = costo_ruta + mora
        txt_total_flete.value = f"Total del Flete: ${total:.2f}"
        
        txt_costo_ruta.update()
        txt_total_flete.update()

    def fecha_seleccionada(e):
        if e.control.value:
            fecha_tf.value = e.control.value.strftime("%d/%m/%Y")
            fecha_tf.update()

    calendario = ft.DatePicker(
        on_change=fecha_seleccionada,
        first_date=datetime.datetime(2024, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
        help_text="Seleccione la fecha del flete"
    )

    def abrir_calendario(e):
        if calendario not in e.page.overlay:
            e.page.overlay.append(calendario)
        calendario.open = True
        e.page.update()

    # ==========================================
    # 3. DEFINICIÓN DE CONTROLES VISUALES
    # ==========================================
    txt_costo_ruta = ft.Text("Costo Ruta: $0.00", size=16, color="black54")
    txt_total_flete = ft.Text("Total del Flete: $0.00", size=24, weight=ft.FontWeight.BOLD, color="#1976d2")

    # Creamos un padding estándar para forzar que todos midan matemáticamente lo mismo
    padding_uniforme = ft.Padding.symmetric(vertical=10, horizontal=12)

    # -- Sección 1: Datos del Servicio --
    fecha_tf = ft.TextField(
        label="Fecha de Operación", 
        value=datetime.datetime.now().strftime("%d/%m/%Y"), 
        read_only=True, 
        expand=1,
        content_padding=padding_uniforme,
        suffix=ft.Container(
            content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
            on_click=abrir_calendario,
            padding=0, 
            margin=ft.Margin.only(right=5),
            tooltip="Seleccionar fecha"
        )
    )
    
    cliente_dd = ft.Dropdown(label="Cliente Solicitante", options=opciones_clientes, expand=1, dense=True, content_padding=padding_uniforme)
    ruta_dd = ft.Dropdown(label="Ruta Ejecutada", options=opciones_rutas, expand=2, on_select=recalcular_total, dense=True, content_padding=padding_uniforme)
    estatus_dd = ft.Dropdown(label="Estatus de Pago", options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Pagado")], expand=1, dense=True, content_padding=padding_uniforme)

    # -- Sección 2: Asignación de Recursos --
    chofer_dd = ft.Dropdown(label="Chofer Asignado", options=opciones_choferes, expand=1, dense=True, content_padding=padding_uniforme)
    camion_dd = ft.Dropdown(label="Camión", options=opciones_camiones, expand=1, dense=True, content_padding=padding_uniforme)
    remolque_dd = ft.Dropdown(label="Remolque (Opcional)", options=[], expand=1, dense=True, content_padding=padding_uniforme)

    # -- Sección 3: Datos Operativos y Financieros --
    gasoil_tf = ft.TextField(label="Gasoil Consumido (Lts)", input_filter=ft.NumbersOnlyInputFilter(), expand=1, dense=True, content_padding=padding_uniforme)
    mora_tf = ft.TextField(label="Mora / Espera ($)", value="0", input_filter=ft.NumbersOnlyInputFilter(), expand=1, on_change=recalcular_total, dense=True, content_padding=padding_uniforme)

    # ==========================================
    # 4. ENSAMBLAJE DE LA VISTA (LAYOUT)
    # ==========================================
    return ft.Container(
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Registro de Fletes", size=28, weight=ft.FontWeight.BOLD, color="black87"),
                ft.Divider(height=20, color="transparent"),

                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("1. Datos del Servicio", weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ft.Divider(),
                            ft.Row([fecha_tf, cliente_dd]),
                            ft.Row([ruta_dd, estatus_dd]),
                        ])
                    )
                ),

                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("2. Asignación de Recursos", weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ft.Divider(),
                            ft.Row([chofer_dd, camion_dd, remolque_dd]),
                        ])
                    )
                ),

                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("3. Datos Operativos y Financieros", weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ft.Divider(),
                            ft.Row([gasoil_tf, mora_tf]),
                        ])
                    )
                ),

                ft.Container(
                    padding=20,
                    bgcolor="#e3f2fd",
                    border_radius=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column([txt_costo_ruta, txt_total_flete]),
                            ft.Row([
                                ft.Button("Limpiar Formulario", icon=ft.Icons.DELETE_OUTLINE),
                                ft.Button("Guardar Flete", icon=ft.Icons.SAVE, bgcolor="#1976d2", color="white"),
                            ])
                        ]
                    )
                )
            ]
        )
    )