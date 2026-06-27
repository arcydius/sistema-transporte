import flet as ft

def FletesView():
    # ==========================================
    # 1. DATOS SIMULADOS (MOCK DATA)
    # Tu compañero reemplazará esto conectándose a PostgreSQL
    # ==========================================
    opciones_clientes = [ft.dropdown.Option("Empresa Polar"), ft.dropdown.Option("Construcciones C.A.")]
    opciones_rutas = [
        # Usamos el atributo 'data' oculto para guardar el precio real de la ruta y usarlo en cálculos
        ft.dropdown.Option(key="R1", text="Maracaibo - Caracas", data=500), 
        ft.dropdown.Option(key="R2", text="Maracaibo - Valencia", data=400)
    ]
    opciones_choferes = [ft.dropdown.Option("Ricardo Montenegro"), ft.dropdown.Option("Saúl Vera")]
    opciones_camiones = [ft.dropdown.Option("Mack - A123 (Optimus)"), ft.dropdown.Option("Ford - B456 (Rayo)")]

    # ==========================================
    # 2. DEFINICIÓN DE CONTROLES VISUALES
    # ==========================================
    
    # -- Sección 1: Datos del Servicio --
    # Nota: Usamos ft.TextField(read_only=True) temporalmente para la fecha hasta implementar el calendario
    fecha_tf = ft.TextField(
        label="Fecha de Operación", value="17/06/2026", 
        read_only=True, 
        prefix_icon=ft.Icons.CALENDAR_MONTH, 
        expand=1)
    
    cliente_dd = ft.Dropdown(label="Cliente Solicitante", options=opciones_clientes, expand=1)

    ruta_dd = ft.Dropdown(label="Ruta Ejecutada", options=opciones_rutas, expand=2)

    estatus_dd = ft.Dropdown(
        label="Estatus de Pago", 
        options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Pagado")], 
        expand=1)

    # -- Sección 2: Asignación de Recursos --
    chofer_dd = ft.Dropdown(label="Chofer Asignado", options=opciones_choferes, expand=1)
    camion_dd = ft.Dropdown(label="Camión", options=opciones_camiones, expand=1)
    remolque_dd = ft.Dropdown(label="Remolque (Opcional)", options=[], expand=1) # Vacío por ahora

    # -- Sección 3: Datos Operativos y Financieros --
    gasoil_tf = ft.TextField(label="Gasoil Consumido (Lts)", input_filter=ft.NumbersOnlyInputFilter(), expand=1)
    mora_tf = ft.TextField(label="Mora / Espera ($)", value="0", input_filter=ft.NumbersOnlyInputFilter(), expand=1)

    # -- Sección 4: Resumen (Textos de solo lectura) --
    txt_costo_ruta = ft.Text("Costo Ruta: $0.00", size=16, color="black54")
    txt_total_flete = ft.Text("Total del Flete: $0.00", size=24, weight=ft.FontWeight.BOLD, color="#1976d2")


    # ==========================================
    # 3. LÓGICA DE INTERACTIVIDAD (LA MAGIA DE FLET)
    # ==========================================
    def recalcular_total(e):
        # 1. Obtenemos el costo de la ruta seleccionada (leyendo el 'data' oculto de la opción elegida)
        costo_ruta = 0
        if ruta_dd.value:
            # Buscamos la opción seleccionada dentro de la lista de rutas
            opcion_seleccionada = next((opt for opt in ruta_dd.options if opt.key == ruta_dd.value), None)
            if opcion_seleccionada:
                costo_ruta = opcion_seleccionada.data
                txt_costo_ruta.value = f"Costo Ruta: ${costo_ruta:.2f}"

        # 2. Obtenemos el valor de la mora (si está vacío, asumimos 0)
        mora = float(mora_tf.value) if mora_tf.value != "" else 0

        # 3. Calculamos y actualizamos el gran total en pantalla
        total = costo_ruta + mora
        txt_total_flete.value = f"Total del Flete: ${total:.2f}"
        
        # Le decimos a la página que actualice solo estos textos
        txt_costo_ruta.update()
        txt_total_flete.update()

    # Conectamos los eventos: Cuando la ruta o la mora cambien, se dispara el cálculo
    ruta_dd = ft.Dropdown(label="Ruta Ejecutada", options=opciones_rutas, expand=2, on_select=recalcular_total)
    mora_tf.on_change = recalcular_total

    # ==========================================
    # 4. ENSAMBLAJE DE LA VISTA (LAYOUT)
    # ==========================================
    # Retornamos todo envuelto en un contenedor para que main.py lo inyecte
    return ft.Container(
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO, # Permite hacer scroll si la pantalla es pequeña
            controls=[
                ft.Text("Registro de Operación Logística (Flete)", size=28, weight=ft.FontWeight.BOLD, color="black87"),
                ft.Divider(height=20, color="transparent"),

                # --- TARJETA 1: SERVICIO ---
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

                # --- TARJETA 2: RECURSOS ---
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

                # --- TARJETA 3: OPERATIVIDAD ---
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

                # --- TARJETA 4: RESUMEN Y ACCIONES ---
                ft.Container(
                    padding=20,
                    bgcolor="#e3f2fd", # Fondo azul muy clarito
                    border_radius=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            # Izquierda: Textos de cálculo
                            ft.Column([txt_costo_ruta, txt_total_flete]),
                            # Derecha: Botones
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