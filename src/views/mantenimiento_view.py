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
        
        # --- Banner de Diagnóstico Visual ---
        self.banner_error = ft.Text(value="", color="red", size=14, weight=ft.FontWeight.BOLD)
        
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
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo Servicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Técnico", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Costo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        # --- Componentes del Formulario ---
        self.dd_categoria = ft.Dropdown(label="Tipo de Servicio", expand=True, options=[])
        self.dd_unidad_especifica = ft.Dropdown(label="Seleccionar Camión (Placa)", expand=True, options=[])
        self.txt_tecnico = ft.TextField(label="Técnico Responsable", expand=True)
        
        # Campo Numérico con Restricción (Solo números y punto decimal)
        self.txt_costo = ft.TextField(
            label="Costo del Servicio ($)", 
            value="0.00", 
            expand=True,
            input_filter=ft.InputFilter(regex_string=r"[0-9.]")
        )
        
        self.txt_descripcion = ft.TextField(label="Descripción del Trabajo", multiline=True, min_lines=2, expand=True)

        # --- Botones del Modal ---
        self.btn_cancelar = ft.TextButton(content=ft.Text("Cancelar"), on_click=self.cerrar_modal)
        self.btn_guardar = ft.ElevatedButton(
            content=ft.Text("Guardar Servicio"), 
            bgcolor="blue", 
            color="white", 
            on_click=self.guardar_servicio_click
        )

        # --- Modales ---
        self.modal_registro = ft.AlertDialog(
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
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este registro?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_modal_confirmacion),
                ft.ElevatedButton("Eliminar", bgcolor="red", color="white", on_click=self.confirmar_eliminacion_real)
            ]
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        btn_registrar = ft.ElevatedButton(
            content=ft.Text("Registrar Servicio"), 
            on_click=self.abrir_modal_nuevo
        )

        self.cargar_datos_tabla()

        return ft.Column([
            ft.Text("Mantenimiento y Taller", size=28, weight=ft.FontWeight.BOLD),
            self.banner_error,  
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

                fecha_str = m.fecha_servicio.strftime("%d/%m/%Y") if hasattr(m, 'fecha_servicio') and m.fecha_servicio else "S/F"
                nombre_servicio = m.tipo.nombre_tipo if hasattr(m, 'tipo') and m.tipo else "General"
                costo_invertido = m.monto_invertido if hasattr(m, 'monto_invertido') else 0.0

                self.tabla_datos.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(fecha_str)),
                            ft.DataCell(ft.Text(unidad_texto, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(nombre_servicio)),
                            ft.DataCell(ft.Text(m.tecnico_responsable or "N/A")),
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
                                        icon=ft.Icons.DELETE, 
                                        icon_color="red", 
                                        tooltip="Eliminar registro",
                                        on_click=lambda e, id=id_m: self.preparar_eliminacion(e, id)
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
            print(f"[-] Error en cargar_datos_tabla: {ex}")
            self.banner_error.value = f"⚠️ Nota: Historial vacío o error de lectura BD."
            if page_context:
                page_context.update()

    # --- Lógica de Eliminación (CORREGIDA) ---
    def preparar_eliminacion(self, e, id_mantenimiento):
        self.id_a_eliminar = id_mantenimiento
        
        e.page.dialog = self.modal_confirmacion
        self.modal_confirmacion.open = True
        
        # Agregar modal al overlay si no está para asegurar su renderizado
        if hasattr(e.page, "overlay") and self.modal_confirmacion not in e.page.overlay:
            e.page.overlay.append(self.modal_confirmacion)
            
        e.page.update()

    def confirmar_eliminacion_real(self, e):
        print(f"DEBUG: Intentando eliminar registro ID: {self.id_a_eliminar}") 
        
        try:
            exito, msg = eliminar_mantenimiento(self.id_a_eliminar)
            if exito:
                self.modal_confirmacion.open = False
                self.id_a_eliminar = None
                self.banner_error.value = "" 
                self.cargar_datos_tabla(e.page)
            else:
                self.banner_error.value = f"❌ Error al eliminar: {msg}"
                self.modal_confirmacion.open = False
                e.page.update()
        except Exception as ex:
            print(f"[-] Error en confirmar_eliminacion_real: {ex}")
            self.banner_error.value = f"⚠️ Error inesperado: {str(ex)}"
            self.modal_confirmacion.open = False
            e.page.update()

    def cerrar_modal_confirmacion(self, e):
        self.modal_confirmacion.open = False
        self.id_a_eliminar = None
        e.page.update()

    # --- Lógica de Edición ---
    def preparar_edicion(self, e, id_mantenimiento):
        self.id_a_editar = id_mantenimiento
        
        # 1. Buscar el registro exacto en el historial cargado
        registro_actual = next((m for m in self.historial_completo if getattr(m, 'id_mantenimiento', 0) == id_mantenimiento), None)
        
        if registro_actual:
            # 2. Asegurarse de que los dropdowns tengan las opciones cargadas
            self.cargar_opciones_formularios()
            
            # 3. Asignar los valores a los campos
            self.dd_categoria.value = str(registro_actual.id_tipo) if hasattr(registro_actual, 'id_tipo') else None
            self.dd_unidad_especifica.value = str(registro_actual.id_camion) if hasattr(registro_actual, 'id_camion') else None
            self.txt_tecnico.value = registro_actual.tecnico_responsable or ""
            self.txt_costo.value = str(registro_actual.monto_invertido) if hasattr(registro_actual, 'monto_invertido') else "0.00"
            
            # Si el modelo tiene un campo 'descripcion', lo cargamos:
            self.txt_descripcion.value = registro_actual.descripcion if hasattr(registro_actual, 'descripcion') else ""
            
            # 4. Cambiar textos del modal a modo "Edición"
            self.modal_registro.title = ft.Text("Editar Servicio de Taller")
            self.btn_guardar.content = ft.Text("Actualizar Servicio")
            
            # 5. Mostrar Modal
            self.banner_error.value = ""
            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            if hasattr(e.page, "overlay") and self.modal_registro not in e.page.overlay:
                e.page.overlay.append(self.modal_registro)
            e.page.update()

    # --- Funciones Auxiliares Originales Modificadas para soportar ambos modos ---
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
                ft.dropdown.Option(key=str(t.id_tipo), text=t.nombre_tipo) 
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

    def abrir_modal_nuevo(self, e):
        """Modificado para resetear el formulario a estado 'Nuevo'"""
        try:
            self.id_a_editar = None # Limpiar estado de edición
            self.banner_error.value = ""
            
            # Cargar los selectores
            self.cargar_opciones_formularios()
            
            # Resetear valores del formulario
            if self.dd_unidad_especifica.options:
                self.dd_unidad_especifica.value = self.dd_unidad_especifica.options[0].key
            self.dd_categoria.value = None
            self.txt_tecnico.value = ""
            self.txt_costo.value = "0.00"
            self.txt_descripcion.value = ""

            # Cambiar Textos a modo "Registro"
            self.modal_registro.title = ft.Text("Registrar Nuevo Servicio de Taller")
            self.btn_guardar.content = ft.Text("Guardar Servicio")

            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            
            if hasattr(e.page, "overlay") and self.modal_registro not in e.page.overlay:
                e.page.overlay.append(self.modal_registro)
                
            e.page.update()
        except Exception as ex:
            print(f"[-] Error en abrir_modal_nuevo: {ex}")
            self.banner_error.value = f"⚠️ Error al abrir el formulario: {str(ex)}"
            e.page.update()

    def cerrar_modal(self, e=None):
        if e:
            self.modal_registro.open = False
            self.id_a_editar = None
            e.page.update()

    def guardar_servicio_click(self, e):
        if not self.dd_categoria.value or not self.dd_unidad_especifica.value:
            self.banner_error.value = "⚠️ Por favor selecciona el tipo de servicio y el camión."
            e.page.update()
            return

        try:
            id_camion = int(self.dd_unidad_especifica.value)
            
            # --- EVALUAR SI ESTAMOS CREANDO O EDITANDO ---
            if self.id_a_editar is None:
                # CREAR NUEVO (Tu lógica original)
                exito, msg = registrar_mantenimiento(
                    id_tipo=int(self.dd_categoria.value),
                    descripcion=self.txt_descripcion.value,
                    monto=float(self.txt_costo.value or 0),
                    tecnico=self.txt_tecnico.value,
                    id_camion=id_camion,
                    id_remolque=None
                )
            else:
                # ACTUALIZAR EXISTENTE
                exito, msg = actualizar_mantenimiento(
                    id_mantenimiento=self.id_a_editar,
                    id_tipo=int(self.dd_categoria.value),
                    descripcion=self.txt_descripcion.value,
                    monto=float(self.txt_costo.value or 0),
                    tecnico=self.txt_tecnico.value,
                    id_camion=id_camion,
                    id_remolque=None
                )

            if exito:
                self.modal_registro.open = False  
                self.id_a_editar = None # Limpiar variable tras éxito
                self.txt_tecnico.value = ""
                self.txt_costo.value = "0.00"
                self.txt_descripcion.value = ""
                self.dd_unidad_especifica.value = None
                self.dd_categoria.value = None
                self.banner_error.value = ""
                self.cargar_datos_tabla(e.page)   
            else:
                self.banner_error.value = f"❌ {msg}"
            e.page.update()
        except Exception as ex:
            print(f"[-] Error crítico en guardar_servicio_click: {ex}")
            self.banner_error.value = f"⚠️ Error en BD: {str(ex)}"
            e.page.update()

    def filtrar_mantenimientos(self, e):
        termino = self.txt_buscar.value.lower()
        self.cargar_datos_tabla(e.page)
        
        if not termino:
            e.page.update()
            return

        filas_filtradas = []
        for row in self.tabla_datos.rows:
            unidad = row.cells[1].content.value.lower()
            tipo = row.cells[2].content.value.lower()
            tecnico = row.cells[3].content.value.lower()
            
            if termino in unidad or termino in tipo or termino in tecnico:
                filas_filtradas.append(row)
                
        self.tabla_datos.rows = filas_filtradas
        e.page.update()