import flet as ft
import datetime
from controllers.maestro_controller import (
    obtener_camiones,
    obtener_clientes,
    obtener_rutas,
    obtener_choferes,
    obtener_remolques,
    registrar_flete
)

class FletesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # --- Banner de Mensajes y Diagnóstico ---
        self.banner_mensaje = ft.Text(value="", color="green", size=14, weight=ft.FontWeight.BOLD)
        
        # --- Componentes de Totales ---
        self.txt_costo_ruta = ft.Text("Costo Ruta: $0.00", size=16, color="black54")
        self.txt_total_flete = ft.Text("Total del Flete: $0.00", size=24, weight=ft.FontWeight.BOLD, color="#1976d2")

        padding_uniforme = ft.Padding.symmetric(vertical=10, horizontal=12)

        # -- Sección 1: Datos del Servicio --
        self.fecha_tf = ft.TextField(
            label="Fecha de Operación", 
            value=datetime.datetime.now().strftime("%d/%m/%Y"), 
            read_only=True, 
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
        
        # Dropdown de Ruta
        self.ruta_dd = ft.Dropdown(label="Ruta Ejecutada", options=[], expand=2, dense=True, content_padding=padding_uniforme, on_select=self.recalcular_total)

        self.estatus_dd = ft.Dropdown(
            label="Estatus de Pago", 
            options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Pagado")], 
            value="Pendiente",
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme
        )

        # -- Sección 2: Asignación de Recursos --
        self.chofer_dd = ft.Dropdown(label="Chofer Asignado", options=[], expand=1, dense=True, content_padding=padding_uniforme)
        self.camion_dd = ft.Dropdown(label="Camión", options=[], expand=1, dense=True, content_padding=padding_uniforme)
        self.remolque_dd = ft.Dropdown(label="Remolque (Opcional)", options=[], expand=1, dense=True, content_padding=padding_uniforme)

        # -- Sección 3: Datos Operativos y Financieros --
        self.gasoil_tf = ft.TextField(
            label="Gasoil Consumido (Lts)", 
            input_filter=ft.InputFilter(regex_string=r"[0-9.]"), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme
        )
        
        self.mora_tf = ft.TextField(
            label="Mora / Espera ($)", 
            value="0", 
            input_filter=ft.InputFilter(regex_string=r"[0-9.]"), 
            expand=1, 
            dense=True, 
            content_padding=padding_uniforme
        )
        self.mora_tf.on_change = self.recalcular_total

        # Calendario
        self.calendario = ft.DatePicker(
            on_change=self.fecha_seleccionada,
            first_date=datetime.datetime(2024, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            help_text="Seleccione la fecha del flete"
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        self.cargar_datos_bd()

        return ft.Container(
            padding=20,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Registro de Fletes", size=28, weight=ft.FontWeight.BOLD, color="black87"),
                    self.banner_mensaje,
                    ft.Divider(height=10, color="transparent"),

                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("1. Datos del Servicio", weight=ft.FontWeight.BOLD, color="#1976d2"),
                                ft.Divider(),
                                ft.Row([self.fecha_tf, self.cliente_dd]),
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
                                ft.Row([self.gasoil_tf, self.mora_tf]),
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
                                ft.Column([self.txt_costo_ruta, self.txt_total_flete]),
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
            if choferes:
                for ch in choferes:
                    nombre_ch = getattr(ch, 'nombre_completo', str(ch))
                    id_ch = str(getattr(ch, 'id_chofer', nombre_ch))
                    self.chofer_dd.options.append(ft.dropdown.Option(key=id_ch, text=nombre_ch))
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

    def recalcular_total(self, e):
        costo_ruta = 0.0
        if self.ruta_dd.value:
            opcion_seleccionada = next((opt for opt in self.ruta_dd.options if opt.key == self.ruta_dd.value), None)
            if opcion_seleccionada and opcion_seleccionada.data is not None:
                try:
                    costo_ruta = float(opcion_seleccionada.data)
                except Exception:
                    costo_ruta = 0.0
            
        self.txt_costo_ruta.value = f"Costo Ruta: ${costo_ruta:.2f}"

        mora = float(self.mora_tf.value) if self.mora_tf.value != "" else 0.0
        total = costo_ruta + mora
        self.txt_total_flete.value = f"Total del Flete: ${total:.2f}"
        
        self.txt_costo_ruta.update()
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

    def limpiar_formulario(self, e):
        self.fecha_tf.value = datetime.datetime.now().strftime("%d/%m/%Y")
        self.cliente_dd.value = None
        self.ruta_dd.value = None
        self.estatus_dd.value = "Pendiente"
        self.chofer_dd.value = None
        self.camion_dd.value = None
        self.remolque_dd.value = None
        self.gasoil_tf.value = ""
        self.mora_tf.value = "0"
        self.txt_costo_ruta.value = "Costo Ruta: $0.00"
        self.txt_total_flete.value = "Total del Flete: $0.00"
        self.banner_mensaje.value = ""
        e.page.update()

    def guardar_flete_click(self, e):
        if not self.cliente_dd.value or not self.ruta_dd.value or not self.camion_dd.value:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = "⚠️ Por favor complete los campos obligatorios (Cliente, Ruta y Camión)."
            e.page.update()
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
            exito, msg = registrar_flete(
                id_cliente=self.cliente_dd.value,
                id_ruta=self.ruta_dd.value,
                id_chofer=self.chofer_dd.value,
                id_camion=self.camion_dd.value,
                id_remolque=self.remolque_dd.value if self.remolque_dd.value != "none" else None,
                estatus=self.estatus_dd.value,
                gasoil=self.gasoil_tf.value,
                mora=self.mora_tf.value,
                costo_unitario=costo_unitario
            )

            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msg}"
                self.limpiar_formulario(e)
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msg}"
            e.page.update()
        except Exception as ex:
            print(f"[-] Error al guardar flete: {ex}")
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"⚠️ Error en BD: {str(ex)}"
            e.page.update()