import flet as ft
import datetime
from controllers.maestro_controller import (
    obtener_camiones,
    obtener_clientes,
    obtener_rutas,
    obtener_choferes,
    obtener_remolques,
    registrar_flete,
    obtener_viajes_filtrados,
    actualizar_estatus_viaje,
    eliminar_viaje
)
from utils.pdf_generator import generar_pdf_reporte_fletes, seleccionar_carpeta_destino, abrir_pdf

def _formatear_fecha(fecha, fmt="%d/%m/%Y"):
    if not fecha:
        return "N/A"
    if isinstance(fecha, str):
        try:
            d = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
            return d.strftime(fmt)
        except Exception:
            return fecha
    try:
        return fecha.strftime(fmt)
    except Exception:
        return str(fecha)

class FletesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # --- Banner de Mensajes ---
        self.banner_mensaje = ft.Text(value="", color="green", size=14, weight=ft.FontWeight.BOLD)
        
        # --- Componentes de Totales ---
        self.txt_costo_ruta = ft.Text("Costo Ruta (1 viaje): $0.00", size=14, color="black54")
        self.txt_costo_gasoil_total = ft.Text("Costo Total Gasoil: $0.00", size=14, color="orange")
        self.txt_total_flete = ft.Text("Total del Flete: $0.00", size=22, weight=ft.FontWeight.BOLD, color="#1976d2")

        padding_uniforme = ft.Padding.symmetric(vertical=10, horizontal=12)

        # -- Pestaña 1: Componentes de Registro --
        self.fecha_tf = ft.TextField(
            label="Fecha de Operación", 
            value=datetime.datetime.now().strftime("%d/%m/%Y"), 
            read_only=True,  # type: ignore
            expand=1,
            content_padding=padding_uniforme,
            suffix=ft.Container(
                content=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#1976d2", size=20),
                on_click=self.abrir_calendario,
                padding=0, 
                margin=ft.Margin.only(right=5),
                tooltip="Seleccionar fecha"
            )
        )
        
        self.cliente_dd = ft.Dropdown(label="Cliente Solicitante", options=[], expand=1, dense=True, content_padding=padding_uniforme)
        
        self.cantidad_tf = ft.TextField(
            label="Cantidad de Viajes", 
            value="1", 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme,
            on_change=self.recalcular_total
        )

        self.ruta_dd = ft.Dropdown(label="Ruta Ejecutada", options=[], expand=2, dense=True, content_padding=padding_uniforme, on_select=self.recalcular_total)

        self.estatus_dd = ft.Dropdown(
            label="Estatus de Pago Cliente", 
            options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Pagado")], 
            value="Pendiente",
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme
        )

        self.chofer_dd = ft.Dropdown(label="Chofer Asignado", options=[], expand=1, dense=True, content_padding=padding_uniforme)
        self.camion_dd = ft.Dropdown(label="Camión", options=[], expand=1, dense=True, content_padding=padding_uniforme)
        self.remolque_dd = ft.Dropdown(label="Remolque (Opcional)", options=[], expand=1, dense=True, content_padding=padding_uniforme)

        self.gasoil_tf = ft.TextField(
            label="Gasoil Consumido (Lts)", 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme,
            on_change=self.recalcular_total
        )

        self.precio_gasoil_tf = ft.TextField(
            label="Precio por Litro Gasoil ($)", 
            value="0.50",
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme,
            on_change=self.recalcular_total
        )
        
        self.mora_tf = ft.TextField(
            label="Mora / Espera ($)", 
            value="0", 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme,
            on_change=self.recalcular_total
        )

        self.calendario = ft.DatePicker(
            on_change=self.fecha_seleccionada,
            first_date=datetime.datetime(2024, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            help_text="Seleccione la fecha del flete"
        )

        # -- Pestaña 2: Componentes de Historial y Filtros --
        self.dd_filtro_chofer = ft.Dropdown(
            label="Filtrar por Chofer",
            expand=True,
            options=[ft.dropdown.Option(key="all", text="Todos los Choferes")]
        )

        self.dp_desde_filtro = ft.DatePicker(on_change=self._on_fecha_desde_filtro_change)
        self.dp_hasta_filtro = ft.DatePicker(on_change=self._on_fecha_hasta_filtro_change)

        self.txt_fecha_desde_filtro = ft.TextField(label="Fecha Desde", read_only=True, expand=True)  # type: ignore
        self.btn_picker_desde_filtro = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            tooltip="Seleccionar fecha desde",
            on_click=lambda e: self.abrir_calendario_filtro(self.dp_desde_filtro, e)
        )

        self.txt_fecha_hasta_filtro = ft.TextField(label="Fecha Hasta", read_only=True, expand=True)  # type: ignore
        self.btn_picker_hasta_filtro = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            tooltip="Seleccionar fecha hasta",
            on_click=lambda e: self.abrir_calendario_filtro(self.dp_hasta_filtro, e)
        )

        self.btn_filtrar_historial = ft.Button(
            content=ft.Text("Aplicar Filtros"),
            icon=ft.Icons.FILTER_ALT,
            bgcolor="#1976d2",
            color="white",
            on_click=self.aplicar_filtros_historial
        )

        self.btn_limpiar_filtros = ft.Button(
            content=ft.Text("Limpiar Filtros"),
            icon=ft.Icons.CLEAR_ALL,
            on_click=self.limpiar_filtros_historial
        )

        self.file_picker_reporte = ft.FilePicker()
        self.btn_exportar_reporte = ft.Button(
            content=ft.Text("Generar Reporte PDF"),
            icon=ft.Icons.PICTURE_AS_PDF,
            bgcolor="#2E7D32",
            color="white",
            on_click=self.generar_reporte_fletes_click
        )

        self.tabla_historial_viajes = ft.DataTable(  # type: ignore
            expand=True,
            column_spacing=30,
            columns=[
                ft.DataColumn(label=ft.Text("N°", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Chofer", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Ruta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Cant.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Gasoil ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Mora ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Total ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Estatus Cliente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Estado Nómina", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.content = self.inicializar_vista()

    def abrir_calendario_filtro(self, date_picker, e):
        if e.page:
            if date_picker not in e.page.overlay:
                e.page.overlay.append(date_picker)
            date_picker.open = True
            e.page.update()

    def _on_fecha_desde_filtro_change(self, e):
        if hasattr(self.dp_desde_filtro, 'value') and self.dp_desde_filtro.value:
            self.txt_fecha_desde_filtro.value = _formatear_fecha(self.dp_desde_filtro.value, "%Y-%m-%d")
            if hasattr(e, 'page') and e.page:
                e.page.update()

    def _on_fecha_hasta_filtro_change(self, e):
        if hasattr(self.dp_hasta_filtro, 'value') and self.dp_hasta_filtro.value:
            self.txt_fecha_hasta_filtro.value = _formatear_fecha(self.dp_hasta_filtro.value, "%Y-%m-%d")
            if hasattr(e, 'page') and e.page:
                e.page.update()

    def inicializar_vista(self):
        self.cargar_datos_bd()

        # Construcción Pestaña 1: Formulario de Registro
        pestana_registro = ft.Container(
            padding=15,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("1. Datos del Servicio", weight=ft.FontWeight.BOLD, color="#1976d2"),
                                ft.Divider(),
                                ft.Row([self.fecha_tf, self.cliente_dd, self.cantidad_tf]),
                                ft.Row([self.ruta_dd, self.estatus_dd]),
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
                                ft.Row([self.chofer_dd, self.camion_dd, self.remolque_dd]),
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
                                ft.Row([self.gasoil_tf, self.precio_gasoil_tf, self.mora_tf]),
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
                                ft.Column([self.txt_costo_ruta, self.txt_costo_gasoil_total, self.txt_total_flete]),
                                ft.Row([
                                    ft.Button("Limpiar Formulario", icon=ft.Icons.DELETE_OUTLINE, on_click=self.limpiar_formulario),
                                    ft.Button("Guardar Flete", icon=ft.Icons.SAVE, bgcolor="#1976d2", color="white", on_click=self.guardar_flete_click),
                                ])
                            ]
                        )
                    )
                ]
            )
        )

        # Construcción Pestaña 2: Historial y Gestión de Viajes
        pestana_historial = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    self.dd_filtro_chofer,
                    ft.Row([self.txt_fecha_desde_filtro, self.btn_picker_desde_filtro], expand=True),
                    ft.Row([self.txt_fecha_hasta_filtro, self.btn_picker_hasta_filtro], expand=True),
                ]),
                ft.Row([self.btn_filtrar_historial, self.btn_limpiar_filtros, self.btn_exportar_reporte], alignment=ft.MainAxisAlignment.END, spacing=10),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Row([self.tabla_historial_viajes], expand=True, scroll=ft.ScrollMode.AUTO),
                    border=ft.Border.all(1, "#E0E0E0"),
                    border_radius=8,
                    padding=5,
                    expand=True
                )
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

        self.pestanas_contenido = [pestana_registro, pestana_historial]
        self.contenedor_pestana = ft.Container(content=self.pestanas_contenido[0], expand=True)

        self.icon_tab_registro = ft.Icon(ft.Icons.LOCAL_SHIPPING, color="white", size=18)
        self.lbl_tab_registro = ft.Text("Registrar Flete", color="white", weight=ft.FontWeight.BOLD, size=14)

        self.btn_tab_registro = ft.Container(
            content=ft.Row([
                self.icon_tab_registro,
                self.lbl_tab_registro
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="#1976d2",
            padding=ft.Padding.symmetric(vertical=10, horizontal=20),
            border_radius=8,
            ink=True,
            on_click=lambda e: self.cambiar_pestana(0, e)
        )

        self.icon_tab_historial = ft.Icon(ft.Icons.LIST_ALT, color="#555555", size=18)
        self.lbl_tab_historial = ft.Text("Historial y Gestión de Viajes", color="#555555", weight=ft.FontWeight.BOLD, size=14)

        self.btn_tab_historial = ft.Container(
            content=ft.Row([
                self.icon_tab_historial,
                self.lbl_tab_historial
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="#E0E0E0",
            padding=ft.Padding.symmetric(vertical=10, horizontal=20),
            border_radius=8,
            ink=True,
            on_click=lambda e: self.cambiar_pestana(1, e)
        )

        self.tabs_bar = ft.Row([self.btn_tab_registro, self.btn_tab_historial], spacing=10)

        return ft.Column([
            ft.Row([
                ft.Text("Gestión de Fletes y Viajes", size=26, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refrescar datos de la base de datos",
                    icon_color="#1976d2",
                    on_click=self.refrescar_click
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.banner_mensaje,
            ft.Container(height=5),
            self.tabs_bar,
            ft.Container(height=10),
            self.contenedor_pestana
        ], expand=True)

    def cambiar_pestana(self, indice, e):
        self.contenedor_pestana.content = self.pestanas_contenido[indice]

        if indice == 0:
            self.btn_tab_registro.bgcolor = "#1976d2"
            self.icon_tab_registro.color = "white"
            self.lbl_tab_registro.color = "white"

            self.btn_tab_historial.bgcolor = "#E0E0E0"
            self.icon_tab_historial.color = "#555555"
            self.lbl_tab_historial.color = "#555555"
        else:
            self.btn_tab_registro.bgcolor = "#E0E0E0"
            self.icon_tab_registro.color = "#555555"
            self.lbl_tab_registro.color = "#555555"

            self.btn_tab_historial.bgcolor = "#1976d2"
            self.icon_tab_historial.color = "white"
            self.lbl_tab_historial.color = "white"

            self.cargar_tabla_historial_viajes(e.page if hasattr(e, 'page') else None)

        if hasattr(e, 'page') and e.page:
            e.page.update()
        else:
            self.update()

    def cargar_datos_bd(self):
        try:
            # 1. Clientes
            try:
                clientes = obtener_clientes()
            except Exception:
                clientes = []
            
            self.cliente_dd.options.clear()
            if clientes:
                for c in clientes:
                    nombre = getattr(c, 'nombre_cliente', str(c))
                    id_c = str(getattr(c, 'id_cliente', nombre))
                    self.cliente_dd.options.append(ft.dropdown.Option(key=id_c, text=nombre))
            else:
                self.cliente_dd.options = [ft.dropdown.Option(key="0", text="Sin clientes registrados")]

            # 2. Rutas
            try:
                rutas = obtener_rutas()
            except Exception:
                rutas = []

            self.ruta_dd.options.clear()
            if rutas:
                for r in rutas:
                    nombre_ruta = getattr(r, 'descripcion_trayecto', f"Ruta {getattr(r, 'id_ruta', '')}")
                    costo = float(getattr(r, 'costo_unitario_sugerido', 0.0) or 0.0)
                    id_r = str(getattr(r, 'id_ruta', nombre_ruta))
                    self.ruta_dd.options.append(ft.dropdown.Option(key=id_r, text=nombre_ruta, data=costo))
            else:
                self.ruta_dd.options = [ft.dropdown.Option(key="0", text="Sin rutas registradas", data=0.0)]

            # 3. Choferes
            try:
                choferes = obtener_choferes()
            except Exception:
                choferes = []

            self.chofer_dd.options.clear()
            self.dd_filtro_chofer.options.clear()
            self.dd_filtro_chofer.options.append(ft.dropdown.Option(key="all", text="Todos los Choferes"))

            if choferes:
                for ch in choferes:
                    nombre_ch = str(getattr(ch, 'nombre_completo', str(ch)))
                    id_ch = str(getattr(ch, 'id_chofer', nombre_ch))
                    self.chofer_dd.options.append(ft.dropdown.Option(key=id_ch, text=nombre_ch))
                    self.dd_filtro_chofer.options.append(ft.dropdown.Option(key=id_ch, text=nombre_ch))
            else:
                self.chofer_dd.options = [ft.dropdown.Option(key="0", text="Sin choferes registrados")]

            # 4. Camiones
            try:
                camiones = obtener_camiones()
            except Exception:
                camiones = []

            self.camion_dd.options.clear()
            if camiones:
                for ca in camiones:
                    texto_camion = f"{getattr(ca, 'marca', 'Camión')} - {getattr(ca, 'placa', 'S/P')}"
                    id_ca = str(getattr(ca, 'id_camion', texto_camion))
                    self.camion_dd.options.append(ft.dropdown.Option(key=id_ca, text=texto_camion))
            else:
                self.camion_dd.options = [ft.dropdown.Option(key="0", text="Sin camiones registrados")]

            # 5. Remolques
            try:
                remolques = obtener_remolques()
            except Exception:
                remolques = []

            self.remolque_dd.options.clear()
            if remolques:
                for re in remolques:
                    texto_remolque = f"Remolque - {getattr(re, 'placa', 'S/P')}"
                    id_re = str(getattr(re, 'id_remolque', texto_remolque))
                    self.remolque_dd.options.append(ft.dropdown.Option(key=id_re, text=texto_remolque))
            else:
                self.remolque_dd.options = [ft.dropdown.Option(key="none", text="Ninguno / Sin remolque")]

            self.banner_mensaje.value = ""
        except Exception as ex:
            print(f"Error cargando entidades en fletes: {ex}")
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"⚠️ Error al conectar con la base de datos: {str(ex)}"

    def cargar_tabla_historial_viajes(self, page_context=None):
        chofer_id = self.dd_filtro_chofer.value
        f_desde = self.txt_fecha_desde_filtro.value
        f_hasta = self.txt_fecha_hasta_filtro.value

        viajes = obtener_viajes_filtrados(
            id_chofer=chofer_id,
            fecha_desde=f_desde,
            fecha_hasta=f_hasta
        )

        self.tabla_historial_viajes.rows.clear()
        if viajes:
            for v in viajes:
                id_v = int(getattr(v, 'id_viaje'))
                f_op = _formatear_fecha(getattr(v, 'fecha_operacion', None), "%d/%m/%Y")
                
                ch_obj = getattr(v, 'chofer', None)
                ch_name = str(getattr(ch_obj, 'nombre_completo', 'N/A')) if ch_obj else "N/A"
                
                cl_obj = getattr(v, 'cliente', None)
                cl_name = str(getattr(cl_obj, 'nombre_cliente', 'N/A')) if cl_obj else "N/A"
                
                rt_obj = getattr(v, 'ruta', None)
                rt_name = str(getattr(rt_obj, 'descripcion_trayecto', 'N/A')) if rt_obj else "N/A"

                cant = int(getattr(v, 'cantidad_fletes', 1) or 1)
                costo_u = float(getattr(v, 'costo_unitario_aplicado', 0.0) or 0.0)
                mora = float(getattr(v, 'monto_mora_espera', 0.0) or 0.0)
                gasoil_tot = float(getattr(v, 'costo_total_gasoil', 0.0) or 0.0)
                total_flete = (cant * costo_u) + mora

                estatus_cliente = str(getattr(v, 'estatus_pago_cliente', 'Pendiente'))
                id_nomina = getattr(v, 'id_nomina_pago', None)
                estado_nomina = f"NOM-{int(id_nomina):05d}" if id_nomina else "Pendiente"

                # Color de badges
                color_estatus = "green" if estatus_cliente.lower() == "pagado" else "orange"
                color_nomina = "blue" if id_nomina else "grey"

                self.tabla_historial_viajes.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"#{id_v}", weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(f_op)),
                        ft.DataCell(ft.Text(ch_name, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(cl_name)),
                        ft.DataCell(ft.Text(rt_name)),
                        ft.DataCell(ft.Text(str(cant))),
                        ft.DataCell(ft.Text(f"${gasoil_tot:,.2f}", color="orange")),
                        ft.DataCell(ft.Text(f"${mora:,.2f}")),
                        ft.DataCell(ft.Text(f"${total_flete:,.2f}", weight=ft.FontWeight.BOLD, color="blue")),
                        ft.DataCell(ft.Text(estatus_cliente, color=color_estatus, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(estado_nomina, color=color_nomina)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color="blue",
                                    tooltip="Editar Estatus de Pago Cliente",
                                    on_click=lambda e, id_viaje=id_v, est=estatus_cliente: self.abrir_modal_editar_estatus(e, id_viaje, est)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color="red",
                                    tooltip="Eliminar Viaje No Realizado",
                                    on_click=lambda e, id_viaje=id_v: self.abrir_modal_eliminar_viaje(e, id_viaje)
                                )
                            ])
                        )
                    ])
                )
        if page_context:
            page_context.update()

    def aplicar_filtros_historial(self, e):
        self.cargar_tabla_historial_viajes(e.page)

    def limpiar_filtros_historial(self, e):
        self.dd_filtro_chofer.value = "all"
        self.txt_fecha_desde_filtro.value = ""
        self.txt_fecha_hasta_filtro.value = ""
        self.cargar_tabla_historial_viajes(e.page)

    def generar_reporte_fletes_click(self, e):
        page = e.page if hasattr(e, 'page') and e.page else getattr(self, 'page', None)

        carpeta_destino = seleccionar_carpeta_destino(
            titulo="Seleccionar carpeta para guardar el reporte de Fletes / Viajes"
        )

        if not carpeta_destino:
            if page:
                self.mostrar_mensaje(page, "Generación de reporte cancelada (no se seleccionó carpeta).", "orange")
            return

        chofer_id = self.dd_filtro_chofer.value
        f_desde = self.txt_fecha_desde_filtro.value
        f_hasta = self.txt_fecha_hasta_filtro.value

        chofer_nombre = None
        if chofer_id and chofer_id != "all":
            opcion = next((opt for opt in self.dd_filtro_chofer.options if opt.key == chofer_id), None)
            if opcion:
                chofer_nombre = opcion.text

        viajes = obtener_viajes_filtrados(
            id_chofer=chofer_id,
            fecha_desde=f_desde,
            fecha_hasta=f_hasta
        )

        try:
            pdf_path = generar_pdf_reporte_fletes(
                viajes=viajes,
                filtro_chofer_nombre=chofer_nombre,
                fecha_desde=f_desde,
                fecha_hasta=f_hasta,
                output_dir=carpeta_destino
            )
            abrir_pdf(pdf_path)
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = f"✅ Reporte PDF guardado exitosamente en: {pdf_path}"
            if page:
                self.mostrar_mensaje(page, f"Reporte de Fletes guardado en: {pdf_path}", "green")
                page.update()
        except Exception as ex:
            print(f"Error generando reporte PDF de fletes: {ex}")
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ Error generando reporte PDF: {str(ex)}"
            if page:
                self.mostrar_mensaje(page, f"Error al generar reporte PDF: {ex}", "red")
                page.update()

    def abrir_modal_editar_estatus(self, e, id_viaje: int, estatus_actual: str):
        dd_nuevo_estatus = ft.Dropdown(
            label="Estatus de Pago del Cliente",
            options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Pagado")],
            value=estatus_actual if estatus_actual in ["Pendiente", "Pagado"] else "Pendiente",
            expand=True
        )

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            exito, msj = actualizar_estatus_viaje(id_viaje, dd_nuevo_estatus.value or "Pendiente")
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                self.cargar_tabla_historial_viajes(e.page)
                cerrar()
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
                e.page.update()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Estatus del Viaje #{id_viaje}"),
            content=ft.Column([
                ft.Text(f"Modifique el estado de cobro al cliente para el viaje N° #{id_viaje}:"),
                ft.Container(height=10),
                dd_nuevo_estatus
            ], tight=True, width=400),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Actualizar", bgcolor="blue", color="white", on_click=guardar)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def abrir_modal_eliminar_viaje(self, e, id_viaje: int):
        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def confirmar(e_conf):
            exito, msj = eliminar_viaje(id_viaje)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                self.cargar_tabla_historial_viajes(e.page)
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
            cerrar()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Confirmar Eliminación de Viaje #{id_viaje}", color="red"),
            content=ft.Text(f"¿Está seguro de que desea eliminar el registro del Viaje N° #{id_viaje}?\n\nEsta acción es irreversible y removerá el flete del sistema."),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Eliminar Viaje", icon=ft.Icons.DELETE_FOREVER, bgcolor="red", color="white", on_click=confirmar)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def refrescar_click(self, e):
        self.cargar_datos_bd()
        self.cargar_tabla_historial_viajes(e.page)
        self.banner_mensaje.color = "green"
        self.banner_mensaje.value = "✅ Listas y datos de viajes actualizados."
        if hasattr(e, 'page') and e.page:
            e.page.update()

    def recalcular_total(self, e=None):
        try:
            cant = int(self.cantidad_tf.value) if self.cantidad_tf.value else 1
            if cant < 1:
                cant = 1
        except ValueError:
            cant = 1

        costo_unitario = 0.0
        if self.ruta_dd.value:
            opcion_seleccionada = next((opt for opt in self.ruta_dd.options if opt.key == self.ruta_dd.value), None)
            if opcion_seleccionada and opcion_seleccionada.data is not None:
                try:
                    costo_unitario = float(opcion_seleccionada.data)
                except Exception:
                    costo_unitario = 0.0

        costo_ruta_subtotal = cant * costo_unitario

        try:
            litros = float(self.gasoil_tf.value) if self.gasoil_tf.value else 0.0
        except ValueError:
            litros = 0.0

        try:
            precio_l = float(self.precio_gasoil_tf.value) if self.precio_gasoil_tf.value else 0.0
        except ValueError:
            precio_l = 0.0

        total_gasoil = litros * precio_l

        try:
            mora = float(self.mora_tf.value) if self.mora_tf.value else 0.0
        except ValueError:
            mora = 0.0

        total_flete = costo_ruta_subtotal + mora

        self.txt_costo_ruta.value = f"Costo Ruta ({cant} viaje{'s' if cant > 1 else ''}): ${costo_ruta_subtotal:.2f}"
        self.txt_costo_gasoil_total.value = f"Costo Total Gasoil: ${total_gasoil:.2f}"
        self.txt_total_flete.value = f"Total del Flete: ${total_flete:.2f}"
        
        if e and hasattr(e, 'page') and e.page:
            self.txt_costo_ruta.update()
            self.txt_costo_gasoil_total.update()
            self.txt_total_flete.update()

    def fecha_seleccionada(self, e):
        if e.control.value:
            self.fecha_tf.value = e.control.value.strftime("%d/%m/%Y")
            self.fecha_tf.update()

    def abrir_calendario(self, e):
        if self.calendario not in e.page.overlay:
            e.page.overlay.append(self.calendario)
        self.calendario.open = True
        e.page.update()

    def mostrar_mensaje(self, page, texto, color="green"):
        if page:
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE if color == "green" else ft.Icons.ERROR, color="white"),
                    ft.Text(texto, color="white", weight=ft.FontWeight.BOLD)
                ]),
                bgcolor=color,
                duration=4000
            )
            page.snack_bar.open = True
            page.update()

    def limpiar_formulario(self, e, limpiar_banner=True):
        self.fecha_tf.value = datetime.datetime.now().strftime("%d/%m/%Y")
        self.cliente_dd.value = None
        self.cantidad_tf.value = "1"
        self.ruta_dd.value = None
        self.estatus_dd.value = "Pendiente"
        self.chofer_dd.value = None
        self.camion_dd.value = None
        self.remolque_dd.value = None
        self.gasoil_tf.value = ""
        self.precio_gasoil_tf.value = "0.50"
        self.mora_tf.value = "0"
        self.txt_costo_ruta.value = "Costo Ruta (1 viaje): $0.00"
        self.txt_costo_gasoil_total.value = "Costo Total Gasoil: $0.00"
        self.txt_total_flete.value = "Total del Flete: $0.00"
        if limpiar_banner:
            self.banner_mensaje.value = ""
        if hasattr(e, 'page') and e.page:
            e.page.update()

    def guardar_flete_click(self, e):
        if not self.cliente_dd.value or not self.ruta_dd.value or not self.camion_dd.value:
            msj_err = "⚠️ Por favor complete los campos obligatorios (Cliente, Ruta y Camión)."
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_err
            self.mostrar_mensaje(e.page, msj_err, "red")
            return

        costo_unitario = 0.0
        if self.ruta_dd.value:
            opcion_seleccionada = next((opt for opt in self.ruta_dd.options if opt.key == self.ruta_dd.value), None)
            if opcion_seleccionada and opcion_seleccionada.data is not None:
                try:
                    costo_unitario = float(opcion_seleccionada.data)
                except Exception:
                    costo_unitario = 0.0

        try:
            cant_fletes = int(self.cantidad_tf.value) if self.cantidad_tf.value else 1
            if cant_fletes < 1:
                cant_fletes = 1
        except (ValueError, TypeError):
            cant_fletes = 1

        try:
            exito, msg = registrar_flete(
                id_cliente=self.cliente_dd.value,
                id_ruta=self.ruta_dd.value,
                id_chofer=self.chofer_dd.value,
                id_camion=self.camion_dd.value,
                id_remolque=self.remolque_dd.value if self.remolque_dd.value != "none" else None,
                estatus=self.estatus_dd.value,
                gasoil=self.gasoil_tf.value,
                precio_gasoil=self.precio_gasoil_tf.value,
                mora=self.mora_tf.value,
                costo_unitario=costo_unitario,
                cantidad_fletes=cant_fletes
            )

            if exito:
                msj_exito = f"✅ {msg}"
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = msj_exito
                self.mostrar_mensaje(e.page, msj_exito, "green")
                self.limpiar_formulario(e, limpiar_banner=False)
                # Actualizar tabla de historial si está cargada
                self.cargar_tabla_historial_viajes()
            else:
                msj_fail = f"❌ {msg}"
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = msj_fail
                self.mostrar_mensaje(e.page, msj_fail, "red")
            e.page.update()
        except Exception as ex:
            print(f"[-] Error al guardar flete: {ex}")
            msj_ex = f"⚠️ Error en BD: {str(ex)}"
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_ex
            self.mostrar_mensaje(e.page, msj_ex, "red")
            e.page.update()