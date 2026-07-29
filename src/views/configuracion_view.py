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
        self.tabla_usuarios = ft.DataTable(  # type: ignore
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
                    # --- Sección 2: Respaldos ---
                    ft.Text("Gestión de Respaldos (Base de Datos)", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Protege la información del sistema generando copias de seguridad de forma segura.", size=13, color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    ft.Row([
                        self.btn_crear_backup,
                        self.btn_restaurar_backup
                    ], spacing=15)
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

    def mostrar_mensaje(self, page, texto, color="green"):
        if page:
            snack = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE if color == "green" else ft.Icons.ERROR, color="white"),
                    ft.Text(texto, color="white", weight=ft.FontWeight.BOLD)
                ]),
                bgcolor=color,
                duration=4000
            )
            if snack not in page.overlay:
                page.overlay.append(snack)
            snack.open = True
            page.update()

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
                msj_txt = f"✅ {msj}"
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = msj_txt
                self.mostrar_mensaje(e.page, msj_txt, "green")
                self.cargar_tabla_usuarios()
                cerrar()
            else:
                tf_username.error = msj
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
                self.mostrar_mensaje(e.page, f"❌ {msj}", "red")
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
        if modal not in e.page.overlay:
            e.page.overlay.append(modal)
        modal.open = True
        e.page.update()

    def abrir_modal_editar_usuario(self, e, usuario):
        tf_username = ft.TextField(label="Nombre de Usuario", value=str(usuario.username), input_filter=self.filtro_username, max_length=15)
        tf_nombre = ft.TextField(label="Nombre Completo", value=str(usuario.nombre_completo or ""), input_filter=self.filtro_letras)
        
        # Campos de contraseña en panel desplegable retraíble
        tf_pass1 = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True)
        tf_pass2 = ft.TextField(label="Confirmar Nueva Contraseña", password=True, can_reveal_password=True)

        container_pass = ft.Container(
            visible=False,
            padding=12,
            bgcolor="#F8FAFC",
            border=ft.Border.all(1, "#CBD5E1"),
            border_radius=8,
            content=ft.Column([
                ft.Text("Cambio de Contraseña", weight=ft.FontWeight.BOLD, size=13, color="#1565C0"),
                tf_pass1,
                tf_pass2
            ], spacing=10)
        )

        def toggle_panel_pass(ev):
            container_pass.visible = not container_pass.visible
            if container_pass.visible:
                btn_toggle_pass.text = "Ocultar Cambio de Contraseña"
                btn_toggle_pass.icon = ft.Icons.KEY_OFF
            else:
                btn_toggle_pass.text = "Cambiar Contraseña"
                btn_toggle_pass.icon = ft.Icons.KEY
                tf_pass1.value = ""
                tf_pass2.value = ""
                tf_pass1.error = None
                tf_pass2.error = None
            if hasattr(ev, 'page') and ev.page:
                ev.page.update()
            elif hasattr(e, 'page') and e.page:
                e.page.update()

        btn_toggle_pass = ft.Button(
            "Cambiar Contraseña",
            icon=ft.Icons.KEY,
            on_click=toggle_panel_pass
        )

        def cerrar(e_cerrar=None):
            modal.open = False
            if hasattr(e, 'page') and e.page:
                e.page.update()

        def guardar(e_guardar):
            tf_username.error = "Requerido" if not tf_username.value else None
            tf_nombre.error = "Requerido" if not tf_nombre.value else None
            tf_pass1.error = None
            tf_pass2.error = None

            if not tf_username.value or not tf_nombre.value:
                e.page.update()
                return

            pass_val = None
            if container_pass.visible or (tf_pass1.value and tf_pass1.value.strip()) or (tf_pass2.value and tf_pass2.value.strip()):
                p1 = tf_pass1.value.strip() if tf_pass1.value else ""
                p2 = tf_pass2.value.strip() if tf_pass2.value else ""

                if not p1 or not p2:
                    if not p1: tf_pass1.error = "Ingrese la nueva contraseña"
                    if not p2: tf_pass2.error = "Confirme la nueva contraseña"
                    e.page.update()
                    return

                if p1 != p2:
                    tf_pass2.error = "Las contraseñas no coinciden"
                    self.mostrar_mensaje(e.page, "❌ Las contraseñas no coinciden.", "red")
                    e.page.update()
                    return

                pass_val = p1

            exito, msj = actualizar_usuario(int(usuario.id_admin), tf_username.value, tf_nombre.value, pass_val)
            if exito:
                msj_txt = f"✅ {msj}"
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = msj_txt
                self.mostrar_mensaje(e.page, msj_txt, "green")
                self.cargar_tabla_usuarios()
                cerrar()
            else:
                tf_username.error = msj
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = f"❌ {msj}"
                self.mostrar_mensaje(e.page, f"❌ {msj}", "red")
                e.page.update()

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Usuario '{usuario.username}'"),
            content=ft.Container(
                content=ft.Column([
                    tf_username,
                    tf_nombre,
                    ft.Container(height=5),
                    btn_toggle_pass,
                    container_pass
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=420
            ),
            actions=[
                ft.Button("Cancelar", on_click=cerrar),
                ft.Button("Actualizar", bgcolor="blue", color="white", on_click=guardar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if modal not in e.page.overlay:
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
                msj_txt = f"✅ {msj}"
                self.banner_mensaje.color = "green"
                self.banner_mensaje.value = msj_txt
                self.mostrar_mensaje(e.page, msj_txt, "green")
                self.cargar_tabla_usuarios()
            else:
                msj_err = f"❌ {msj}"
                self.banner_mensaje.color = "red"
                self.banner_mensaje.value = msj_err
                self.mostrar_mensaje(e.page, msj_err, "red")
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
            msj_txt = f"✅ {msj}"
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = msj_txt
            self.mostrar_mensaje(e.page, msj_txt, "green")
        else:
            msj_err = f"❌ {msj}"
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_err
            self.mostrar_mensaje(e.page, msj_err, "red")
        e.page.update()

    def abrir_modal_restaurar(self, e):
        columna_lista_backups = ft.Column(controls=[], scroll=ft.ScrollMode.AUTO, spacing=10)

        def recargar_controles_lista():
            backups = obtener_lista_backups()
            columna_lista_backups.controls.clear()

            if not backups:
                columna_lista_backups.controls.append(
                    ft.Container(
                        content=ft.Text("No se encontraron archivos de respaldo generados en el sistema.", color="grey"),
                        padding=20,
                        alignment=ft.Alignment(0, 0)
                    )
                )
            else:
                for b in backups:
                    tamano_kb = b["size_bytes"] / 1024
                    filename = b["filename"]
                    filepath = b["filepath"]
                    
                    columna_lista_backups.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color="#1565C0", size=26),
                                    ft.Column([
                                        ft.Text(filename, weight=ft.FontWeight.BOLD, size=13, color="#1565C0"),
                                        ft.Text(f"📅 {b['fecha']}   |   📦 {tamano_kb:.1f} KB", size=12, color=ft.Colors.GREY_700),
                                    ], spacing=2),
                                ], expand=True),
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="red",
                                        tooltip="Eliminar Respaldo",
                                        on_click=lambda ev, p=filepath, fn=filename: solicitar_confirmacion_eliminar(ev, p, fn)
                                    ),
                                    ft.Button(
                                        "Restaurar",
                                        icon=ft.Icons.RESTORE,
                                        bgcolor="orange",
                                        color="white",
                                        on_click=lambda ev, p=filepath, fn=filename: solicitar_confirmacion_restaurar(ev, p, fn)
                                    )
                                ], spacing=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=12,
                            bgcolor="#F8FAFC",
                            border=ft.Border.all(1, "#CBD5E1"),
                            border_radius=8
                        )
                    )

        recargar_controles_lista()

        def cerrar_dialogo(dlg):
            dlg.open = False
            e.page.update()

        def solicitar_confirmacion_restaurar(ev, filepath, filename):
            def ejecutar_restauracion(e_r):
                cerrar_dialogo(modal_confirmar)
                cerrar_dialogo(modal_principal)
                exito, msj = restaurar_backup(filepath)
                if exito:
                    msj_txt = f"✅ {msj}"
                    self.banner_mensaje.color = "green"
                    self.banner_mensaje.value = msj_txt
                    self.mostrar_mensaje(e.page, msj_txt, "green")
                else:
                    msj_err = f"❌ {msj}"
                    self.banner_mensaje.color = "red"
                    self.banner_mensaje.value = msj_err
                    self.mostrar_mensaje(e.page, msj_err, "red")
                e.page.update()

            modal_confirmar = ft.AlertDialog(
                modal=True,
                title=ft.Text("⚠️ Confirmar Restauración de Base de Datos", color="orange"),
                content=ft.Column([
                    ft.Text(f"¿Estás seguro de que deseas restaurar la base de datos a partir del respaldo:"),
                    ft.Text(filename, weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Text("\n¡ADVERTENCIA!: Los datos actuales de la aplicación serán actualizados con los registros de este respaldo. Esta acción es irreversible.", color="red", size=13)
                ], tight=True, width=450),
                actions=[
                    ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo(modal_confirmar)),
                    ft.Button("Confirmar Restauración", icon=ft.Icons.RESTORE, bgcolor="orange", color="white", on_click=ejecutar_restauracion),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            e.page.overlay.append(modal_confirmar)
            modal_confirmar.open = True
            e.page.update()

        def solicitar_confirmacion_eliminar(ev, filepath, filename):
            def ejecutar_eliminacion(e_el):
                cerrar_dialogo(modal_elim)
                exito, msj = eliminar_backup(filepath)
                if exito:
                    msj_txt = f"✅ {msj}"
                    self.banner_mensaje.color = "green"
                    self.banner_mensaje.value = msj_txt
                    self.mostrar_mensaje(e.page, msj_txt, "green")
                    # Refrescar dinámicamente la lista sin cerrar modal_principal
                    recargar_controles_lista()
                    modal_principal.update()
                else:
                    msj_err = f"❌ {msj}"
                    self.banner_mensaje.color = "red"
                    self.banner_mensaje.value = msj_err
                    self.mostrar_mensaje(e.page, msj_err, "red")
                    e.page.update()

            modal_elim = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Eliminación de Respaldo", color="red"),
                content=ft.Text(f"¿Estás seguro de eliminar el archivo de respaldo '{filename}'?"),
                actions=[
                    ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo(modal_elim)),
                    ft.Button("Eliminar Archivo", icon=ft.Icons.DELETE_FOREVER, bgcolor="red", color="white", on_click=ejecutar_eliminacion),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            e.page.overlay.append(modal_elim)
            modal_elim.open = True
            e.page.update()

        modal_principal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Historial y Restauración de Respaldos"),
            content=ft.Container(
                content=columna_lista_backups,
                width=600,
                height=380
            ),
            actions=[
                ft.Button("Cerrar", on_click=lambda _: cerrar_dialogo(modal_principal))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.overlay.append(modal_principal)
        modal_principal.open = True
        e.page.update()

    def cambiar_contrasena_click(self, e):
        if not self.txt_pass_actual.value or not self.txt_pass_nuevo.value or not self.txt_pass_confirmar.value:
            msj_err = "⚠️ Todos los campos de contraseña son obligatorios."
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_err
            self.mostrar_mensaje(e.page, msj_err, "red")
            return

        if self.txt_pass_nuevo.value != self.txt_pass_confirmar.value:
            msj_err = "❌ Las nuevas contraseñas no coinciden."
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_err
            self.mostrar_mensaje(e.page, msj_err, "red")
            return

        exito, msj = cambiar_contrasena(None, self.txt_pass_actual.value, self.txt_pass_nuevo.value)
        if exito:
            msj_txt = f"🔒 {msj}"
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = msj_txt
            self.mostrar_mensaje(e.page, msj_txt, "green")
            self.txt_pass_actual.value = ""
            self.txt_pass_nuevo.value = ""
            self.txt_pass_confirmar.value = ""
        else:
            msj_err = f"❌ {msj}"
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = msj_err
            self.mostrar_mensaje(e.page, msj_err, "red")
        e.page.update()