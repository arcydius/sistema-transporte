import flet as ft
from controllers.maestro_controller import (
    obtener_choferes, 
    obtener_nominas, 
    registrar_nomina, 
    actualizar_nomina, 
    eliminar_nomina
)

class NominaView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.historial_completo = []
        self.id_a_eliminar = None 
        self.id_a_editar = None   
        
        # --- Banner de Diagnóstico ---
        self.banner_error = ft.Text(value="", color="red", size=14, weight=ft.FontWeight.BOLD)
        
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
                ft.DataColumn(ft.Text("Emisión", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Chofer", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Período", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ingresos ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Gasoil ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Neto ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
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

        # Campos Numéricos con Restricción (Solo números y punto decimal)
        self.txt_ingresos = ft.TextField(
            label="Total Ingresos Fletes", 
            value="0.00", 
            expand=True,
            input_filter=ft.InputFilter(regex_string=r"[0-9.]")
        )
        self.txt_gasoil = ft.TextField(
            label="Total Costo Gasoil", 
            value="0.00", 
            expand=True,
            input_filter=ft.InputFilter(regex_string=r"[0-9.]")
        )
        self.txt_neto = ft.TextField(
            label="Monto Neto Comisión", 
            value="0.00", 
            expand=True,
            input_filter=ft.InputFilter(regex_string=r"[0-9.]")
        )

        self.btn_cancelar = ft.TextButton(content=ft.Text("Cancelar"), on_click=self.cerrar_modal)
        self.btn_guardar = ft.ElevatedButton(
            content=ft.Text("Guardar Nómina"), 
            bgcolor="blue", 
            color="white", 
            on_click=self.guardar_click
        )

        # --- Modales ---
        self.modal_registro = ft.AlertDialog(
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
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar esta nómina?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_modal_confirmacion),
                ft.ElevatedButton("Eliminar", bgcolor="red", color="white", on_click=self.confirmar_eliminacion_real)
            ]
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        btn_registrar = ft.ElevatedButton(
            content=ft.Text("Nueva Nómina"), 
            on_click=self.abrir_modal_nuevo
        )
        self.cargar_datos_tabla()

        return ft.Column([
            ft.Text("Nómina y Finanzas: Comisiones y Reportes", size=28, weight=ft.FontWeight.BOLD),
            self.banner_error,  
            ft.Container(height=10),
            ft.Row([self.txt_buscar, btn_registrar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Container(content=ft.ListView([self.tabla_datos], expand=True), expand=True)
        ], expand=True)

    def cargar_datos_tabla(self, page_context=None):
        try:
            self.historial_completo = obtener_nominas()
            self.tabla_datos.rows.clear()
            
            for n in self.historial_completo:
                id_n = n.id_nomina
                nombre_chofer = n.chofer.nombre_completo if n.chofer else "Desconocido"
                fecha_emision = n.fecha_emision.strftime("%Y-%m-%d") if n.fecha_emision else "S/F"
                periodo = f"{n.periodo_desde.strftime('%d/%m')} al {n.periodo_hasta.strftime('%d/%m')}" if n.periodo_desde and n.periodo_hasta else "S/F"
                
                self.tabla_datos.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(fecha_emision)),
                            ft.DataCell(ft.Text(nombre_chofer, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(periodo)),
                            ft.DataCell(ft.Text(f"${n.total_ingresos_fletes:,.2f}", color="green")),
                            ft.DataCell(ft.Text(f"${n.total_costo_gasoil:,.2f}", color="orange")),
                            ft.DataCell(ft.Text(f"${n.monto_neto_comision:,.2f}", weight=ft.FontWeight.BOLD, color="blue")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT, 
                                        icon_color="blue", 
                                        tooltip="Editar nómina",
                                        on_click=lambda e, id=id_n: self.preparar_edicion(e, id)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE, 
                                        icon_color="red", 
                                        tooltip="Eliminar nómina",
                                        on_click=lambda e, id=id_n: self.preparar_eliminacion(e, id)
                                    )
                                ])
                            )
                        ]
                    )
                )
            self.banner_error.value = "" 
            if page_context: 
                page_context.update()
        except Exception as ex:
            self.banner_error.value = f"⚠️ Error de lectura BD: {ex}"
            if page_context: 
                page_context.update()

    def cargar_choferes(self):
        self.dd_chofer.options.clear()
        lista = obtener_choferes()
        if lista:
            for c in lista:
                self.dd_chofer.options.append(ft.dropdown.Option(key=str(c.id_chofer), text=c.nombre_completo))

    # --- Métodos para los Selectores de Fecha ---
    def abrir_calendario(self, date_picker, e):
        self.asegurar_overlays(e.page)
        date_picker.open = True
        e.page.update()

    def cambiar_fecha_emision(self, e):
        if self.dp_emision.value:
            self.txt_fecha_emision.value = self.dp_emision.value.strftime("%Y-%m-%d")
            self.update()

    def cambiar_fecha_desde(self, e):
        if self.dp_desde.value:
            self.txt_periodo_desde.value = self.dp_desde.value.strftime("%Y-%m-%d")
            self.update()

    def cambiar_fecha_hasta(self, e):
        if self.dp_hasta.value:
            self.txt_periodo_hasta.value = self.dp_hasta.value.strftime("%Y-%m-%d")
            self.update()

    def asegurar_overlays(self, page):
        """Asegura que los DatePickers y Diálogos estén registrados en el overlay de la página"""
        for dp in [self.dp_emision, self.dp_desde, self.dp_hasta]:
            if dp not in page.overlay:
                page.overlay.append(dp)
        if self.modal_registro not in page.overlay:
            page.overlay.append(self.modal_registro)
        if self.modal_confirmacion not in page.overlay:
            page.overlay.append(self.modal_confirmacion)

    def abrir_modal_nuevo(self, e):
        self.id_a_editar = None
        self.banner_error.value = ""
        self.cargar_choferes()
        
        self.dd_chofer.value = None
        self.txt_fecha_emision.value = ""
        self.txt_periodo_desde.value = ""
        self.txt_periodo_hasta.value = ""
        self.txt_ingresos.value = "0.00"
        self.txt_gasoil.value = "0.00"
        self.txt_neto.value = "0.00"

        self.modal_registro.title = ft.Text("Registrar Nómina")
        self.btn_guardar.content = ft.Text("Guardar Nómina")
        
        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_registro
        self.modal_registro.open = True
        e.page.update()

    def preparar_edicion(self, e, id_nomina):
        self.id_a_editar = id_nomina
        registro = next((n for n in self.historial_completo if n.id_nomina == id_nomina), None)
        
        if registro:
            self.cargar_choferes()
            self.dd_chofer.value = str(registro.id_chofer) if registro.id_chofer else None
            
            if registro.fecha_emision:
                self.txt_fecha_emision.value = registro.fecha_emision.strftime("%Y-%m-%d")
                self.dp_emision.value = registro.fecha_emision
            else:
                self.txt_fecha_emision.value = ""

            if registro.periodo_desde:
                self.txt_periodo_desde.value = registro.periodo_desde.strftime("%Y-%m-%d")
                self.dp_desde.value = registro.periodo_desde
            else:
                self.txt_periodo_desde.value = ""

            if registro.periodo_hasta:
                self.txt_periodo_hasta.value = registro.periodo_hasta.strftime("%Y-%m-%d")
                self.dp_hasta.value = registro.periodo_hasta
            else:
                self.txt_periodo_hasta.value = ""

            self.txt_ingresos.value = str(registro.total_ingresos_fletes)
            self.txt_gasoil.value = str(registro.total_costo_gasoil)
            self.txt_neto.value = str(registro.monto_neto_comision)
            
            self.modal_registro.title = ft.Text("Editar Nómina")
            self.btn_guardar.content = ft.Text("Actualizar Nómina")
            
            self.asegurar_overlays(e.page)
            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            e.page.update()

    def guardar_click(self, e):
        if not self.dd_chofer.value:
            self.banner_error.value = "⚠️ Por favor selecciona un chofer."
            e.page.update()
            return

        try:
            params = {
                "id_chofer": int(self.dd_chofer.value),
                "fecha_emision": self.txt_fecha_emision.value,
                "periodo_desde": self.txt_periodo_desde.value,
                "periodo_hasta": self.txt_periodo_hasta.value,
                "ingresos": float(self.txt_ingresos.value or 0),
                "gasoil": float(self.txt_gasoil.value or 0),
                "comision": float(self.txt_neto.value or 0)
            }

            if self.id_a_editar is None:
                exito, msg = registrar_nomina(**params)
            else:
                exito, msg = actualizar_nomina(self.id_a_editar, **params)

            if exito:
                self.modal_registro.open = False  
                self.id_a_editar = None
                self.cargar_datos_tabla(e.page)   
            else:
                self.banner_error.value = f"❌ {msg}"
            e.page.update()
        except ValueError:
             self.banner_error.value = "⚠️ Verifica que los valores numéricos sean correctos."
             e.page.update()
        except Exception as ex:
            self.banner_error.value = f"⚠️ Error: {str(ex)}"
            e.page.update()

    def cerrar_modal(self, e):
        self.modal_registro.open = False
        self.id_a_editar = None
        e.page.update()

    def preparar_eliminacion(self, e, id_nomina):
        self.id_a_eliminar = id_nomina
        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_confirmacion
        self.modal_confirmacion.open = True
        e.page.update()

    def confirmar_eliminacion_real(self, e):
        exito, msg = eliminar_nomina(self.id_a_eliminar)
        if exito:
            self.modal_confirmacion.open = False
            self.id_a_eliminar = None
            self.cargar_datos_tabla(e.page)
        else:
            self.banner_error.value = f"❌ Error al eliminar: {msg}"
            self.modal_confirmacion.open = False
            e.page.update()

    def cerrar_modal_confirmacion(self, e):
        self.modal_confirmacion.open = False
        self.id_a_eliminar = None
        e.page.update()

    def filtrar_datos(self, e):
        termino = self.txt_buscar.value.lower()
        self.cargar_datos_tabla(e.page)
        if not termino: return

        filas = []
        for row in self.tabla_datos.rows:
            fecha = row.cells[0].content.value.lower()
            chofer = row.cells[1].content.value.lower()
            
            if termino in fecha or termino in chofer:
                filas.append(row)
                
        self.tabla_datos.rows = filas
        e.page.update()