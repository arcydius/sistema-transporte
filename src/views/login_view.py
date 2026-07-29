import flet as ft
from controllers.configuracion_controller import verificar_credenciales

class LoginView(ft.Container):
    def __init__(self, on_login_success):
        super().__init__()
        self.expand = True
        self.on_login_success = on_login_success
        self.alignment = ft.Alignment(0, 0)
        self.bgcolor = "#0F172A"  # Dark Slate Background

        self.txt_usuario = ft.TextField(
            label="Usuario",
            hint_text="Ingrese su nombre de usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINED,
            autofocus=True,
            border_radius=8,
            on_submit=self._iniciar_sesion_click
        )

        self.txt_password = ft.TextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            password=True,
            can_reveal_password=True,
            border_radius=8,
            on_submit=self._iniciar_sesion_click
        )

        self.lbl_error = ft.Text(
            value="",
            color="red",
            size=13,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

        self.btn_ingresar = ft.Button(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGIN, color="white"),
                ft.Text("Iniciar Sesión", color="white", weight=ft.FontWeight.BOLD, size=15)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="#1565C0",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=18
            ),
            on_click=self._iniciar_sesion_click
        )

        # Card / Contenedor central de Login
        self.content = ft.Container(
            width=420,
            padding=35,
            bgcolor="white",
            border_radius=16,
            shadow=ft.BoxShadow(
                blur_radius=20,
                color="black54",
                offset=ft.Offset(0, 8)
            ),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.LOCAL_SHIPPING, size=55, color="#1565C0"),
                        bgcolor="#E3F2FD",
                        padding=15,
                        border_radius=50
                    ),
                    ft.Column([
                        ft.Text("TRANSPORTE MONTENEGRO", size=22, weight=ft.FontWeight.BOLD, color="#1E293B", text_align=ft.TextAlign.CENTER),
                        ft.Text("Sistema de Gestión de Transporte (SGTM)", size=13, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    ft.Divider(height=10, color="transparent"),
                    self.txt_usuario,
                    self.txt_password,
                    self.lbl_error,
                    ft.Container(height=5),
                    self.btn_ingresar,
                    ft.Divider(height=15, color="#E2E8F0"),
                    ft.Text("Credenciales por defecto: admin / admin123", size=11, italic=True, color="#94A3B8")
                ]
            )
        )

    def _iniciar_sesion_click(self, e):
        usuario = self.txt_usuario.value
        password = self.txt_password.value

        if not usuario or not password:
            self.lbl_error.value = "⚠️ Por favor ingrese su usuario y contraseña."
            self.update()
            return

        exito, resultado = verificar_credenciales(usuario, password)
        if exito:
            self.lbl_error.value = ""
            self.txt_password.value = ""
            self.on_login_success(resultado)
        else:
            self.lbl_error.value = f"❌ {resultado}"
            self.update()
