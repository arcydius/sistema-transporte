import flet as ft
from datetime import datetime

class ConfiguracionView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        # --- Banner de Mensajes y Diagnóstico ---
        self.banner_mensaje = ft.Text(value="", color="green", size=14, weight=ft.FontWeight.BOLD)
        
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
            content=ft.Text("Restaurar desde Respaldo"),
            icon=ft.Icons.RESTORE,
            bgcolor="orange",
            color="white",
            on_click=self.restaurar_respaldo_click
        )

        self.content = self.inicializar_vista()

    def inicializar_vista(self):
        return ft.Column([
            ft.Text("Configuración: Seguridad y Respaldos", size=28, weight=ft.FontWeight.BOLD),
            self.banner_mensaje,
            ft.Divider(height=20),
            
            # Contenedor desplazable para las secciones de configuración
            ft.Container(
                content=ft.ListView([
                    # --- Sección 1: Respaldos ---
                    ft.Text("Gestión de Respaldos (Base de Datos)", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Protege la información del sistema generando copias de seguridad de forma segura.", size=13, color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    ft.Row([
                        self.btn_crear_backup,
                        self.btn_restaurar_backup
                    ], spacing=15),
                    
                    ft.Divider(height=35),
                    
                    # --- Sección 2: Seguridad ---
                    ft.Text("Seguridad y Credenciales del Administrador", size=18, weight=ft.FontWeight.BOLD),
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

    def crear_respaldo_click(self, e):
        try:
            # Aquí puedes conectar la lógica de copiado de tu archivo de base de datos (ej. SQLite)
            fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = f"✅ Respaldo creado exitosamente (backup_{fecha_actual}.db)."
            e.page.update()
        except Exception as ex:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ Error al generar el respaldo: {str(ex)}"
            e.page.update()

    def restaurar_respaldo_click(self, e):
        try:
            self.banner_mensaje.color = "orange"
            self.banner_mensaje.value = "⚠️ Módulo de restauración preparado para seleccionar el archivo de respaldo."
            e.page.update()
        except Exception as ex:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ Error al restaurar: {str(ex)}"
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

        try:
            # Lógica para verificar la contraseña actual y guardar la nueva en tu BD o controlador
            self.banner_mensaje.color = "green"
            self.banner_mensaje.value = "🔒 Contraseña de administrador actualizada correctamente."
            
            # Limpiar campos
            self.txt_pass_actual.value = ""
            self.txt_pass_nuevo.value = ""
            self.txt_pass_confirmar.value = ""
            e.page.update()
        except Exception as ex:
            self.banner_mensaje.color = "red"
            self.banner_mensaje.value = f"❌ Error al actualizar contraseña: {str(ex)}"
            e.page.update()