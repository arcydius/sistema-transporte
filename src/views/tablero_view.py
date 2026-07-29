import flet as ft
from controllers.dashboard_controller import obtener_metricas_dashboard

class TableroView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # Banner de Mensajes / Diagnóstico
        self.banner_error = ft.Text(value="", color="red", size=14, weight=ft.FontWeight.BOLD)
        self.lbl_nombre_mes = ft.Text(value="Mes Actual", size=14, color="#1565C0", weight=ft.FontWeight.BOLD)
        
        # --- Indicadores Operativos y Financieros del Mes (KPIs) ---
        self.txt_viajes_mes = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#1565C0")
        self.txt_ingresos_mes = ft.Text("$0.00", size=20, weight=ft.FontWeight.BOLD, color="blue")
        self.txt_gasoil_mes = ft.Text("$0.00", size=20, weight=ft.FontWeight.BOLD, color="orange")
        self.txt_utilidad_mes = ft.Text("$0.00", size=24, weight=ft.FontWeight.BOLD, color="green")
        
        # --- Indicadores de Flota y Personal ---
        self.txt_choferes = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color="black87")
        self.txt_camiones = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color="black87")
        self.txt_remolques = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color="black87")
        self.txt_fletes_pendientes = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color="orange")
        
        # --- Banner Destacado para Alertas Urgentes ---
        self.container_alerta_urgente = ft.Container(visible=False)

        # --- Tabla de Alertas ---
        self.tabla_alertas = ft.DataTable(  # type: ignore
            expand=True,
            column_spacing=40,
            columns=[
                ft.DataColumn(label=ft.Text("Unidad / Vehículo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Documento / Alerta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Fecha Vencimiento", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Observaciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        self.cargar_datos_tablero()

        # Fila 1: KPIs Financieros del Mes Actual
        kpis_financieros = ft.Row([
            ft.Card(
                elevation=3,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.LOCAL_SHIPPING, color="#1565C0", size=20), ft.Text("Viajes del Mes", size=13, weight=ft.FontWeight.BOLD, color="black54")]),
                        self.txt_viajes_mes,
                        ft.Text("Se reinicia cada mes", size=11, color="grey")
                    ]),
                    padding=15, expand=True
                ),
                expand=True
            ),
            ft.Card(
                elevation=3,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.ATTACH_MONEY, color="blue", size=20), ft.Text("Ingresos Fletes", size=13, weight=ft.FontWeight.BOLD, color="black54")]),
                        self.txt_ingresos_mes,
                        ft.Text("Total facturado del mes", size=11, color="grey")
                    ]),
                    padding=15, expand=True
                ),
                expand=True
            ),
            ft.Card(
                elevation=3,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.LOCAL_GAS_STATION, color="orange", size=20), ft.Text("Gasto Gasoil", size=13, weight=ft.FontWeight.BOLD, color="black54")]),
                        self.txt_gasoil_mes,
                        ft.Text("Combustible gastado", size=11, color="grey")
                    ]),
                    padding=15, expand=True
                ),
                expand=True
            ),
            ft.Card(
                elevation=3,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="green", size=20), ft.Text("Utilidad Neta Estimada", size=13, weight=ft.FontWeight.BOLD, color="black54")]),
                        self.txt_utilidad_mes,
                        ft.Text("Ingresos - Gasoil - Comisiones", size=11, color="grey")
                    ]),
                    padding=15, expand=True
                ),
                expand=True
            ),
        ], spacing=15)

        # Fila 2: Flota y Cobros
        kpis_flota = ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color="blue", size=24),
                        ft.Column([ft.Text("Choferes Activos", size=12, color="grey"), self.txt_choferes], spacing=2)
                    ]),
                    padding=12, expand=True
                ), expand=True
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.COMMUTE, color="indigo", size=24),
                        ft.Column([ft.Text("Camiones Registrados", size=12, color="grey"), self.txt_camiones], spacing=2)
                    ]),
                    padding=12, expand=True
                ), expand=True
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.RV_HOOKUP, color="purple", size=24),
                        ft.Column([ft.Text("Remolques / Bateas", size=12, color="grey"), self.txt_remolques], spacing=2)
                    ]),
                    padding=12, expand=True
                ), expand=True
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PENDING_ACTIONS, color="orange", size=24),
                        ft.Column([ft.Text("Fletes Pend. Cobro Cliente", size=12, color="grey"), self.txt_fletes_pendientes], spacing=2)
                    ]),
                    padding=12, expand=True
                ), expand=True
            ),
        ], spacing=15)

        btn_actualizar = ft.Button(
            content=ft.Text("Actualizar Tablero"),
            icon=ft.Icons.REFRESH,
            bgcolor="#1565C0",
            color="white",
            on_click=self.actualizar_click
        )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Tablero de Control Operativo y Financiero", size=24, weight=ft.FontWeight.BOLD),
                    self.lbl_nombre_mes
                ], spacing=2),
                btn_actualizar
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.banner_error,
            ft.Container(height=5),
            kpis_financieros,
            ft.Container(height=10),
            kpis_flota,
            ft.Container(height=15),
            self.container_alerta_urgente,
            ft.Text("Alertas y Vencimientos de Documentación (RCV / Trimestres)", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=5),
            ft.Container(
                content=ft.Row([self.tabla_alertas], expand=True, scroll=ft.ScrollMode.AUTO),
                border=ft.Border.all(1, "#E0E0E0"),
                border_radius=8,
                padding=5,
                expand=True
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def cargar_datos_tablero(self, page_context=None):
        try:
            m = obtener_metricas_dashboard()
            
            self.lbl_nombre_mes.value = f"📅 Resumen del Mes: {m.get('mes_nombre', '')}"
            self.txt_viajes_mes.value = f"{m.get('cant_viajes_mes', 0)} viajes"
            self.txt_ingresos_mes.value = f"${m.get('ingresos_fletes_mes', 0.0):,.2f}"
            self.txt_gasoil_mes.value = f"${m.get('gasoil_mes', 0.0):,.2f}"
            
            utilidad = m.get('utilidad_neta_mes', 0.0)
            self.txt_utilidad_mes.value = f"${utilidad:,.2f}"
            self.txt_utilidad_mes.color = "green" if utilidad >= 0 else "red"

            self.txt_choferes.value = str(m.get('cant_choferes', 0))
            self.txt_camiones.value = str(m.get('cant_camiones', 0))
            self.txt_remolques.value = str(m.get('cant_remolques', 0))
            self.txt_fletes_pendientes.value = str(m.get('fletes_pendientes_cliente', 0))

            # Banner de alerta urgente destacada
            urgentes = m.get('cant_alertas_urgentes', 0)
            proximas = m.get('cant_alertas_proximas', 0)

            if urgentes > 0:
                self.container_alerta_urgente.visible = True
                self.container_alerta_urgente.content = ft.Container(
                    bgcolor="#FFEBEE",
                    border=ft.Border.all(1.5, "red"),
                    border_radius=8,
                    padding=12,
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="red", size=26),
                        ft.Text(f"⚠️ URGENTE: Hay {urgentes} documento(s) VENCIDO(S) (RCV / Trimestre). Requiere renovación inmediata.", color="red", weight=ft.FontWeight.BOLD, size=14)
                    ])
                )
            elif proximas > 0:
                self.container_alerta_urgente.visible = True
                self.container_alerta_urgente.content = ft.Container(
                    bgcolor="#FFF3E0",
                    border=ft.Border.all(1.5, "orange"),
                    border_radius=8,
                    padding=12,
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="orange", size=26),
                        ft.Text(f"⚡ ADVERTENCIA: Hay {proximas} documento(s) por vencer en los próximos 15 días.", color="orange", weight=ft.FontWeight.BOLD, size=14)
                    ])
                )
            else:
                self.container_alerta_urgente.visible = False

            # Llenar Tabla de Alertas
            self.tabla_alertas.rows.clear()
            alertas = m.get('alertas', [])
            
            if alertas:
                for a in alertas:
                    nivel = a.get('nivel')
                    estado_str = a.get('estado')
                    bg_badge = "red" if nivel == "URGENTE" else "orange"
                    
                    self.tabla_alertas.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(a.get('unidad', ''), weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(a.get('tipo', ''))),
                            ft.DataCell(ft.Text(a.get('fecha', ''))),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(estado_str, color="white", weight=ft.FontWeight.BOLD, size=11),
                                    bgcolor=bg_badge,
                                    padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                                    border_radius=12
                                )
                            ),
                            ft.DataCell(ft.Text(a.get('obs', ''), color="red" if nivel == "URGENTE" else "orange", weight=ft.FontWeight.BOLD)),
                        ])
                    )
            else:
                self.tabla_alertas.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text("Toda la Flota")),
                        ft.DataCell(ft.Text("Seguros RCV / Trimestres")),
                        ft.DataCell(ft.Text("Al día")),
                        ft.DataCell(ft.Container(content=ft.Text("AL DÍA", color="white", weight=ft.FontWeight.BOLD, size=11), bgcolor="green", padding=ft.Padding.symmetric(vertical=4, horizontal=10), border_radius=12)),
                        ft.DataCell(ft.Text("✅ Sin vencimientos pendientes", color="green")),
                    ])
                )

            self.banner_error.value = ""
            if page_context:
                page_context.update()
        except Exception as ex:
            print(f"Error al sincronizar dashboard: {ex}")
            self.banner_error.value = f"⚠️ Error al sincronizar métricas del tablero: {str(ex)}"
            if page_context:
                page_context.update()

    def actualizar_click(self, e):
        self.cargar_datos_tablero(e.page)

    def cargar_datos_bd(self, page_context=None):
        """Método invocado automáticamente al seleccionar el Tablero."""
        self.cargar_datos_tablero(page_context)