import flet as ft
from controllers.maestro_controller import (
    obtener_camiones, 
    obtener_tipos_mantenimiento, 
    registrar_mantenimiento, 
    obtener_historial_mantenimiento
)

class MantenimientoView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.historial_completo = []
        
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
        
        self.dd_unidad_especifica = ft.Dropdown(
            label="Seleccionar Camión (Placa)", 
            expand=True, 
            options=[]
        )

        self.txt_tecnico = ft.TextField(label="Técnico Responsable", expand=True)
        self.txt_costo = ft.TextField(label="Costo del Servicio ($)", value="0.00", expand=True)
        self.txt_descripcion = ft.TextField(label="Descripción del Trabajo", multiline=True, min_lines=2, expand=True)

        # --- Botones del Modal ---
        self.btn_cancelar = ft.TextButton(
            content=ft.Text("Cancelar"), 
            on_click=self.cerrar_modal
        )

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Text("Guardar Servicio"), 
            bgcolor="blue", 
            color="white", 
            on_click=self.guardar_servicio_click
        )

        # --- Estructura del Modal ---
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

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        btn_registrar = ft.ElevatedButton(
            content=ft.Text("Registrar Servicio"), 
            on_click=self.abrir_modal
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
            
            # Traemos la lista de camiones para cruzar nombres en caso de que la relación falle
            lista_camiones = obtener_camiones()
            camiones_dict = {c.id_camion: f"{c.marca} ({c.placa})" for c in lista_camiones} if lista_camiones else {}
            
            for m in self.historial_completo:
                # SOLUCIÓN AL TRANSPORTE DE DATOS: Verificación exhaustiva de la procedencia del camión
                if hasattr(m, 'camion') and m.camion:
                    unidad_texto = f"{m.camion.marca or 'Camión'} ({m.camion.placa})"
                elif hasattr(m, 'id_camion') and m.id_camion in camiones_dict:
                    unidad_texto = camiones_dict[m.id_camion]
                elif hasattr(m, 'id_camion') and m.id_camion:
                    unidad_texto = f"Camión #{m.id_camion}"
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
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar registro")
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

    def abrir_modal(self, e):
        try:
            self.banner_error.value = ""
            
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

            self.dd_unidad_especifica.value = None
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
            
            if self.dd_unidad_especifica.options:
                self.dd_unidad_especifica.value = self.dd_unidad_especifica.options[0].key

            e.page.dialog = self.modal_registro
            self.modal_registro.open = True
            
            if hasattr(e.page, "overlay") and self.modal_registro not in e.page.overlay:
                e.page.overlay.append(self.modal_registro)
                
            e.page.update()
        except Exception as ex:
            print(f"[-] Error en abrir_modal: {ex}")
            self.banner_error.value = f"⚠️ Error al abrir el formulario: {str(ex)}"
            e.page.update()

    def cerrar_modal(self, e=None):
        if e:
            self.modal_registro.open = False
            e.page.update()

    def guardar_servicio_click(self, e):
        if not self.dd_categoria.value or not self.dd_unidad_especifica.value:
            self.banner_error.value = "⚠️ Por favor selecciona el tipo de servicio y el camión."
            e.page.update()
            return

        try:
            id_camion = int(self.dd_unidad_especifica.value)

            exito, msg = registrar_mantenimiento(
                id_tipo=int(self.dd_categoria.value),
                descripcion=self.txt_descripcion.value,
                monto=float(self.txt_costo.value or 0),
                tecnico=self.txt_tecnico.value,
                id_camion=id_camion,
                id_remolque=None
            )

            if exito:
                self.modal_registro.open = False  
                
                # Reseteamos campos del formulario
                self.txt_tecnico.value = ""
                self.txt_costo.value = "0.00"
                self.txt_descripcion.value = ""
                self.dd_unidad_especifica.value = None
                self.dd_categoria.value = None
                self.banner_error.value = ""
                
                # Forzamos la recarga inmediata de la tabla antes de renderizar la página principal
                self.cargar_datos_tabla(e.page)   
            else:
                self.banner_error.value = f"❌ {msg}"
                
            e.page.update()
        except Exception as ex:
            print(f"[-] Error crítico en guardar_servicio_click: {ex}")
            self.banner_error.value = f"⚠️ Error al guardar en BD: {str(ex)}"
            e.page.update()