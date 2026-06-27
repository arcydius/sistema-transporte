import flet as ft

def MaestrosView():
    # ==========================================
    # 1. DATOS SIMULADOS (MOCK DATA)
    # ==========================================
    datos_choferes = [
        {"cedula": "V-12345678", "nombre": "Ricardo Montenegro", "telefono": "0414-1234567", "estatus": "Activo"},
        {"cedula": "V-87654321", "nombre": "Saúl Vera", "telefono": "0412-9876543", "estatus": "Activo"}
    ]
    
    datos_flota = [
        {"placa": "A123BC", "marca": "Mack (Optimus)", "tipo": "Chuto", "capacidad": "N/A"},
        {"placa": "X987YZ", "marca": "Remolque 3 Ejes", "tipo": "Batea", "capacidad": "30 Ton"}
    ]
    
    datos_clientes = [
        {"rif": "J-12345678-9", "razon_social": "Empresa Polar", "contacto": "Juan Pérez", "telefono": "0414-1112233"},
        {"rif": "J-98765432-1", "razon_social": "Construcciones C.A.", "contacto": "María Gómez", "telefono": "0412-3334455"}
    ]
    
    datos_rutas = [
        {"codigo": "R1", "origen": "Maracaibo", "destino": "Caracas", "costo": "$500"},
        {"codigo": "R2", "origen": "Maracaibo", "destino": "Valencia", "costo": "$400"}
    ]

    # ==========================================
    # 2. LÓGICA DE VENTANAS MODALES (MÉTODO OVERLAY)
    # ==========================================
    # El método Overlay inyecta el modal en la capa superior sin fallar en ninguna versión
    
    def abrir_modal_chofer(e, datos=None):
        titulo = "Editar Chofer" if datos else "Nuevo Chofer"
        
        tf_cedula = ft.TextField(label="Cédula", value=datos["cedula"] if datos else "")
        tf_nombre = ft.TextField(label="Nombre Completo", value=datos["nombre"] if datos else "")
        tf_telefono = ft.TextField(label="Teléfono", value=datos["telefono"] if datos else "")
        
        def cerrar(e_cerrar):
            modal.open = False
            e_cerrar.page.update()

        def guardar(e_guardar):
            print(f"[Simulación] Guardando chofer: {tf_nombre.value}...")
            cerrar(e_guardar)

        modal = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Column([tf_cedula, tf_nombre, tf_telefono], tight=True),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Guardar", on_click=guardar, bgcolor="#1976d2", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # EL TRUCO INFALIBLE: Lo metemos en el overlay
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def abrir_modal_eliminar(e, nombre):
        def cerrar(e_cerrar):
            modal_eliminar.open = False
            e_cerrar.page.update()

        def confirmar(e_conf):
            print(f"[Simulación] Eliminando a: {nombre}...")
            cerrar(e_conf)

        modal_eliminar = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text(f"¿Estás seguro de que deseas dar de baja a {nombre}? Esta acción no se puede deshacer."),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=confirmar, bgcolor="red", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        e.page.overlay.append(modal_eliminar)
        modal_eliminar.open = True
        e.page.update()

    # Modal genérico para no repetir código visual en Flota, Clientes y Rutas
    def abrir_modal_generico(e, modulo):
        def cerrar(e_cerrar):
            modal_gen.open = False
            e_cerrar.page.update()

        modal_gen = ft.AlertDialog(
            title=ft.Text(f"Módulo: {modulo}"),
            content=ft.Text("El CRUD de esta tabla lo conectará tu compañero del Backend."),
            actions=[ft.Button("Entendido", on_click=cerrar)],
        )
        
        e.page.overlay.append(modal_gen)
        modal_gen.open = True
        e.page.update()

    # ==========================================
    # 3. CONSTRUCCIÓN DE LAS VISTAS Y TABLAS
    # ==========================================
    
    # -- VISTA: CHOFERES --
    filas_choferes = []
    for c in datos_choferes:
        filas_choferes.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(c["cedula"])),
                ft.DataCell(ft.Text(c["nombre"])),
                ft.DataCell(ft.Text(c["telefono"])),
                ft.DataCell(ft.Text(c["estatus"])),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color="blue", on_click=lambda e, data=c: abrir_modal_chofer(e, data)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e, nom=c["nombre"]: abrir_modal_eliminar(e, nom)),
                ])),
            ])
        )
    tabla_choferes = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Cédula", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Estatus", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=filas_choferes
    )
    vista_choferes = ft.Column([
        ft.Row([
            ft.TextField(hint_text="Buscar por nombre o cédula...", prefix_icon=ft.Icons.SEARCH, expand=True),
            ft.Button("Nuevo Chofer", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_chofer)
        ]), ft.Row([tabla_choferes], scroll=ft.ScrollMode.AUTO)
    ])

    # -- VISTA: FLOTA --
    filas_flota = []
    for f in datos_flota:
        filas_flota.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(f["placa"])),
                ft.DataCell(ft.Text(f["marca"])),
                ft.DataCell(ft.Text(f["tipo"])),
                ft.DataCell(ft.Text(f["capacidad"])),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color="blue", on_click=lambda e: abrir_modal_generico(e, "Editar Unidad")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e: abrir_modal_generico(e, "Eliminar Unidad")),
                ])),
            ])
        )
    tabla_flota = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Marca / Modelo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Capacidad Max", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=filas_flota
    )
    vista_flota = ft.Column([
        ft.Row([
            ft.TextField(hint_text="Buscar por placa...", prefix_icon=ft.Icons.SEARCH, expand=True),
            ft.Button("Nueva Unidad", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=lambda e: abrir_modal_generico(e, "Nueva Unidad"))
        ]), ft.Row([tabla_flota], scroll=ft.ScrollMode.AUTO)
    ])

    # -- VISTA: CLIENTES --
    filas_clientes = []
    for c in datos_clientes:
        filas_clientes.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(c["rif"])),
                ft.DataCell(ft.Text(c["razon_social"])),
                ft.DataCell(ft.Text(c["contacto"])),
                ft.DataCell(ft.Text(c["telefono"])),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color="blue", on_click=lambda e: abrir_modal_generico(e, "Editar Cliente")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e: abrir_modal_generico(e, "Eliminar Cliente")),
                ])),
            ])
        )
    tabla_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("RIF", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Razón Social", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Contacto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=filas_clientes
    )
    vista_clientes = ft.Column([
        ft.Row([
            ft.TextField(hint_text="Buscar cliente...", prefix_icon=ft.Icons.SEARCH, expand=True),
            ft.Button("Nuevo Cliente", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=lambda e: abrir_modal_generico(e, "Nuevo Cliente"))
        ]), ft.Row([tabla_clientes], scroll=ft.ScrollMode.AUTO)
    ])

    # -- VISTA: RUTAS --
    filas_rutas = []
    for r in datos_rutas:
        filas_rutas.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(r["codigo"])),
                ft.DataCell(ft.Text(r["origen"])),
                ft.DataCell(ft.Text(r["destino"])),
                ft.DataCell(ft.Text(r["costo"])),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color="blue", on_click=lambda e: abrir_modal_generico(e, "Editar Ruta")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e: abrir_modal_generico(e, "Eliminar Ruta")),
                ])),
            ])
        )
    tabla_rutas = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Código", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Origen", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Destino", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Costo Sugerido", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=filas_rutas
    )
    vista_rutas = ft.Column([
        ft.Row([
            ft.TextField(hint_text="Buscar ruta...", prefix_icon=ft.Icons.SEARCH, expand=True),
            ft.Button("Nueva Ruta", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=lambda e: abrir_modal_generico(e, "Nueva Ruta"))
        ]), ft.Row([tabla_rutas], scroll=ft.ScrollMode.AUTO)
    ])


    # ==========================================
    # 4. SISTEMA NATIVO DE PESTAÑAS
    # ==========================================
    pestanas_nativas = ft.Tabs(
        length=4,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Choferes", icon=ft.Icons.PEOPLE),
                        ft.Tab(label="Flota", icon=ft.Icons.LOCAL_SHIPPING),
                        ft.Tab(label="Clientes", icon=ft.Icons.BUSINESS),
                        ft.Tab(label="Rutas", icon=ft.Icons.MAP),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Container(content=vista_choferes, padding=20),
                        ft.Container(content=vista_flota, padding=20),
                        ft.Container(content=vista_clientes, padding=20),
                        ft.Container(content=vista_rutas, padding=20),
                    ],
                ),
            ],
        ),
    )

    # ==========================================
    # 5. RETORNO FINAL
    # ==========================================
    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column([
            ft.Text("Datos Maestros y Directorios", size=28, weight=ft.FontWeight.BOLD, color="black87"),
            ft.Divider(height=20, color="transparent"),
            pestanas_nativas
        ], expand=True)
    )