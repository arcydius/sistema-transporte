import flet as ft
from datetime import datetime
from controllers.configuracion_controller import (
    obtener_usuarios, registrar_usuario, actualizar_usuario, eliminar_usuario,
    cambiar_contrasena, crear_backup, obtener_lista_backups, restaurar_backup,
    eliminar_backup
)

class ConfiguracionView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # Banner de Mensajes y Diagnóstico
        self.banner_mensaje = ft.Text(value="", color="green", size=14, weight=ft.FontWeight.BOLD)
        
        # Filtro de texto para campos
        self.filtro_letras = ft.InputFilter(allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$", replacement_string="")
        self.filtro_username = ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9_]*$", replacement_string="")
        
        # --- Componentes de Usuarios ---
        self.tabla_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        self.btn_nuevo_usuario = ft.Button(
            content=ft.Text("Añadir Usuario"),
            icon=ft.Icons.ADD,
            bgcolor="blue",
            color="white",
            on_click=self.abrir_modal_crear_usuario
        )

        # --- Componentes de Seguridad (Cambio de Contraseña) ---
        self.txt_pass_actual = ft.TextField(
            label="Contraseña Actual", 
            password=True, 
            can_reveal_password=True, 
            expand=True
        )
        self.txt_pass_nuevo = ft.TextField(
            label="Nueva Contraseña", 
            password=True, 
            can_reveal_password=True, 
            expand=True
        )
        self.txt_pass_confirmar = ft.TextField(
            label="Confirmar Nueva Contraseña", 
            password=True, 
            can_reveal_password=True, 
            expand=True
        )
        
        self.btn_guardar_pass = ft.Button(
            content=ft.Text("Actualizar Contraseña"),
            bgcolor="blue",
            color="white",
            on_click=self.cambiar_contrasena_click
        )
        
        # --- Componentes de Respaldos ---
        self.btn_crear_backup = ft.Button(
            content=ft.Text("Crear Respaldo de Base de Datos"),
            icon=ft.Icons.BACKUP,
            bgcolor="green",
            color="white",
            on_click=self.crear_respaldo_click
        )
        
        self.btn_restaurar_backup = ft.Button(
            content=ft.Text("Historial y Restauración"),
            icon=ft.Icons.RESTORE,
            bgcolor="orange",
            color="white",
            on_click=self.abrir_modal_restaurar
        )

        self.content = self.inicializar_vista()
        self.cargar_tabla_usuarios()

    def inicializar_vista(self):
        return ft.Column([
            ft.Text("Configuración del Sistema: Usuarios, Seguridad y Respaldos", size=24, weight=ft.FontWeight.BOLD),
            self.banner_mensaje,
            ft.Divider(height=20),
            
            # Contenedor desplazable para las secciones de configuración
            ft.Container(
                content=ft.ListView([
                    # --- Sección 1: Gestión de Usuarios ---
                    ft.Row([
                        ft.Column([
                            ft.Text("Gestión de Usuarios y Accesos", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Administra los usuarios autorizados para ingresar y utilizar la plataforma.", size=13, color=ft.Colors.GREY_700),
                        ], expand=True),
                        self.btn_nuevo_usuario
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.Container(
                        content=self.tabla_usuarios,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=10
                    ),
                    
                    ft.Divider(height=35),
                    
                    # --- Sección 2: Respaldos ---
                    ft.Text("Gestión de Respaldos (Base de Datos)", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Protege la información del sistema generando copias de seguridad de forma segura.", size=13, color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    ft.Row([
                        self.btn_crear_backup,
                        self.btn_restaurar_backup
                    ], spacing=15),
                    
                    ft.Divider(height=35),
                    
                    # --- Sección 3: Seguridad ---
                    ft.Text("Seguridad y Credenciales de Administrador", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Actualiza la contraseña de acceso principal para mantener segura la aplicación.", size=13, color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([self.txt_pass_actual]),
                            ft.Row([self.txt_pass_nuevo, self.txt_pass_confirmar]),
                            ft.Container(height=5),
                            ft.Row([self.btn_guardar_pass], alignment=ft.MainAxisAlignment.END)
                        ], spacing=15, tight=True),
                        width=650
                    )
                ], expand=True),
                expand=True
            )
        ], expand=True)

    def cargar_tabla_usuarios(self):
        self.tabla_usuarios.rows.clear()
        usuarios = obtener_usuarios()
        for u in usuarios:
            self.tabla_usuarios.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(u.id_admin))),
                ft.DataCell(ft.Text(str(u.username))),
                ft.DataCell(ft.Text(str(u.nombre_completo or ""))),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT, 
                        icon_color="blue", 
                        tooltip="Editar Usuario", 
                        on_click=lambda e, user=u: self.abrir_modal_editar_usuario(e, user)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE, 
                        icon_color="red", 
                        tooltip="Eliminar Usuario", 
                        on_click=lambda e, id_a=u.id_admin, un=u.username: self.abrir_modal_eliminar_usuario(e, id_a, un)
                    ),
                ])),
            ]))

    def abrir_modal_crear_usuario(self, e):
        tf_username = ft.TextField(label="Nombre de Usuario", input_filter=self.filtro_username, max_length=15)
        tf_nombre = ft.TextField(label="Nombre Completo", input_filter=self.filtro_letras)
        tf_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_username.error = "Requerido" if not tf_username.value else None
            tf_nombre.error = "Requerido" if not tf_nombre.value else None
            tf_password.error = "Requerido" if not tf_password.value else None

            if not tf_username.value or not tf_nombre.value or not tf_password.value:
                e.page.update()
                return

            exito, msj = registrar_usuario(tf_username.value, tf_password.value, tf_nombre.value)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                self.cargar_tabla_usuarios()
                cerrar()
            else:
                tf_username.error = msj
                e.page.update()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Añadir Nuevo Usuario"),
            content=ft.Column([
                tf_username,
                tf_nombre,
                tf_password
            ], tight=True, width=400),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Guardar", bgcolor="blue", color="white", on_click=guardar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def abrir_modal_editar_usuario(self, e, usuario):
        tf_username = ft.TextField(label="Nombre de Usuario", value=usuario.username, input_filter=self.filtro_username, max_length=15)
        tf_nombre = ft.TextField(label="Nombre Completo", value=usuario.nombre_completo or "", input_filter=self.filtro_letras)
        tf_password = ft.TextField(label="Nueva Contraseña (dejar en blanco para no cambiar)", password=True, can_reveal_password=True)

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def guardar(e_guardar):
            tf_username.error = "Requerido" if not tf_username.value else None
            tf_nombre.error = "Requerido" if not tf_nombre.value else None

            if not tf_username.value or not tf_nombre.value:
                e.page.update()
                return

            pass_val = tf_password.value.strip() if tf_password.value else None
            exito, msj = actualizar_usuario(usuario.id_admin, tf_username.value, tf_nombre.value, pass_val)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                self.cargar_tabla_usuarios()
                cerrar()
            else:
                tf_username.error = msj
                e.page.update()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Usuario '{usuario.username}'"),
            content=ft.Column([
                tf_username,
                tf_nombre,
                tf_password
            ], tight=True, width=400),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Actualizar", bgcolor="blue", color="white", on_click=guardar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def abrir_modal_eliminar_usuario(self, e, id_admin, username):
        def cerrar(e_cerrar=None):
            modal_eliminar.open = False
            e.page.update()

        def confirmar(e_conf):
            exito, msj = eliminar_usuario(id_admin)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                self.cargar_tabla_usuarios()
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
            cerrar()

        modal_eliminar = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color="red"),
            content=ft.Text(f"¿Estás seguro de que deseas eliminar al usuario '{username}'?"),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=confirmar, bgcolor="red", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal_eliminar)
        modal_eliminar.open = True
        e.page.update()

    def crear_respaldo_click(self, e):
        exito, msj = crear_backup()
        if exito:
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = f"✅ {msj}"
        else:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ {msj}"
        e.page.update()

    def abrir_modal_restaurar(self, e):
        backups = obtener_lista_backups()
        
        lista_backups_controls = []
        if not backups:
            lista_backups_controls.append(ft.Text("No se encontraron archivos de respaldo generados."))
        else:
            for b in backups:
                tamano_kb = b["size_bytes"] / 1024
                lista_backups_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(b["filename"], weight=ft.FontWeight.BOLD),
                                ft.Text(f"Fecha: {b['fecha']} | Tamaño: {tamano_kb:.1f} KB", size=12, color=ft.Colors.GREY_700),
                            ], expand=True),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color="red",
                                    tooltip="Eliminar",
                                    on_click=lambda ev, path=b["filepath"]: confirmar_eliminacion(ev, path)
                                ),
                                ft.Button(
                                    "Restaurar",
                                    icon=ft.Icons.RESTORE,
                                    bgcolor="orange",
                                    color="white",
                                    on_click=lambda ev, path=b["filepath"]: confirmar_restauracion(ev, path)
                                )
                            ])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=5
                    )
                )

        def cerrar(e_cerrar=None):
            modal.open = False
            e.page.update()

        def confirmar_restauracion(ev, filepath):
            cerrar()
            exito, msj = restaurar_backup(filepath)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
            e.page.update()

        def confirmar_eliminacion(ev, filepath):
            cerrar()
            exito, msj = eliminar_backup(filepath)
            if exito:
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = f"✅ {msj}"
                # Volver a abrir el modal para que se refresque la lista
                self.abrir_modal_restaurar(e)
            else:
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
                e.page.update()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Historial y Restauración de Respaldos"),
            content=ft.Container(
                content=ft.Column(lista_backups_controls, scroll=ft.ScrollMode.AUTO),
                width=550,
                height=350
            ),
            actions=[
                ft.Button("Cerrar", on_click=cerrar)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def cambiar_contrasena_click(self, e):
        if not self.txt_pass_actual.value or not self.txt_pass_nuevo.value or not self.txt_pass_confirmar.value:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = "⚠️ Todos los campos de contraseña son obligatorios."
            e.page.update()
            return

        if self.txt_pass_nuevo.value != self.txt_pass_confirmar.value:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = "❌ Las nuevas contraseñas no coinciden."
            e.page.update()
            return

        exito, msj = cambiar_contrasena(None, self.txt_pass_actual.value, self.txt_pass_nuevo.value)
        if exito:
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = f"🔒 {msj}"
            self.txt_pass_actual.value = ""
            self.txt_pass_nuevo.value = ""
            self.txt_pass_confirmar.value = ""
        else:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ {msj}"
        e.page.update()