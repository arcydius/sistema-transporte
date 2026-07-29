import os
import sys
sys_src_path = os.path.abspath(os.path.dirname(__file__))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import flet as ft

# 1. Importamos nuestro componente reutilizable
from components.sidebar import MenuLateral

# 2. Importamos todas nuestras vistas
from views.login_view import LoginView
from views.tablero_view import TableroView
from views.fletes_view import FletesView
from views.maestros_view import MaestrosView
from views.mantenimiento_view import MantenimientoView
from views.nomina_view import NominaView
from views.configuracion_view import ConfiguracionView
from controllers.configuracion_controller import asegurar_usuario_default

def main(page: ft.Page):
    page.title = "Sistema de Gestión - Transporte Montenegro"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.window.maximized = True
    page.bgcolor = "#F0F4F8"

    # Garantizar que exista usuario por defecto (admin / admin123)
    try:
        asegurar_usuario_default()
    except Exception as ex:
        print(f"[-] Error al verificar usuario default: {ex}")

    def iniciar_sesion_exitosa(usuario):
        vistas = [
            TableroView(),
            FletesView(),
            MaestrosView(),
            MantenimientoView(),
            NominaView(),
            ConfiguracionView()
        ]

        area_central = ft.Container(
            expand=True,
            content=vistas[0],
            padding=20
        )

        def cambiar_modulo(e):
            indice = e.control.selected_index
            vista_seleccionada = vistas[indice]
            
            if hasattr(vista_seleccionada, 'cargar_datos_tablero'):
                try:
                    vista_seleccionada.cargar_datos_tablero(page)
                except Exception as ex:
                    print(f"[-] Error refrescando tablero {indice}: {ex}")
            elif hasattr(vista_seleccionada, 'cargar_datos_bd'):
                try:
                    vista_seleccionada.cargar_datos_bd()
                except Exception as ex:
                    print(f"[-] Error refrescando vista {indice}: {ex}")
            elif hasattr(vista_seleccionada, 'cargar_opciones_choferes'):
                try:
                    vista_seleccionada.cargar_opciones_choferes()
                except Exception as ex:
                    print(f"[-] Error refrescando opciones choferes: {ex}")

            area_central.content = vista_seleccionada
            page.update()

        def cerrar_sesion_click(e):
            page.controls.clear()
            page.add(login_view)
            page.update()

        rail = MenuLateral(al_cambiar_ruta=cambiar_modulo, al_cerrar_sesion=cerrar_sesion_click)
        contenedor_rail = ft.Container(
            content=rail,
            bgcolor="#1E293B",
            width=125
        )
        
        page.controls.clear()
        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        contenedor_rail,
                        ft.VerticalDivider(width=1, color="#334155"),
                        area_central, 
                    ],
                ),
            )
        )
        page.update()

    login_view = LoginView(on_login_success=iniciar_sesion_exitosa)

    page.controls.clear()
    page.add(login_view)
    page.update()

if __name__ == "__main__":
    ft.run(main)