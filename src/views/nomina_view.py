import flet as ft
from datetime import datetime, date
from controllers.maestro_controller import (
    obtener_choferes, 
    obtener_nominas, 
    registrar_nomina, 
    actualizar_nomina, 
    eliminar_nomina
)

def _formatear_fecha(val, formato="%d/%m/%Y"):
    """Convierte objetos date/datetime o cadenas de fecha de manera segura sin activar __bool__ de SQLAlchemy Column."""
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime(formato)
    return str(val)

class NominaView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.historial_completo = []
        self.id_a_eliminar = None 
        self.id_a_editar = None   
        
        # --- Componentes Principales ---
        self.txt_buscar = ft.TextField(
            hint_text="Buscar por chofer o fecha...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filtrar_datos,
            expand=True,
            border_radius=8
        )
        
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Emisión", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Chofer", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Período", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Ingresos ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Gasoil ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Neto ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        # --- Componentes del Formulario y Selectores de Fecha ---
        self.dd_chofer = ft.Dropdown(label="Seleccionar Chofer", expand=True, options=[])
        
        # Objetos DatePicker de Flet
        self.dp_emision = ft.DatePicker(on_change=self.cambiar_fecha_emision)
        self.dp_desde = ft.DatePicker(on_change=self.cambiar_fecha_desde)
        self.dp_hasta = ft.DatePicker(on_change=self.cambiar_fecha_hasta)

        # Campos de Fecha (Bloqueados para escritura manual)
        self.txt_fecha_emision = ft.TextField(label="Fecha Emisión", read_only=True, expand=True)
        self.btn_picker_emision = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH, 
            tooltip="Seleccionar fecha de emisión",
            on_click=lambda e: self.abrir_calendario(self.dp_emision, e)
        )
        
        self.txt_periodo_desde = ft.TextField(label="Período Desde", read_only=True, expand=True)
        self.btn_picker_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH, 
            tooltip="Seleccionar fecha inicial",
            on_click=lambda e: self.abrir_calendario(self.dp_desde, e)
        )
        
        self.txt_periodo_hasta = ft.TextField(label="Período Hasta", read_only=True, expand=True)
        self.btn_picker_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH, 
            tooltip="Seleccionar fecha final",
            on_click=lambda e: self.abrir_calendario(self.dp_hasta, e)
        )

        # Campos Numéricos Decimales Restringidos
        filtro_decimal = ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string="")

        self.txt_ingresos = ft.TextField(
            label="Total Ingresos Fletes ($)", 
            value="0.00", 
            hint_text="Ej: 500.00",
            expand=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=filtro_decimal,
            on_change=self.calcular_neto_automatico
        )
        self.txt_gasoil = ft.TextField(
            label="Total Costo Gasoil ($)", 
            value="0.00", 
            hint_text="Ej: 100.00",
            expand=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=filtro_decimal,
            on_change=self.calcular_neto_automatico
        )
        self.txt_neto = ft.TextField(
            label="Monto Neto Comisión ($)", 
            value="0.00", 
            hint_text="Ej: 400.00",
            expand=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=filtro_decimal
        )

        self.btn_cancelar = ft.TextButton(content=ft.Text("Cancelar"), on_click=self.cerrar_modal)
        self.btn_guardar = ft.Button(
            content=ft.Text("Guardar Nómina"), 
            bgcolor="blue", 
            color="white", 
            on_click=self.guardar_click
        )

        # --- Modales ---
        self.modal_registro = ft.AlertDialog(
            modal=True,
            title=ft.Text("Registrar Nómina"),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([self.dd_chofer]),
                    ft.Row([self.txt_fecha_emision, self.btn_picker_emision]),
                    ft.Row([
                        ft.Row([self.txt_periodo_desde, self.btn_picker_desde], expand=True),
                        ft.Row([self.txt_periodo_hasta, self.btn_picker_hasta], expand=True)
                    ]),
                    ft.Row([self.txt_ingresos, self.txt_gasoil, self.txt_neto]),
                    ft.Container(height=10),
                    ft.Row([self.btn_cancelar, self.btn_guardar], alignment=ft.MainAxisAlignment.END, spacing=10)
                ], tight=True, spacing=15),
                width=650
            )
        )

        self.modal_confirmacion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text("¿Está seguro de que desea eliminar este registro de nómina?"),
            actions=[
                ft.Button("Cancelar", on_click=self.cerrar_modal_confirmacion),
                ft.Button("Eliminar", icon=ft.Icons.DELETE_FOREVER, bgcolor="red", color="white", on_click=self.confirmar_eliminacion_real)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.content = self.inicializar_vista()

    def mostrar_mensaje(self, page, texto, color="green"):
        """Muestra notificaciones flotantes (SnackBar) al estilo maestros_view."""
        if page:
            page.snack_bar = ft.SnackBar(content=ft.Text(texto, color="white"), bgcolor=color)
            page.snack_bar.open = True
            page.update()

    def inicializar_vista(self):
        btn_registrar = ft.Button(
            content=ft.Text("Nueva Nómina"), 
            icon=ft.Icons.ADD,
            bgcolor="#1976d2",
            color="white",
            on_click=self.abrir_modal_nuevo
        )
        self.cargar_datos_tabla()

        return ft.Column([
            ft.Text("Nómina y Finanzas: Comisiones y Reportes", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Row([self.txt_buscar, btn_registrar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Container(content=ft.ListView([self.tabla_datos], expand=True), expand=True)
        ], expand=True)

    def cargar_datos_tabla(self, page_context=None):
        try:
            self.historial_completo = obtener_nominas()
            self.tabla_datos.rows.clear()
            
            if self.historial_completo:
                for n in self.historial_completo:
                    id_n = getattr(n, 'id_nomina', 0)
                    
                    chofer_obj = getattr(n, 'chofer', None)
                    if chofer_obj is not None and hasattr(chofer_obj, 'nombre_completo'):
                        nombre_chofer = chofer_obj.nombre_completo
                    else:
                        nombre_chofer = "Desconocido"
                    
                    f_emision = getattr(n, 'fecha_emision', None)
                    fecha_emision = _formatear_fecha(f_emision, "%d/%m/%Y") if f_emision is not None else "S/F"
                    
                    p_desde = getattr(n, 'periodo_desde', None)
                    p_hasta = getattr(n, 'periodo_hasta', None)
                    
                    str_desde = _formatear_fecha(p_desde, "%d/%m")
                    str_hasta = _formatear_fecha(p_hasta, "%d/%m")
                    periodo = f"{str_desde} al {str_hasta}" if (p_desde is not None and p_hasta is not None) else "S/F"
                    
                    ingresos = getattr(n, 'total_ingresos_fletes', 0.0) or 0.0
                    gasoil = getattr(n, 'total_costo_gasoil', 0.0) or 0.0
                    neto = getattr(n, 'monto_neto_comision', 0.0) or 0.0

                    self.tabla_datos.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(fecha_emision)),
                                ft.DataCell(ft.Text(nombre_chofer, weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text(periodo)),
                                ft.DataCell(ft.Text(f"${ingresos:,.2f}", color="green")),
                                ft.DataCell(ft.Text(f"${gasoil:,.2f}", color="orange")),
                                ft.DataCell(ft.Text(f"${neto:,.2f}", weight=ft.FontWeight.BOLD, color="blue")),
                                ft.DataCell(
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT, 
                                            icon_color="blue", 
                                            tooltip="Editar nómina",
                                            on_click=lambda e, id=id_n: self.preparar_edicion(e, id)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE, 
                                            icon_color="red", 
                                            tooltip="Eliminar nómina",
                                            on_click=lambda e, id=id_n: self.preparar_eliminacion(e, id)
                                        )
                                    ])
                                )
                            ]
                        )
                    )
            if page_context: 
                page_context.update()
        except Exception as ex:
            print(f"[-] Error en cargar_datos_tabla: {ex}")
            if page_context: 
                self.mostrar_mensaje(page_context, "⚠️ Error al cargar el historial de nóminas.", "orange")

    def cargar_choferes(self):
        self.dd_chofer.options.clear()
        lista = obtener_choferes()
        if lista is not None:
            for c in lista:
                cid = getattr(c, 'id_chofer', '')
                cname = getattr(c, 'nombre_completo', 'Chofer')
                cced = getattr(c, 'cedula_identidad', '')
                texto_label = f"{cname} (C.I: {cced})" if cced else str(cname)
                self.dd_chofer.options.append(
                    ft.dropdown.Option(key=str(cid), text=texto_label)
                )

    def calcular_neto_automatico(self, e=None):
        """Calcula automáticamente el Neto = Ingresos - Gasoil al escribir en los campos."""
        try:
            ingresos = float(self.txt_ingresos.value) if self.txt_ingresos.value else 0.0
            gasoil = float(self.txt_gasoil.value) if self.txt_gasoil.value else 0.0
            neto = max(0.0, ingresos - gasoil)
            self.txt_neto.value = f"{neto:.2f}"
            if e and hasattr(e, 'page') and e.page:
                self.txt_neto.update()
        except ValueError:
            pass

    # --- Métodos para los Selectores de Fecha ---
    def abrir_calendario(self, date_picker, e):
        self.asegurar_overlays(e.page)
        date_picker.open = True
        e.page.update()

    def cambiar_fecha_emision(self, e):
        if hasattr(self.dp_emision, 'value') and self.dp_emision.value is not None:
            self.txt_fecha_emision.value = _formatear_fecha(self.dp_emision.value, "%Y-%m-%d")
            self.txt_fecha_emision.error = None
            self.update()

    def cambiar_fecha_desde(self, e):
        if hasattr(self.dp_desde, 'value') and self.dp_desde.value is not None:
            self.txt_periodo_desde.value = _formatear_fecha(self.dp_desde.value, "%Y-%m-%d")
            self.update()

    def cambiar_fecha_hasta(self, e):
        if hasattr(self.dp_hasta, 'value') and self.dp_hasta.value is not None:
            self.txt_periodo_hasta.value = _formatear_fecha(self.dp_hasta.value, "%Y-%m-%d")
            self.update()

    def asegurar_overlays(self, page):
        """Asegura que los DatePickers y Diálogos estén registrados en el overlay de la página"""
        if page is not None and hasattr(page, 'overlay'):
            for dp in [self.dp_emision, self.dp_desde, self.dp_hasta]:
                if dp not in page.overlay:
                    page.overlay.append(dp)
            if self.modal_registro not in page.overlay:
                page.overlay.append(self.modal_registro)
            if self.modal_confirmacion not in page.overlay:
                page.overlay.append(self.modal_confirmacion)

    def limpiar_errores_formulario(self):
        """Limpia los errores visuales de los controles del formulario."""
        self.dd_chofer.error_text = None
        self.txt_fecha_emision.error = None
        self.txt_ingresos.error = None
        self.txt_gasoil.error = None
        self.txt_neto.error = None

    def abrir_modal_nuevo(self, e):
        self.id_a_editar = None
        self.limpiar_errores_formulario()
        self.cargar_choferes()
        
        self.dd_chofer.value = None
        self.txt_fecha_emision.value = ""
        self.txt_periodo_desde.value = ""
        self.txt_periodo_hasta.value = ""
        self.txt_ingresos.value = "0.00"
        self.txt_gasoil.value = "0.00"
        self.txt_neto.value = "0.00"

        self.modal_registro.title = ft.Text("Registrar Nueva Nómina")
        self.btn_guardar.content = ft.Text("Guardar Nómina")
        
        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_registro
        self.modal_registro.open = True
        e.page.update()

    def preparar_edicion(self, e, id_nomina):
        self.id_a_editar = id_nomina
        self.limpiar_errores_formulario()
        registro = next((n for n in self.historial_completo if getattr(n, 'id_nomina', 0) == id_nomina), None)
        
        if registro is not None:
            self.cargar_choferes()
            id_ch = getattr(registro, 'id_chofer', None)
            self.dd_chofer.value = str(id_ch) if id_ch is not None else None
            
            f_em = getattr(registro, 'fecha_emision', None)
            if f_em is not None:
                self.txt_fecha_emision.value = _formatear_fecha(f_em, "%Y-%m-%d")
                if isinstance(f_em, (datetime, date)):
                    self.dp_emision.value = f_em
            else:
                self.txt_fecha_emision.value = ""

            p_d = getattr(registro, 'periodo_desde', None)
            if p_d is not None:
                self.txt_periodo_desde.value = _formatear_fecha(p_d, "%Y-%m-%d")
                if isinstance(p_d, (datetime, date)):
                    self.dp_desde.value = p_d
            else:
                self.txt_periodo_desde.value = ""

            p_h = getattr(registro, 'periodo_hasta', None)
            if p_h is not None:
                self.txt_periodo_hasta.value = _formatear_fecha(p_h, "%Y-%m-%d")
                if isinstance(p_h, (datetime, date)):
                    self.dp_hasta.value = p_h
            else:
                self.txt_periodo_hasta.value = ""

            self.txt_ingresos.value = str(getattr(registro, 'total_ingresos_fletes', "0.00"))
            self.txt_gasoil.value = str(getattr(registro, 'total_costo_gasoil', "0.00"))
            self.txt_neto.value = str(getattr(registro, 'monto_neto_comision', "0.00"))
            
            self.modal_registro.title = ft.Text("Editar Nómina")
            self.btn_guardar.content = ft.Text("Actualizar Nómina")
            
            self.asegurar_overlays(e.page)
            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            e.page.update()

    def guardar_click(self, e):
        self.limpiar_errores_formulario()
        hay_error = False

        chofer_val = self.dd_chofer.value
        fecha_emision_val = self.txt_fecha_emision.value or ""
        periodo_desde_val = self.txt_periodo_desde.value or ""
        periodo_hasta_val = self.txt_periodo_hasta.value or ""
        ingresos_str = self.txt_ingresos.value or "0"
        gasoil_str = self.txt_gasoil.value or "0"
        neto_str = self.txt_neto.value or "0"

        ingresos_val = 0.0
        gasoil_val = 0.0
        neto_val = 0.0

        if not chofer_val:
            self.dd_chofer.error_text = "Requerido"
            hay_error = True

        if not fecha_emision_val:
            self.txt_fecha_emision.error = "Requerido"
            hay_error = True

        try:
            ingresos_val = float(ingresos_str)
        except ValueError:
            self.txt_ingresos.error = "Monto inválido"
            hay_error = True

        try:
            gasoil_val = float(gasoil_str)
        except ValueError:
            self.txt_gasoil.error = "Monto inválido"
            hay_error = True

        try:
            neto_val = float(neto_str)
        except ValueError:
            self.txt_neto.error = "Monto inválido"
            hay_error = True

        if hay_error or chofer_val is None:
            self.mostrar_mensaje(e.page, "Por favor completa los campos requeridos.", "red")
            e.page.update()
            return

        try:
            params = {
                "id_chofer": int(chofer_val),
                "fecha_emision": fecha_emision_val,
                "periodo_desde": periodo_desde_val,
                "periodo_hasta": periodo_hasta_val,
                "ingresos": ingresos_val,
                "gasoil": gasoil_val,
                "comision": neto_val
            }

            if self.id_a_editar is None:
                exito, msg = registrar_nomina(**params)
            else:
                exito, msg = actualizar_nomina(self.id_a_editar, **params)

            if exito:
                self.modal_registro.open = False  
                self.id_a_editar = None
                self.cargar_datos_tabla(e.page)   
                self.mostrar_mensaje(e.page, msg or "Nómina guardada exitosamente.", "green")
            else:
                self.mostrar_mensaje(e.page, f"❌ {msg}", "red")
        except Exception as ex:
            print(f"[-] Error crítico en guardar_click: {ex}")
            self.mostrar_mensaje(e.page, f"⚠️ Error en BD: {str(ex)}", "red")

    def cerrar_modal(self, e=None):
        if e:
            self.modal_registro.open = False
            self.id_a_editar = None
            self.limpiar_errores_formulario()
            e.page.update()

    def preparar_eliminacion(self, e, id_nomina):
        self.id_a_eliminar = id_nomina
        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_confirmacion
        self.modal_confirmacion.open = True
        e.page.update()

    def confirmar_eliminacion_real(self, e):
        try:
            exito, msg = eliminar_nomina(self.id_a_eliminar)
            self.modal_confirmacion.open = False
            self.id_a_eliminar = None
            if exito:
                self.cargar_datos_tabla(e.page)
                self.mostrar_mensaje(e.page, msg or "Nómina eliminada con éxito.", "green")
            else:
                self.mostrar_mensaje(e.page, f"Error al eliminar: {msg}", "red")
                e.page.update()
        except Exception as ex:
            print(f"[-] Error en confirmar_eliminacion_real: {ex}")
            self.modal_confirmacion.open = False
            self.mostrar_mensaje(e.page, f"⚠️ Error inesperado: {str(ex)}", "red")

    def cerrar_modal_confirmacion(self, e=None):
        if e:
            self.modal_confirmacion.open = False
            self.id_a_eliminar = None
            e.page.update()

    def filtrar_datos(self, e):
        termino = (self.txt_buscar.value or "").lower().strip()
        self.cargar_datos_tabla(e.page if hasattr(e, 'page') else None)
        if not termino:
            return

        filas = []
        for row in self.tabla_datos.rows:
            cell_fecha = row.cells[0].content
            cell_chofer = row.cells[1].content
            
            val_fecha = str(getattr(cell_fecha, 'value', '')).lower()
            val_chofer = str(getattr(cell_chofer, 'value', '')).lower()
            
            if termino in val_fecha or termino in val_chofer:
                filas.append(row)
                
        self.tabla_datos.rows = filas
        if hasattr(e, 'page') and e.page:
            e.page.update()