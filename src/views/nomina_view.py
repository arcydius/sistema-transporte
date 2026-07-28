import os
import sys
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import flet as ft
from datetime import datetime, date
from controllers.maestro_controller import obtener_choferes
from controllers.nomina_controller import (
    obtener_fletes_pendientes_chofer,
    calcular_resumen_comision,
    registrar_pago_nomina,
    obtener_nominas_filtradas,
    obtener_detalles_nomina,
    eliminar_nomina_y_liberar_viajes
)
from utils.pdf_generator import generar_pdf_recibo_nomina, abrir_pdf

def _formatear_fecha(val, formato="%d/%m/%Y"):
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime(formato)
    return str(val)

class NominaView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # Estado interno de la pestaña "Registrar Pago"
        self.fletes_pendientes_actuales = []
        self.resumen_actual = {
            "total_fletes": 0.0,
            "total_gasoil": 0.0,
            "base_calculo": 0.0,
            "monto_comision": 0.0,
            "cantidad_viajes": 0
        }

        # Estado interno de la pestaña "Historial"
        self.historial_nominas = []
        self.id_nomina_eliminar = None

        # --- CONTROLES DE LA PESTAÑA 1: REGISTRAR PAGO ---
        self.dd_chofer_registro = ft.Dropdown(
            label="Seleccionar Chofer",
            expand=True,
            options=[],
            on_select=self.limpiar_tabla_pendientes
        )

        self.dp_desde_registro = ft.DatePicker(on_change=self._on_fecha_desde_registro_change)
        self.dp_hasta_registro = ft.DatePicker(on_change=self._on_fecha_hasta_registro_change)

        self.txt_fecha_desde_reg = ft.TextField(label="Fecha Desde", read_only=True, expand=True)
        self.btn_picker_desde_reg = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            tooltip="Seleccionar fecha desde",
            on_click=lambda e: self.abrir_calendario(self.dp_desde_registro, e)
        )

        self.txt_fecha_hasta_reg = ft.TextField(label="Fecha Hasta", read_only=True, expand=True)
        self.btn_picker_hasta_reg = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            tooltip="Seleccionar fecha hasta",
            on_click=lambda e: self.abrir_calendario(self.dp_hasta_registro, e)
        )

        self.btn_buscar_fletes = ft.Button(
            content=ft.Text("Buscar Fletes y Calcular"),
            icon=ft.Icons.SEARCH,
            bgcolor="#1565C0",
            color="white",
            on_click=self.buscar_fletes_click
        )

        # Tarjetas de Resumen Financiero en Tiempo Real
        self.lbl_total_fletes = ft.Text("$0.00", size=18, weight=ft.FontWeight.BOLD, color="blue")
        self.lbl_total_gasoil = ft.Text("$0.00", size=18, weight=ft.FontWeight.BOLD, color="orange")
        self.lbl_base_calculo = ft.Text("$0.00", size=18, weight=ft.FontWeight.BOLD, color="grey")
        self.lbl_comision_neto = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color="green")
        self.lbl_cant_fletes = ft.Text("0 viajes detectados", size=13, italic=True)

        self.tabla_fletes_pendientes = ft.DataTable(
            expand=True,
            column_spacing=90,
            columns=[
                ft.DataColumn(label=ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Chofer", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Ruta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Cant.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Mora ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Total ($)", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.btn_guardar_pago = ft.Button(
            content=ft.Text("Registrar Pago de Nómina"),
            icon=ft.Icons.SAVE,
            bgcolor="#2E7D32",
            color="white",
            on_click=lambda e: self.procesar_pago_click(e, generar_pdf=False)
        )

        self.btn_guardar_pdf = ft.Button(
            content=ft.Text("Registrar e Imprimir PDF"),
            icon=ft.Icons.PICTURE_AS_PDF,
            bgcolor="#00838F",
            color="white",
            on_click=lambda e: self.procesar_pago_click(e, generar_pdf=True)
        )

        # --- CONTROLES DE LA PESTAÑA 2: HISTORIAL Y FILTROS ---
        self.dd_filtro_chofer = ft.Dropdown(
            label="Filtrar por Chofer",
            expand=True,
            options=[ft.dropdown.Option(key="all", text="Todos los Choferes")]
        )

        self.dp_desde_filtro = ft.DatePicker(on_change=self._on_fecha_desde_filtro_change)
        self.dp_hasta_filtro = ft.DatePicker(on_change=self._on_fecha_hasta_filtro_change)

        self.txt_fecha_desde_filtro = ft.TextField(label="Período Desde", read_only=True, expand=True)
        self.btn_picker_desde_filtro = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.abrir_calendario(self.dp_desde_filtro, e)
        )

        self.txt_fecha_hasta_filtro = ft.TextField(label="Período Hasta", read_only=True, expand=True)
        self.btn_picker_hasta_filtro = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.abrir_calendario(self.dp_hasta_filtro, e)
        )

        self.btn_filtrar_historial = ft.Button(
            content=ft.Text("Aplicar Filtros"),
            icon=ft.Icons.FILTER_ALT,
            bgcolor="#1976D2",
            color="white",
            on_click=self.aplicar_filtros_historial
        )

        self.btn_limpiar_filtros = ft.Button(
            content=ft.Text("Limpiar Filtros"),
            icon=ft.Icons.REFRESH,
            on_click=self.limpiar_filtros_historial
        )

        self.tabla_historial = ft.DataTable(
            expand=True,
            column_spacing=65,
            columns=[
                ft.DataColumn(label=ft.Text("N° RECIBO", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Emisión", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Chofer", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Período", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Total Fletes ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Total Gasoil ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Pago Chofer 20% ($)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        # --- MODAL DE CONFIRMACIÓN Y DETALLE ---
        self.modal_confirmacion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text("¿Está seguro de que desea eliminar este registro de nómina? Los viajes vinculados volverán a quedar pendientes."),
            actions=[
                ft.Button("Cancelar", on_click=self.cerrar_modal_confirmacion),
                ft.Button("Eliminar y Liberar", icon=ft.Icons.DELETE_FOREVER, bgcolor="red", color="white", on_click=self.confirmar_eliminacion_real)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.modal_detalle = ft.AlertDialog(
            modal=False,
            title=ft.Text("Detalle de Recibo de Nómina"),
            content=ft.Container(width=600, height=400, content=ft.Text("Cargando...")),
            actions=[
                ft.Button("Cerrar", on_click=self.cerrar_modal_detalle)
            ]
        )

        self.content = self.inicializar_vista()

    def mostrar_mensaje(self, page, texto, color="green"):
        if page:
            page.snack_bar = ft.SnackBar(content=ft.Text(texto, color="white"), bgcolor=color)
            page.snack_bar.open = True
            page.update()

    def abrir_calendario(self, date_picker, e):
        self.asegurar_overlays(e.page)
        date_picker.open = True
        e.page.update()

    def _on_fecha_desde_registro_change(self, e):
        if hasattr(self.dp_desde_registro, 'value') and self.dp_desde_registro.value:
            self.txt_fecha_desde_reg.value = _formatear_fecha(self.dp_desde_registro.value, "%Y-%m-%d")
            self.update()

    def _on_fecha_hasta_registro_change(self, e):
        if hasattr(self.dp_hasta_registro, 'value') and self.dp_hasta_registro.value:
            self.txt_fecha_hasta_reg.value = _formatear_fecha(self.dp_hasta_registro.value, "%Y-%m-%d")
            self.update()

    def _on_fecha_desde_filtro_change(self, e):
        if hasattr(self.dp_desde_filtro, 'value') and self.dp_desde_filtro.value:
            self.txt_fecha_desde_filtro.value = _formatear_fecha(self.dp_desde_filtro.value, "%Y-%m-%d")
            self.update()

    def _on_fecha_hasta_filtro_change(self, e):
        if hasattr(self.dp_hasta_filtro, 'value') and self.dp_hasta_filtro.value:
            self.txt_fecha_hasta_filtro.value = _formatear_fecha(self.dp_hasta_filtro.value, "%Y-%m-%d")
            self.update()

    def asegurar_overlays(self, page):
        if page and hasattr(page, 'overlay'):
            for dp in [self.dp_desde_registro, self.dp_hasta_registro, self.dp_desde_filtro, self.dp_hasta_filtro]:
                if dp not in page.overlay:
                    page.overlay.append(dp)
            if self.modal_confirmacion not in page.overlay:
                page.overlay.append(self.modal_confirmacion)
            if self.modal_detalle not in page.overlay:
                page.overlay.append(self.modal_detalle)

    def cargar_opciones_choferes(self):
        choferes = obtener_choferes()
        self.dd_chofer_registro.options.clear()
        self.dd_filtro_chofer.options.clear()

        self.dd_filtro_chofer.options.append(ft.dropdown.Option(key="all", text="Todos los Choferes"))

        if choferes:
            for c in choferes:
                cid = str(c.id_chofer)
                cname = c.nombre_completo
                cced = getattr(c, 'cedula_identidad', '')
                label = f"{cname} (C.I: {cced})" if cced else cname

                self.dd_chofer_registro.options.append(ft.dropdown.Option(key=cid, text=label))
                self.dd_filtro_chofer.options.append(ft.dropdown.Option(key=cid, text=label))

    def cargar_datos_bd(self):
        self.cargar_opciones_choferes()
        self.cargar_historial_tabla()

    def inicializar_vista(self):
        self.cargar_datos_bd()

        # Construcción Pestaña 1: Registrar Pago
        card_resumen = ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("Resumen de Liquidación Automática (Comisión 20%)", weight=ft.FontWeight.BOLD, size=16),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("Total Fletes", size=12, color="grey"), self.lbl_total_fletes]),
                        ft.Column([ft.Text("Costo Gasoil (-)", size=12, color="grey"), self.lbl_total_gasoil]),
                        ft.Column([ft.Text("Base (Fletes - Gasoil)", size=12, color="grey"), self.lbl_base_calculo]),
                        ft.Column([ft.Text("PAGO CHOFER (20%)", size=13, weight=ft.FontWeight.BOLD, color="green"), self.lbl_comision_neto]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=5),
                    self.lbl_cant_fletes
                ])
            ),
            bgcolor="#F4F6F8"
        )

        pestana_registro = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([self.dd_chofer_registro]),
                ft.Row([
                    ft.Row([self.txt_fecha_desde_reg, self.btn_picker_desde_reg], expand=True),
                    ft.Row([self.txt_fecha_hasta_reg, self.btn_picker_hasta_reg], expand=True),
                    self.btn_buscar_fletes
                ]),
                ft.Container(height=10),
                card_resumen,
                ft.Container(height=10),
                ft.Text("Fletes Detectados en el Período:", weight=ft.FontWeight.BOLD, size=15),
                ft.Container(
                    content=ft.Row([self.tabla_fletes_pendientes], expand=True, scroll=ft.ScrollMode.AUTO),
                    border=ft.Border.all(1, "#E0E0E0"),
                    border_radius=8,
                    padding=5,
                    expand=True
                ),
                ft.Container(height=15),
                ft.Row([self.btn_guardar_pago, self.btn_guardar_pdf], alignment=ft.MainAxisAlignment.END, spacing=15)
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

        # Construcción Pestaña 2: Historial
        pestana_historial = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    self.dd_filtro_chofer,
                    ft.Row([self.txt_fecha_desde_filtro, self.btn_picker_desde_filtro], expand=True),
                    ft.Row([self.txt_fecha_hasta_filtro, self.btn_picker_hasta_filtro], expand=True),
                ]),
                ft.Row([self.btn_filtrar_historial, self.btn_limpiar_filtros], alignment=ft.MainAxisAlignment.END, spacing=10),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Row([self.tabla_historial], expand=True, scroll=ft.ScrollMode.AUTO),
                    border=ft.Border.all(1, "#E0E0E0"),
                    border_radius=8,
                    padding=5,
                    expand=True
                )
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

        self.pestanas_contenido = [pestana_registro, pestana_historial]
        self.contenedor_pestana = ft.Container(content=self.pestanas_contenido[0], expand=True)

        self.btn_tab_registro = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, color="white", size=18),
                ft.Text("Registrar Nuevo Pago", color="white", weight=ft.FontWeight.BOLD, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="#1565C0",
            padding=ft.Padding.symmetric(vertical=10, horizontal=20),
            border_radius=8,
            ink=True,
            on_click=lambda e: self.cambiar_pestana(0, e)
        )

        self.btn_tab_historial = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HISTORY, color="#555555", size=18),
                ft.Text("Consultar Historial", color="#555555", weight=ft.FontWeight.BOLD, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="#E0E0E0",
            padding=ft.Padding.symmetric(vertical=10, horizontal=20),
            border_radius=8,
            ink=True,
            on_click=lambda e: self.cambiar_pestana(1, e)
        )

        self.tabs_bar = ft.Row([self.btn_tab_registro, self.btn_tab_historial], spacing=10)

        # Cargar datos iniciales del historial
        self.cargar_historial_tabla()

        return ft.Column([
            ft.Text("Gestión de Nómina y Comisiones de Choferes", size=26, weight=ft.FontWeight.BOLD),
            ft.Container(height=5),
            self.tabs_bar,
            ft.Container(height=10),
            self.contenedor_pestana
        ], expand=True)

    def cambiar_pestana(self, indice, e):
        self.contenedor_pestana.content = self.pestanas_contenido[indice]

        if indice == 0:
            self.btn_tab_registro.bgcolor = "#1565C0"
            self.btn_tab_registro.content.controls[0].color = "white"
            self.btn_tab_registro.content.controls[1].color = "white"

            self.btn_tab_historial.bgcolor = "#E0E0E0"
            self.btn_tab_historial.content.controls[0].color = "#555555"
            self.btn_tab_historial.content.controls[1].color = "#555555"
        else:
            self.btn_tab_registro.bgcolor = "#E0E0E0"
            self.btn_tab_registro.content.controls[0].color = "#555555"
            self.btn_tab_registro.content.controls[1].color = "#555555"

            self.btn_tab_historial.bgcolor = "#1565C0"
            self.btn_tab_historial.content.controls[0].color = "white"
            self.btn_tab_historial.content.controls[1].color = "white"

            self.cargar_historial_tabla(e.page if hasattr(e, 'page') else None)

        if hasattr(e, 'page') and e.page:
            e.page.update()
        else:
            self.update()

    def limpiar_tabla_pendientes(self, e=None):
        self.fletes_pendientes_actuales.clear()
        self.tabla_fletes_pendientes.rows.clear()
        self.resumen_actual = {"total_fletes": 0.0, "total_gasoil": 0.0, "base_calculo": 0.0, "monto_comision": 0.0, "cantidad_viajes": 0}
        self._actualizar_tarjeta_resumen()
        if e and hasattr(e, 'page') and e.page:
            e.page.update()

    def _actualizar_tarjeta_resumen(self):
        r = self.resumen_actual
        self.lbl_total_fletes.value = f"${r['total_fletes']:,.2f}"
        self.lbl_total_gasoil.value = f"${r['total_gasoil']:,.2f}"
        self.lbl_base_calculo.value = f"${r['base_calculo']:,.2f}"
        self.lbl_comision_neto.value = f"${r['monto_comision']:,.2f}"
        self.lbl_cant_fletes.value = f"{r['cantidad_viajes']} viajes incluidos para liquidar comisión (20%)."

    def buscar_fletes_click(self, e):
        chofer_id = self.dd_chofer_registro.value
        if not chofer_id:
            self.mostrar_mensaje(e.page, "Por favor seleccione un chofer.", "orange")
            return

        f_desde = self.txt_fecha_desde_reg.value
        f_hasta = self.txt_fecha_hasta_reg.value

        self.fletes_pendientes_actuales = obtener_fletes_pendientes_chofer(
            id_chofer=int(chofer_id),
            fecha_desde=f_desde,
            fecha_hasta=f_hasta
        )

        self.tabla_fletes_pendientes.rows.clear()

        if self.fletes_pendientes_actuales:
            for v in self.fletes_pendientes_actuales:
                cant = getattr(v, 'cantidad_fletes', 1) or 1
                costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
                mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
                total_ruta = cant * costo_u

                fecha_str = _formatear_fecha(v.fecha_operacion, "%d/%m/%Y")
                chofer_str = v.chofer.nombre_completo if getattr(v, 'chofer', None) else "N/A"
                cliente_str = v.cliente.nombre_cliente if getattr(v, 'cliente', None) else "N/A"
                ruta_str = v.ruta.descripcion_trayecto if getattr(v, 'ruta', None) else "N/A"

                self.tabla_fletes_pendientes.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(fecha_str)),
                        ft.DataCell(ft.Text(chofer_str, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(cliente_str)),
                        ft.DataCell(ft.Text(ruta_str)),
                        ft.DataCell(ft.Text(str(cant))),
                        ft.DataCell(ft.Text(f"${mora:,.2f}", color="orange")),
                        ft.DataCell(ft.Text(f"${total_ruta:,.2f}", weight=ft.FontWeight.BOLD, color="blue")),
                    ])
                )

            self.resumen_actual = calcular_resumen_comision(self.fletes_pendientes_actuales)
            self.mostrar_mensaje(e.page, f"Se encontraron {len(self.fletes_pendientes_actuales)} fletes pendientes.", "green")
        else:
            self.resumen_actual = {"total_fletes": 0.0, "total_gasoil": 0.0, "base_calculo": 0.0, "monto_comision": 0.0, "cantidad_viajes": 0}
            self.mostrar_mensaje(e.page, "No se encontraron fletes pendientes para este chofer en las fechas seleccionadas.", "orange")

        self._actualizar_tarjeta_resumen()
        e.page.update()

    def procesar_pago_click(self, e, generar_pdf=False):
        chofer_id = self.dd_chofer_registro.value
        if not chofer_id:
            self.mostrar_mensaje(e.page, "Por favor seleccione un chofer.", "red")
            return

        if not self.fletes_pendientes_actuales:
            self.mostrar_mensaje(e.page, "No hay fletes pendientes para registrar este pago.", "red")
            return

        viajes_ids = [v.id_viaje for v in self.fletes_pendientes_actuales]
        f_emision = datetime.now().strftime("%Y-%m-%d")
        f_desde = self.txt_fecha_desde_reg.value or f_emision
        f_hasta = self.txt_fecha_hasta_reg.value or f_emision

        exito, msg, nueva_nomina = registrar_pago_nomina(
            id_chofer=int(chofer_id),
            fecha_emision=f_emision,
            periodo_desde=f_desde,
            periodo_hasta=f_hasta,
            viajes_ids=viajes_ids
        )

        if exito and nueva_nomina:
            self.mostrar_mensaje(e.page, msg, "green")
            
            if generar_pdf:
                try:
                    nomina_full, chofer_obj, viajes_full = obtener_detalles_nomina(nueva_nomina.id_nomina)
                    pdf_path = generar_pdf_recibo_nomina(nomina_full, chofer_obj, viajes_full)
                    abrir_pdf(pdf_path)
                    self.mostrar_mensaje(e.page, f"PDF generado y abierto: {pdf_path}", "green")
                except Exception as ex_pdf:
                    print(f"Error generando PDF: {ex_pdf}")
                    self.mostrar_mensaje(e.page, f"Nómina guardada pero ocurrió un error al abrir el PDF: {ex_pdf}", "orange")

            # Limpiar formulario
            self.limpiar_tabla_pendientes()
            self.txt_fecha_desde_reg.value = ""
            self.txt_fecha_hasta_reg.value = ""
            self.cargar_historial_tabla(e.page)
        else:
            self.mostrar_mensaje(e.page, f"❌ {msg}", "red")

        e.page.update()

    def cargar_historial_tabla(self, page_context=None):
        chofer_id = self.dd_filtro_chofer.value
        f_desde = self.txt_fecha_desde_filtro.value
        f_hasta = self.txt_fecha_hasta_filtro.value

        self.historial_nominas = obtener_nominas_filtradas(
            id_chofer=int(chofer_id) if chofer_id and chofer_id != "all" else None,
            fecha_desde=f_desde,
            fecha_hasta=f_hasta
        )

        self.tabla_historial.rows.clear()
        if self.historial_nominas:
            for n in self.historial_nominas:
                nid = n.id_nomina
                recibo_str = f"NOM-{nid:05d}"
                f_emision = _formatear_fecha(n.fecha_emision, "%d/%m/%Y")
                
                chofer_str = n.chofer.nombre_completo if getattr(n, 'chofer', None) else "N/A"
                periodo_str = f"{_formatear_fecha(n.periodo_desde, '%d/%m')} al {_formatear_fecha(n.periodo_hasta, '%d/%m/%Y')}"
                
                tot_fletes = float(n.total_ingresos_fletes or 0)
                tot_gasoil = float(n.total_costo_gasoil or 0)
                pago_chofer = float(n.monto_neto_comision or 0)

                self.tabla_historial.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(recibo_str, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(f_emision)),
                        ft.DataCell(ft.Text(chofer_str, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(periodo_str)),
                        ft.DataCell(ft.Text(f"${tot_fletes:,.2f}", color="blue")),
                        ft.DataCell(ft.Text(f"${tot_gasoil:,.2f}", color="orange")),
                        ft.DataCell(ft.Text(f"${pago_chofer:,.2f}", weight=ft.FontWeight.BOLD, color="green")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    icon_color="#00838F",
                                    tooltip="Imprimir Recibo PDF",
                                    on_click=lambda e, id_n=nid: self.reimprimir_pdf_click(e, id_n)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY,
                                    icon_color="blue",
                                    tooltip="Ver Detalle de Viajes",
                                    on_click=lambda e, id_n=nid: self.ver_detalle_click(e, id_n)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color="red",
                                    tooltip="Eliminar Nómina y Liberar Viajes",
                                    on_click=lambda e, id_n=nid: self.preparar_eliminacion(e, id_n)
                                ),
                            ])
                        )
                    ])
                )
        if page_context:
            page_context.update()

    def aplicar_filtros_historial(self, e):
        self.cargar_historial_tabla(e.page)

    def limpiar_filtros_historial(self, e):
        self.dd_filtro_chofer.value = "all"
        self.txt_fecha_desde_filtro.value = ""
        self.txt_fecha_hasta_filtro.value = ""
        self.cargar_historial_tabla(e.page)

    def reimprimir_pdf_click(self, e, id_nomina):
        try:
            nomina_obj, chofer_obj, viajes_lista = obtener_detalles_nomina(id_nomina)
            if nomina_obj:
                pdf_path = generar_pdf_recibo_nomina(nomina_obj, chofer_obj, viajes_lista)
                abrir_pdf(pdf_path)
                self.mostrar_mensaje(e.page, f"PDF generado y abierto: {pdf_path}", "green")
            else:
                self.mostrar_mensaje(e.page, "No se encontró el registro de nómina.", "red")
        except Exception as ex:
            self.mostrar_mensaje(e.page, f"Error al generar PDF: {ex}", "red")

    def ver_detalle_click(self, e, id_nomina):
        nomina_obj, chofer_obj, viajes_lista = obtener_detalles_nomina(id_nomina)
        if not nomina_obj:
            self.mostrar_mensaje(e.page, "No se encontró el registro.", "red")
            return

        cols_det = [
            ft.DataColumn(label=ft.Text("N° Viaje")),
            ft.DataColumn(label=ft.Text("Fecha")),
            ft.DataColumn(label=ft.Text("Cliente")),
            ft.DataColumn(label=ft.Text("Ruta")),
            ft.DataColumn(label=ft.Text("Flete ($)")),
            ft.DataColumn(label=ft.Text("Gasoil ($)")),
        ]

        rows_det = []
        for v in viajes_lista:
            cant = getattr(v, 'cantidad_fletes', 1) or 1
            costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
            mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
            flete_total = (cant * costo_u) + mora
            gasoil_v = float(getattr(v, 'costo_total_gasoil', 0) or 0)

            rows_det.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{v.id_viaje}")),
                ft.DataCell(ft.Text(_formatear_fecha(v.fecha_operacion, "%d/%m/%Y"))),
                ft.DataCell(ft.Text(v.cliente.nombre_cliente if getattr(v, 'cliente', None) else "N/A")),
                ft.DataCell(ft.Text(v.ruta.descripcion_trayecto if getattr(v, 'ruta', None) else "N/A")),
                ft.DataCell(ft.Text(f"${flete_total:,.2f}")),
                ft.DataCell(ft.Text(f"${gasoil_v:,.2f}")),
            ]))

        tabla_det = ft.DataTable(columns=cols_det, rows=rows_det)

        self.modal_detalle.title = ft.Text(f"Detalle Recibo NOM-{id_nomina:05d} - {chofer_obj.nombre_completo if chofer_obj else ''}")
        self.modal_detalle.content = ft.Container(
            width=650,
            height=400,
            content=ft.Column([
                ft.Text(f"Período: {_formatear_fecha(nomina_obj.periodo_desde, '%d/%m/%Y')} al {_formatear_fecha(nomina_obj.periodo_hasta, '%d/%m/%Y')}"),
                ft.Text(f"Total Fletes: ${float(nomina_obj.total_ingresos_fletes or 0):,.2f} | Total Gasoil: ${float(nomina_obj.total_costo_gasoil or 0):,.2f}"),
                ft.Text(f"Pago Neto Chofer (20%): ${float(nomina_obj.monto_neto_comision or 0):,.2f}", weight=ft.FontWeight.BOLD, color="green"),
                ft.Divider(),
                ft.Container(content=ft.ListView([tabla_det], expand=True), expand=True)
            ])
        )

        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_detalle
        self.modal_detalle.open = True
        e.page.update()

    def cerrar_modal_detalle(self, e):
        self.modal_detalle.open = False
        e.page.update()

    def preparar_eliminacion(self, e, id_nomina):
        self.id_nomina_eliminar = id_nomina
        self.asegurar_overlays(e.page)
        e.page.dialog = self.modal_confirmacion
        self.modal_confirmacion.open = True
        e.page.update()

    def confirmar_eliminacion_real(self, e):
        if self.id_nomina_eliminar:
            exito, msg = eliminar_nomina_y_liberar_viajes(self.id_nomina_eliminar)
            self.modal_confirmacion.open = False
            self.id_nomina_eliminar = None
            if exito:
                self.cargar_historial_tabla(e.page)
                self.mostrar_mensaje(e.page, msg, "green")
            else:
                self.mostrar_mensaje(e.page, f"Error: {msg}", "red")
                e.page.update()

    def cerrar_modal_confirmacion(self, e):
        self.modal_confirmacion.open = False
        self.id_nomina_eliminar = None
        e.page.update()