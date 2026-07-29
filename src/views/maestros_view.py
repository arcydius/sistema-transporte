import flet as ft
import datetime

from controllers.maestro_controller import (
    registrar_chofer, obtener_choferes, actualizar_chofer, eliminar_chofer,
    registrar_camion, obtener_camiones, actualizar_camion, eliminar_camion,
    registrar_remolque, obtener_remolques, actualizar_remolque, eliminar_remolque,
    registrar_cliente, obtener_clientes, actualizar_cliente, eliminar_cliente,
    registrar_ruta, obtener_rutas, actualizar_ruta, eliminar_ruta,
    registrar_tipo_mantenimiento, obtener_tipos_mantenimiento, actualizar_tipo_mantenimiento, eliminar_tipo_mantenimiento
)

def _fmt_fecha(val):
    if not val:
        return "N/A"
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%d/%m/%Y")
    return str(val)

def MaestrosView():
    # ==========================================
    # HERRAMIENTAS GLOBALES (NOTIFICACIONES Y FILTROS)
    # ==========================================
    def mostrar_mensaje(page, texto, color="green"):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto, color="white"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    filtro_numeros = ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,12}$", replacement_string="")
    filtro_letras = ft.InputFilter(allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$", replacement_string="")
    filtro_placa = ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9]*$", replacement_string="")
    filtro_decimal = ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string="")

    # ==========================================
    # MODAL DE ELIMINACIÓN REUTILIZABLE PARA TODOS
    # ==========================================
    def abrir_modal_eliminar(e, id_registro, nombre, funcion_eliminar, funcion_recargar):
        def cerrar(e_cerrar=None):
            modal_eliminar.open = False
            e.page.update()

        def confirmar(e_conf):
            exito, mensaje = funcion_eliminar(id_registro) 
            if exito:
                mostrar_mensaje(e.page, mensaje, "green")
                funcion_recargar() 
            else:
                mostrar_mensaje(e.page, mensaje, "red")
            cerrar()

        modal_eliminar = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text(f"¿Estás seguro de que deseas eliminar '{nombre}'?"),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=confirmar, bgcolor="red", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal_eliminar)
        modal_eliminar.open = True
        e.page.update()

    # ==========================================
    # 1. CHOFERES
    # ==========================================
    tabla_choferes = ft.DataTable(
        expand=True,
        column_spacing=40,
        columns=[
            ft.DataColumn(label=ft.Text("Cédula", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Teléfono / Contacto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_choferes():
        tabla_choferes.rows.clear()
        for c in obtener_choferes():
            tabla_choferes.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(c.cedula_identidad))),
                ft.DataCell(ft.Text(str(c.nombre_completo))),
                ft.DataCell(ft.Text(str(c.contacto) if str(c.contacto) else "N/A")),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_c=c.id_chofer, c_id=c.cedula_identidad, n=c.nombre_completo, t=c.contacto: abrir_modal_chofer(e, id_c, str(c_id), str(n), str(t) if str(t) else "")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_c=c.id_chofer, n=c.nombre_completo: abrir_modal_eliminar(e, id_c, n, eliminar_chofer, cargar_tabla_choferes)),
                ])),
            ]))

    def abrir_modal_chofer(e, id_chofer=None, cedula="", nombre="", telefono=""):
        tf_cedula = ft.TextField(label="Cédula", value=cedula, hint_text="Ej: 12345678", keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,8}$", replacement_string=""))
        tf_nombre = ft.TextField(label="Nombre Completo", value=nombre, input_filter=filtro_letras)
        tf_telefono = ft.TextField(label="Teléfono", value=telefono, hint_text="Ej: 04141234567", keyboard_type=ft.KeyboardType.NUMBER, input_filter=filtro_numeros)
        
        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_cedula.error = "Requerido" if not tf_cedula.value else None
            tf_nombre.error = "Requerido" if not tf_nombre.value else None
            tf_telefono.error = "Requerido" if not tf_telefono.value else None

            if not tf_cedula.value or not tf_nombre.value or not tf_telefono.value:
                e.page.update()
                return

            if id_chofer: exito, msj = actualizar_chofer(id_chofer, tf_cedula.value, tf_nombre.value, tf_telefono.value)
            else: exito, msj = registrar_chofer(tf_cedula.value, tf_nombre.value, tf_telefono.value)
            
            if exito:
                mostrar_mensaje(e.page, msj); cargar_tabla_choferes(); cerrar()
            else:
                mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Chofer" if id_chofer else "Nuevo Chofer"),
            content=ft.Column([tf_cedula, tf_nombre, tf_telefono], tight=True),
            actions=[ft.Button("Cancelar", on_click=cerrar), ft.Button("Actualizar" if id_chofer else "Guardar", on_click=guardar, bgcolor="blue", color="white")],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal); modal.open = True; e.page.update()

    vista_choferes = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar chofer...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nuevo Chofer", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_chofer)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_choferes], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # 2. CAMIONES (FLOTA)
    # ==========================================
    tabla_camiones = ft.DataTable(
        expand=True,
        column_spacing=30,
        columns=[
            ft.DataColumn(label=ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Alias", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Marca", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Venc. RCV", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Venc. Trimestre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_camiones():
        tabla_camiones.rows.clear()
        for c in obtener_camiones():
            rcv_str = _fmt_fecha(c.vencimiento_rcv)
            trim_str = _fmt_fecha(c.vencimiento_trimestre)
            tabla_camiones.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(c.placa))),
                ft.DataCell(ft.Text(str(c.alias_identificador) if str(c.alias_identificador) else "N/A")),
                ft.DataCell(ft.Text(str(c.marca) if str(c.marca) else "N/A")),
                ft.DataCell(ft.Text(rcv_str)),
                ft.DataCell(ft.Text(trim_str)),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_c=c.id_camion, p=c.placa, a=c.alias_identificador, m=c.marca, r=rcv_str, t=trim_str: abrir_modal_camion(e, id_c, str(p), str(a) if str(a) else "", str(m) if str(m) else "", r if r != "N/A" else "", t if t != "N/A" else "")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_c=c.id_camion, p=c.placa: abrir_modal_eliminar(e, id_c, p, eliminar_camion, cargar_tabla_camiones)),
                ])),
            ]))

    def abrir_modal_camion(e, id_camion=None, placa="", alias="", marca="", rcv="", trimestre=""):
        tf_placa = ft.TextField(label="Placa", value=placa, hint_text="Ej: A12B34C", max_length=7, input_filter=filtro_placa)
        tf_alias = ft.TextField(label="Alias / Identificador", value=alias)
        tf_marca = ft.TextField(label="Marca", value=marca)

        dp_rcv = ft.DatePicker(on_change=lambda ev: _set_fecha(tf_rcv, ev))
        dp_trimestre = ft.DatePicker(on_change=lambda ev: _set_fecha(tf_trimestre, ev))

        def _set_fecha(tf_target, ev):
            if ev.control.value:
                tf_target.value = ev.control.value.strftime("%d/%m/%Y")
                tf_target.update()

        def abrir_dp(dp_control, ev):
            if dp_control not in ev.page.overlay:
                ev.page.overlay.append(dp_control)
            dp_control.open = True
            ev.page.update()

        tf_rcv = ft.TextField(
            label="Vencimiento RCV", 
            value=rcv, 
            read_only=True, 
            hint_text="Seleccionar fecha",
            suffix=ft.Container(
                content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
                on_click=lambda ev: abrir_dp(dp_rcv, ev),
                margin=ft.Margin.only(right=5),
                tooltip="Seleccionar fecha RCV"
            )
        )

        tf_trimestre = ft.TextField(
            label="Vencimiento Trimestre", 
            value=trimestre, 
            read_only=True, 
            hint_text="Seleccionar fecha",
            suffix=ft.Container(
                content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
                on_click=lambda ev: abrir_dp(dp_trimestre, ev),
                margin=ft.Margin.only(right=5),
                tooltip="Seleccionar fecha Trimestre"
            )
        )

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_placa.error = "Requerido" if not tf_placa.value else None
            if not tf_placa.value: 
                e.page.update()
                return

            if id_camion:
                exito, msj = actualizar_camion(id_camion, tf_placa.value, tf_alias.value, tf_marca.value, tf_rcv.value, tf_trimestre.value)
            else:
                exito, msj = registrar_camion(tf_placa.value, tf_alias.value, tf_marca.value, tf_rcv.value, tf_trimestre.value)
            
            if exito:
                mostrar_mensaje(e.page, msj)
                cargar_tabla_camiones()
                cerrar()
            else:
                mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Camión" if id_camion else "Nuevo Camión"),
            content=ft.Column([
                tf_placa, tf_alias, tf_marca,
                tf_rcv, tf_trimestre
            ], tight=True),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Actualizar" if id_camion else "Guardar", on_click=guardar, bgcolor="blue", color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    vista_camiones = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar camión...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nuevo Camión", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_camion)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_camiones], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # 3. REMOLQUES (FLOTA)
    # ==========================================
    tabla_remolques = ft.DataTable(
        expand=True,
        column_spacing=35,
        columns=[
            ft.DataColumn(label=ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Alias / Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Venc. RCV", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Venc. Trimestre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_remolques():
        tabla_remolques.rows.clear()
        for r in obtener_remolques():
            rcv_str = _fmt_fecha(r.vencimiento_rcv)
            trim_str = _fmt_fecha(r.vencimiento_trimestre)
            tabla_remolques.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r.placa))),
                ft.DataCell(ft.Text(str(r.alias_identificador) if str(r.alias_identificador) else "N/A")),
                ft.DataCell(ft.Text(rcv_str)),
                ft.DataCell(ft.Text(trim_str)),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_r=r.id_remolque, p=r.placa, a=r.alias_identificador, r_rcv=rcv_str, t_tri=trim_str: abrir_modal_remolque(e, id_r, str(p), str(a) if str(a) else "", r_rcv if r_rcv != "N/A" else "", t_tri if t_tri != "N/A" else "")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_r=r.id_remolque, p=r.placa: abrir_modal_eliminar(e, id_r, p, eliminar_remolque, cargar_tabla_remolques)),
                ])),
            ]))

    def abrir_modal_remolque(e, id_remolque=None, placa="", alias="", rcv="", trimestre=""):
        tf_placa = ft.TextField(label="Placa Remolque", value=placa, hint_text="Ej: R12B34C", max_length=7, input_filter=filtro_placa)
        tf_alias = ft.TextField(label="Alias / Identificador", value=alias, hint_text="Ej: Batea de 3 ejes")

        dp_rcv = ft.DatePicker(on_change=lambda ev: _set_fecha(tf_rcv, ev))
        dp_trimestre = ft.DatePicker(on_change=lambda ev: _set_fecha(tf_trimestre, ev))

        def _set_fecha(tf_target, ev):
            if ev.control.value:
                tf_target.value = ev.control.value.strftime("%d/%m/%Y")
                tf_target.update()

        def abrir_dp(dp_control, ev):
            if dp_control not in ev.page.overlay:
                ev.page.overlay.append(dp_control)
            dp_control.open = True
            ev.page.update()

        tf_rcv = ft.TextField(
            label="Vencimiento RCV", 
            value=rcv, 
            read_only=True, 
            hint_text="Seleccionar fecha",
            suffix=ft.Container(
                content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
                on_click=lambda ev: abrir_dp(dp_rcv, ev),
                margin=ft.Margin.only(right=5),
                tooltip="Seleccionar fecha RCV"
            )
        )

        tf_trimestre = ft.TextField(
            label="Vencimiento Trimestre", 
            value=trimestre, 
            read_only=True, 
            hint_text="Seleccionar fecha",
            suffix=ft.Container(
                content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
                on_click=lambda ev: abrir_dp(dp_trimestre, ev),
                margin=ft.Margin.only(right=5),
                tooltip="Seleccionar fecha Trimestre"
            )
        )

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_placa.error = "Requerido" if not tf_placa.value else None
            if not tf_placa.value:
                e.page.update()
                return

            if id_remolque:
                exito, msj = actualizar_remolque(id_remolque, tf_placa.value, tf_alias.value, tf_rcv.value, tf_trimestre.value)
            else:
                exito, msj = registrar_remolque(tf_placa.value, tf_alias.value, tf_rcv.value, tf_trimestre.value)
            
            if exito:
                mostrar_mensaje(e.page, msj)
                cargar_tabla_remolques()
                cerrar()
            else:
                mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Remolque" if id_remolque else "Nuevo Remolque"),
            content=ft.Column([
                tf_placa, tf_alias,
                tf_rcv, tf_trimestre
            ], tight=True),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Actualizar" if id_remolque else "Guardar", on_click=guardar, bgcolor="blue", color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    vista_remolques = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar remolque...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nuevo Remolque", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_remolque)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_remolques], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # 4. CLIENTES
    # ==========================================
    tabla_clientes = ft.DataTable(
        expand=True,
        column_spacing=50,
        columns=[
            ft.DataColumn(label=ft.Text("Nombre Cliente / Empresa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Contacto Principal", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_clientes():
        tabla_clientes.rows.clear()
        for c in obtener_clientes():
            tabla_clientes.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(c.nombre_cliente))),
                ft.DataCell(ft.Text(str(c.contacto_principal) if str(c.contacto_principal) else "N/A")),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_c=c.id_cliente, n=c.nombre_cliente, t=c.contacto_principal: abrir_modal_cliente(e, id_c, str(n), str(t) if str(t) else "")),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_c=c.id_cliente, n=c.nombre_cliente: abrir_modal_eliminar(e, id_c, n, eliminar_cliente, cargar_tabla_clientes)),
                ])),
            ]))

    def abrir_modal_cliente(e, id_cliente=None, nombre="", contacto=""):
        tf_nombre = ft.TextField(label="Nombre / Empresa", value=nombre, input_filter=filtro_letras)
        tf_contacto = ft.TextField(label="Teléfono / Contacto", value=contacto)
        
        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_nombre.error = "Requerido" if not tf_nombre.value else None
            if not tf_nombre.value:
                e.page.update()
                return

            if id_cliente: exito, msj = actualizar_cliente(id_cliente, tf_nombre.value, tf_contacto.value)
            else: exito, msj = registrar_cliente(tf_nombre.value, tf_contacto.value)
            
            if exito: mostrar_mensaje(e.page, msj); cargar_tabla_clientes(); cerrar()
            else: mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Cliente" if id_cliente else "Nuevo Cliente"),
            content=ft.Column([tf_nombre, tf_contacto], tight=True),
            actions=[ft.Button("Cancelar", on_click=cerrar), ft.Button("Actualizar" if id_cliente else "Guardar", on_click=guardar, bgcolor="blue", color="white")],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal); modal.open = True; e.page.update()

    vista_clientes = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar cliente...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nuevo Cliente", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_cliente)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_clientes], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # 5. RUTAS
    # ==========================================
    tabla_rutas = ft.DataTable(
        expand=True,
        column_spacing=50,
        columns=[
            ft.DataColumn(label=ft.Text("Ruta / Trayecto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Costo Sugerido ($)", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_rutas():
        tabla_rutas.rows.clear()
        for r in obtener_rutas():
            tabla_rutas.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r.descripcion_trayecto))),
                ft.DataCell(ft.Text(f"${float(r.costo_unitario_sugerido or 0):,.2f}")),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_r=r.id_ruta, d=r.descripcion_trayecto, c=r.costo_unitario_sugerido: abrir_modal_ruta(e, id_r, str(d), str(c))),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_r=r.id_ruta, d=r.descripcion_trayecto: abrir_modal_eliminar(e, id_r, d, eliminar_ruta, cargar_tabla_rutas)),
                ])),
            ]))

    def abrir_modal_ruta(e, id_ruta=None, desc="", costo=""):
        tf_desc = ft.TextField(label="Descripción de la Ruta", value=desc)
        tf_costo = ft.TextField(label="Costo Sugerido ($)", value=costo, hint_text="Ej: 150.50", keyboard_type=ft.KeyboardType.NUMBER, input_filter=filtro_decimal)
        
        def cerrar(e_cerrar=None):
            modal.open = False; e.page.update()

        def guardar(e_guardar):
            tf_desc.error = "Requerido" if not tf_desc.value else None
            if not tf_desc.value: e.page.update(); return

            if id_ruta: exito, msj = actualizar_ruta(id_ruta, tf_desc.value, tf_costo.value)
            else: exito, msj = registrar_ruta(tf_desc.value, tf_costo.value)
            
            if exito: mostrar_mensaje(e.page, msj); cargar_tabla_rutas(); cerrar()
            else: mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Ruta" if id_ruta else "Nueva Ruta"),
            content=ft.Column([tf_desc, tf_costo], tight=True),
            actions=[ft.Button("Cancelar", on_click=cerrar), ft.Button("Actualizar" if id_ruta else "Guardar", on_click=guardar, bgcolor="blue", color="white")],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal); modal.open = True; e.page.update()

    vista_rutas = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar ruta...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nueva Ruta", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_ruta)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_rutas], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # 6. TIPOS DE MANTENIMIENTO
    # ==========================================
    tabla_mantenimientos = ft.DataTable(
        expand=True,
        column_spacing=60,
        columns=[
            ft.DataColumn(label=ft.Text("Tipo de Servicio / Mantenimiento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ], rows=[]
    )

    def cargar_tabla_mantenimientos():
        tabla_mantenimientos.rows.clear()
        for t in obtener_tipos_mantenimiento():
            tabla_mantenimientos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(t.nombre_tipo))),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, id_t=t.id_tipo, n=t.nombre_tipo: abrir_modal_mantenimiento(e, id_t, str(n))),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", tooltip="Eliminar", on_click=lambda e, id_t=t.id_tipo, n=t.nombre_tipo: abrir_modal_eliminar(e, id_t, n, eliminar_tipo_mantenimiento, cargar_tabla_mantenimientos)),
                ])),
            ]))

    def abrir_modal_mantenimiento(e, id_tipo=None, nombre=""):
        tf_nombre = ft.TextField(label="Nombre del Servicio", value=nombre, hint_text="Ej: Cambio de Aceite", input_filter=filtro_letras)
        
        def cerrar(e_cerrar=None):
            modal.open = False; e.page.update()

        def guardar(e_guardar):
            tf_nombre.error = "Requerido" if not tf_nombre.value else None
            if not tf_nombre.value: e.page.update(); return

            if id_tipo: exito, msj = actualizar_tipo_mantenimiento(id_tipo, tf_nombre.value)
            else: exito, msj = registrar_tipo_mantenimiento(tf_nombre.value)
            
            if exito: mostrar_mensaje(e.page, msj); cargar_tabla_mantenimientos(); cerrar()
            else: mostrar_mensaje(e.page, msj, "red") 

        modal = ft.AlertDialog(
            modal=True, title=ft.Text("Editar Mantenimiento" if id_tipo else "Nuevo Mantenimiento"),
            content=ft.Column([tf_nombre], tight=True),
            actions=[ft.Button("Cancelar", on_click=cerrar), ft.Button("Actualizar" if id_tipo else "Guardar", on_click=guardar, bgcolor="blue", color="white")],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal); modal.open = True; e.page.update()

    vista_mantenimientos = ft.Column([
        ft.Row([ft.TextField(hint_text="Buscar tipo de mantenimiento...", prefix_icon=ft.Icons.SEARCH, expand=True), ft.Button("Nuevo Servicio", icon=ft.Icons.ADD, bgcolor="#1976d2", color="white", on_click=abrir_modal_mantenimiento)]), 
        ft.Container(height=5),
        ft.Container(content=ft.Row([tabla_mantenimientos], scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START), expand=True)
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    # ==========================================
    # CARGA INICIAL Y ENSAMBLAJE DE PESTAÑAS
    # ==========================================
    cargar_tabla_choferes()
    cargar_tabla_camiones()
    cargar_tabla_remolques()
    cargar_tabla_clientes()
    cargar_tabla_rutas()
    cargar_tabla_mantenimientos()

    pestanas_nativas = ft.Tabs(
        length=6,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Choferes", icon=ft.Icons.PEOPLE),
                        ft.Tab(label="Camiones", icon=ft.Icons.LOCAL_SHIPPING),
                        ft.Tab(label="Remolques", icon=ft.Icons.RV_HOOKUP),
                        ft.Tab(label="Clientes", icon=ft.Icons.BUSINESS),
                        ft.Tab(label="Rutas", icon=ft.Icons.MAP),
                        ft.Tab(label="Mantenimientos", icon=ft.Icons.BUILD),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Container(content=vista_choferes, padding=20),
                        ft.Container(content=vista_camiones, padding=20),
                        ft.Container(content=vista_remolques, padding=20),
                        ft.Container(content=vista_clientes, padding=20),
                        ft.Container(content=vista_rutas, padding=20),
                        ft.Container(content=vista_mantenimientos, padding=20),
                    ],
                ),
            ],
        ),
    )

    return ft.Container(
        padding=20, expand=True,
        content=ft.Column([
            ft.Text("Datos Maestros y Directorios", size=28, weight=ft.FontWeight.BOLD, color="black87"),
            ft.Divider(height=20, color="transparent"),
            pestanas_nativas
        ], expand=True)
    )