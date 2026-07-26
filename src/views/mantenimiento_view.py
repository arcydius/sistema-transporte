import flet as ft
from controllers.maestro_controller import (
    obtener_camiones, 
    obtener_tipos_mantenimiento, 
    registrar_mantenimiento, 
    obtener_historial_mantenimiento,
    eliminar_mantenimiento,  
    actualizar_mantenimiento 
)

class MantenimientoView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.historial_completo = []
        self.id_a_eliminar = None 
        self.id_a_editar = None   
        
        # --- Componentes Principales de la Vista ---
        self.txt_buscar = ft.TextField(
            hint_text="Buscar por placa, tipo o técnico...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filtrar_mantenimientos,
            expand=True,
            border_radius=8
        )
        
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Tipo Servicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Técnico", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Costo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        # --- Componentes del Formulario ---
        self.dd_categoria = ft.Dropdown(label="Tipo de Servicio", expand=True, options=[])
        self.dd_unidad_especifica = ft.Dropdown(label="Seleccionar Camión (Placa)", expand=True, options=[])
        self.txt_tecnico = ft.TextField(
            label="Técnico Responsable", 
            expand=True,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$", replacement_string="")
        )
        
        # Campo Numérico Decimal Restringido (Solo números y un punto decimal)
        self.txt_costo = ft.TextField(
            label="Costo del Servicio ($)", 
            value="0.00", 
            hint_text="Ej: 150.50",
            expand=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string="")
        )
        
        self.txt_descripcion = ft.TextField(label="Descripción del Trabajo", multiline=True, min_lines=2, expand=True)

        # --- Botones del Modal ---
        self.btn_cancelar = ft.TextButton(content=ft.Text("Cancelar"), on_click=self.cerrar_modal)
        self.btn_guardar = ft.Button(
            content=ft.Text("Guardar Servicio"), 
            bgcolor="blue", 
            color="white", 
            on_click=self.guardar_servicio_click
        )

        # --- Modales ---
        self.modal_registro = ft.AlertDialog(
            modal=True,
            title=ft.Text("Registrar Nuevo Servicio de Taller"),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([self.dd_categoria]),
                    ft.Row([self.dd_unidad_especifica, self.txt_tecnico]),
                    ft.Row([self.txt_costo]),
                    ft.Row([self.txt_descripcion]),
                    ft.Container(height=10),
                    ft.Row([self.btn_cancelar, self.btn_guardar], alignment=ft.MainAxisAlignment.END, spacing=10)
                ], tight=True, spacing=15),
                width=500
            )
        )

        # Modal de Confirmación para Eliminar
        self.modal_confirmacion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text("¿Está seguro de que desea eliminar este registro de mantenimiento?"),
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
            content=ft.Text("Registrar Servicio"), 
            icon=ft.Icons.ADD,
            bgcolor="#1976d2",
            color="white",
            on_click=self.abrir_modal_nuevo
        )

        self.cargar_datos_tabla()

        return ft.Column([
            ft.Text("Mantenimiento y Taller", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Row([self.txt_buscar, btn_registrar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Container(
                content=ft.ListView([self.tabla_datos], expand=True),
                expand=True
            )
        ], expand=True)

    def cargar_datos_tabla(self, page_context=None):
        try:
            self.historial_completo = obtener_historial_mantenimiento()
            self.tabla_datos.rows.clear()
            
            lista_camiones = obtener_camiones()
            camiones_dict = {c.id_camion: f"{c.marca} ({c.placa})" for c in lista_camiones} if lista_camiones else {}
            
            for m in self.historial_completo:
                id_m = getattr(m, 'id_mantenimiento', 0)
                
                if hasattr(m, 'camion') and m.camion:
                    unidad_texto = f"{m.camion.marca or 'Camión'} ({m.camion.placa})"
                elif hasattr(m, 'id_camion') and m.id_camion in camiones_dict:
                    unidad_texto = camiones_dict[m.id_camion]
                else:
                    unidad_texto = "Unidad General"

                f_serv = getattr(m, 'fecha_servicio', None)
                fecha_str = f_serv.strftime("%d/%m/%Y") if f_serv is not None and hasattr(f_serv, 'strftime') else str(f_serv or "S/F")
                
                tipo_obj = getattr(m, 'tipo', None)
                nombre_servicio = str(getattr(tipo_obj, 'nombre_tipo', 'General')) if tipo_obj is not None else "General"
                costo_invertido = float(getattr(m, 'monto_invertido', 0.0) or 0.0)
                tec_resp = str(getattr(m, 'tecnico_responsable', 'N/A') or 'N/A')

                self.tabla_datos.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(fecha_str)),
                            ft.DataCell(ft.Text(unidad_texto, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(nombre_servicio)),
                            ft.DataCell(ft.Text(tec_resp)),
                            ft.DataCell(ft.Text(f"${costo_invertido:,.2f}", color="red", weight=ft.FontWeight.BOLD)),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT, 
                                        icon_color="blue", 
                                        tooltip="Editar registro",
                                        on_click=lambda e, id=id_m: self.preparar_edicion(e, id) 
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, 
                                        icon_color="red", 
                                        tooltip="Eliminar registro",
                                        on_click=lambda e, id=id_m: self.preparar_eliminacion(e, id)
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
                self.mostrar_mensaje(page_context, "⚠️ Error al cargar el historial de mantenimiento.", "orange")

    # --- Lógica de Eliminación ---
    def preparar_eliminacion(self, e, id_mantenimiento):
        self.id_a_eliminar = id_mantenimiento
        e.page.dialog = self.modal_confirmacion
        self.modal_confirmacion.open = True
        
        if hasattr(e.page, "overlay") and self.modal_confirmacion not in e.page.overlay:
            e.page.overlay.append(self.modal_confirmacion)
            
        e.page.update()

    def confirmar_eliminacion_real(self, e):
        try:
            exito, msg = eliminar_mantenimiento(self.id_a_eliminar)
            self.modal_confirmacion.open = False
            self.id_a_eliminar = None
            if exito:
                self.cargar_datos_tabla(e.page)
                self.mostrar_mensaje(e.page, msg or "Registro eliminado con éxito.", "green")
            else:
                self.mostrar_mensaje(e.page, f"Error al eliminar: {msg}", "red")
                e.page.update()
        except Exception as ex:
            print(f"[-] Error en confirmar_eliminacion_real: {ex}")
            self.modal_confirmacion.open = False
            self.mostrar_mensaje(e.page, f"⚠️ Error inesperado: {str(ex)}", "red")

    def cerrar_modal_confirmacion(self, e):
        self.modal_confirmacion.open = False
        self.id_a_eliminar = None
        e.page.update()

    # --- Lógica de Edición ---
    def preparar_edicion(self, e, id_mantenimiento):
        self.id_a_editar = id_mantenimiento
        self.limpiar_errores_formulario()
        
        registro_actual = next((m for m in self.historial_completo if getattr(m, 'id_mantenimiento', 0) == id_mantenimiento), None)
        
        if registro_actual:
            self.cargar_opciones_formularios()
            
            id_t = getattr(registro_actual, 'id_tipo', None)
            id_c = getattr(registro_actual, 'id_camion', None)
            tec = getattr(registro_actual, 'tecnico_responsable', None)
            monto = getattr(registro_actual, 'monto_invertido', "0.00")
            desc = getattr(registro_actual, 'descripcion', None)

            self.dd_categoria.value = str(id_t) if id_t is not None else None
            self.dd_unidad_especifica.value = str(id_c) if id_c is not None else None
            self.txt_tecnico.value = str(tec or "")
            self.txt_costo.value = str(monto)
            self.txt_descripcion.value = str(desc or "")
            
            self.modal_registro.title = ft.Text("Editar Servicio de Taller")
            self.btn_guardar.content = ft.Text("Actualizar Servicio")
            
            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            if hasattr(e.page, "overlay") and self.modal_registro not in e.page.overlay:
                e.page.overlay.append(self.modal_registro)
            e.page.update()

    def cargar_opciones_formularios(self):
        """Extrae la lógica de cargar opciones para usarla al crear o al editar."""
        tipos = obtener_tipos_mantenimiento()
        if not tipos:
            self.dd_categoria.options = [
                ft.dropdown.Option(key="1", text="Mantenimiento Preventivo"),
                ft.dropdown.Option(key="2", text="Mantenimiento Correctivo"),
                ft.dropdown.Option(key="3", text="Mantenimiento General")
            ]
        else:
            self.dd_categoria.options = [
                ft.dropdown.Option(key=str(getattr(t, 'id_tipo', '')), text=str(getattr(t, 'nombre_tipo', ''))) 
                for t in tipos
            ]

        self.dd_unidad_especifica.options.clear()
        lista_camiones = obtener_camiones()
        if not lista_camiones:
            self.dd_unidad_especifica.options.append(
                ft.dropdown.Option(key="1", text="Mercedez - ABCDE67")
            )
        else:
            for c in lista_camiones:
                self.dd_unidad_especifica.options.append(
                    ft.dropdown.Option(key=str(c.id_camion), text=f"{c.marca} - {c.placa}")
                )

    def limpiar_errores_formulario(self):
        """Limpia los indicadores visuales de error de los campos del formulario."""
        self.dd_categoria.error_text = None
        self.dd_unidad_especifica.error_text = None
        self.txt_costo.error = None

    def abrir_modal_nuevo(self, e):
        """Modificado para resetear el formulario a estado 'Nuevo'"""
        try:
            self.id_a_editar = None
            self.limpiar_errores_formulario()
            self.cargar_opciones_formularios()
            
            if self.dd_unidad_especifica.options:
                self.dd_unidad_especifica.value = self.dd_unidad_especifica.options[0].key
            self.dd_categoria.value = None
            self.txt_tecnico.value = ""
            self.txt_costo.value = "0.00"
            self.txt_descripcion.value = ""

            self.modal_registro.title = ft.Text("Registrar Nuevo Servicio de Taller")
            self.btn_guardar.content = ft.Text("Guardar Servicio")

            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            
            if hasattr(e.page, "overlay") and self.modal_registro not in e.page.overlay:
                e.page.overlay.append(self.modal_registro)
                
            e.page.update()
        except Exception as ex:
            print(f"[-] Error en abrir_modal_nuevo: {ex}")
            self.mostrar_mensaje(e.page, f"⚠️ Error al abrir el formulario: {str(ex)}", "red")

    def cerrar_modal(self, e=None):
        if e:
            self.modal_registro.open = False
            self.id_a_editar = None
            self.limpiar_errores_formulario()
            e.page.update()

    def guardar_servicio_click(self, e):
        self.limpiar_errores_formulario()
        hay_error = False

        cat_val = self.dd_categoria.value
        unidad_val = self.dd_unidad_especifica.value
        costo_str = self.txt_costo.value or "0"
        monto_val = 0.0

        if not cat_val:
            self.dd_categoria.error_text = "Requerido"
            hay_error = True

        if not unidad_val:
            self.dd_unidad_especifica.error_text = "Requerido"
            hay_error = True

        if not costo_str or costo_str.strip() == "":
            self.txt_costo.error = "Requerido"
            hay_error = True

        try:
            monto_val = float(costo_str)
        except ValueError:
            self.txt_costo.error = "Monto inválido"
            hay_error = True

        if hay_error or cat_val is None or unidad_val is None:
            self.mostrar_mensaje(e.page, "Por favor completa correctamente los campos requeridos.", "red")
            e.page.update()
            return

        try:
            id_camion = int(unidad_val)
            id_tipo = int(cat_val)
            
            if self.id_a_editar is None:
                exito, msg = registrar_mantenimiento(
                    id_tipo=id_tipo,
                    descripcion=self.txt_descripcion.value,
                    monto=monto_val,
                    tecnico=self.txt_tecnico.value,
                    id_camion=id_camion,
                    id_remolque=None
                )
            else:
                exito, msg = actualizar_mantenimiento(
                    id_mantenimiento=self.id_a_editar,
                    id_tipo=id_tipo,
                    descripcion=self.txt_descripcion.value,
                    monto=monto_val,
                    tecnico=self.txt_tecnico.value,
                    id_camion=id_camion,
                    id_remolque=None
                )

            if exito:
                self.modal_registro.open = False  
                self.id_a_editar = None
                self.txt_tecnico.value = ""
                self.txt_costo.value = "0.00"
                self.txt_descripcion.value = ""
                self.dd_unidad_especifica.value = None
                self.dd_categoria.value = None
                self.cargar_datos_tabla(e.page)   
                self.mostrar_mensaje(e.page, msg or "Operación realizada con éxito.", "green")
            else:
                self.mostrar_mensaje(e.page, f"❌ {msg}", "red")
        except Exception as ex:
            print(f"[-] Error crítico en guardar_servicio_click: {ex}")
            self.mostrar_mensaje(e.page, f"⚠️ Error en BD: {str(ex)}", "red")

    def filtrar_mantenimientos(self, e):
        termino = (self.txt_buscar.value or "").lower().strip()
        self.cargar_datos_tabla(e.page if hasattr(e, 'page') else None)
        
        if not termino:
            if hasattr(e, 'page') and e.page:
                e.page.update()
            return

        filas_filtradas = []
        for row in self.tabla_datos.rows:
            c_unidad = row.cells[1].content
            c_tipo = row.cells[2].content
            c_tecnico = row.cells[3].content
            
            unidad = str(getattr(c_unidad, 'value', '')).lower()
            tipo = str(getattr(c_tipo, 'value', '')).lower()
            tecnico = str(getattr(c_tecnico, 'value', '')).lower()
            
            if termino in unidad or termino in tipo or termino in tecnico:
                filas_filtradas.append(row)
                
        self.tabla_datos.rows = filas_filtradas
        if hasattr(e, 'page') and e.page:
            e.page.update()