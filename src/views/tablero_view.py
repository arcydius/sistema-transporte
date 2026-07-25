import flet as ft
from controllers.maestro_controller import obtener_camiones

class TableroView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # --- Banner de Diagnóstico ---
        self.banner_error = ft.Text(value="", color="red", size=14, weight=ft.FontWeight.BOLD)
        
        # --- Componentes de Indicadores (KPIs) ---
        self.txt_total_camiones = ft.Text("0", size=26, weight=ft.FontWeight.BOLD, color="blue")
        self.txt_alertas_rcv = ft.Text("0", size=26, weight=ft.FontWeight.BOLD, color="orange")
        self.txt_alertas_trimestre = ft.Text("0", size=26, weight=ft.FontWeight.BOLD, color="red")
        
        # --- Tabla de Alertas ---
        self.tabla_alertas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Unidad / Placa", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo de Servicio / Alerta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Observaciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        self.cargar_datos_tablero()

        # Tarjetas de Resumen (KPIs)
        kpi_row = ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Total Flota Registrada", size=13, color=ft.Colors.GREY_700),
                        self.txt_total_camiones
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=15,
                    expand=True
                ),
                expand=True
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Alertas RCV Pendientes", size=13, color=ft.Colors.GREY_700),
                        self.txt_alertas_rcv
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=15,
                    expand=True
                ),
                expand=True
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Alertas Trimestre", size=13, color=ft.Colors.GREY_700),
                        self.txt_alertas_trimestre
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=15,
                    expand=True
                ),
                expand=True
            ),
        ], spacing=15)

        btn_actualizar = ft.ElevatedButton(
            content=ft.Text("Actualizar Tablero"),
            icon=ft.Icons.REFRESH,
            on_click=self.actualizar_click
        )

        return ft.Column([
            ft.Row([
                ft.Text("Panel Principal: Alertas (RCV/Trimestre)", size=28, weight=ft.FontWeight.BOLD),
                btn_actualizar
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.banner_error,
            ft.Container(height=5),
            kpi_row,
            ft.Container(height=15),
            ft.Text("Estado de Documentación y Vencimientos", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=5),
            ft.Container(
                content=ft.ListView([self.tabla_alertas], expand=True),
                expand=True
            )
        ], expand=True)

    def cargar_datos_tablero(self, page_context=None):
        try:
            camiones = obtener_camiones()
            total_camiones = len(camiones) if camiones else 0
            self.txt_total_camiones.value = str(total_camiones)
            
            self.tabla_alertas.rows.clear()
            
            rcv_pendientes = 0
            trim_pendientes = 0

            if camiones:
                for c in camiones:
                    placa = getattr(c, 'placa', 'S/P')
                    marca = getattr(c, 'marca', 'Unidad')
                    
                    # Rellenar con los datos de la flota
                    self.tabla_alertas.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{marca} ({placa})", weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text("Seguro RCV / Trimestre")),
                                ft.DataCell(ft.Text("Al día", color="green", weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text("Sin novedades registradas")),
                            ]
                        )
                    )
            
            self.txt_alertas_rcv.value = str(rcv_pendientes)
            self.txt_alertas_trimestre.value = str(trim_pendientes)
            self.banner_error.value = ""
            
            if page_context:
                page_context.update()
        except Exception as ex:
            self.banner_error.value = f"⚠️ Error al sincronizar métricas del tablero: {str(ex)}"
            if page_context:
                page_context.update()

    def actualizar_click(self, e):
        self.cargar_datos_tablero(e.page)