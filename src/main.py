import os
import sys
sys_src_path = os.path.abspath(os.path.dirname(__file__))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import flet as ft

# 1. Importamos nuestro componente reutilizable
from components.sidebar import MenuLateral

# 2. Importamos todas nuestras vistas
from views.tablero_view import TableroView
from views.fletes_view import FletesView
from views.maestros_view import MaestrosView
from views.mantenimiento_view import MantenimientoView
from views.nomina_view import NominaView
from views.configuracion_view import ConfiguracionView

def main(page: ft.Page):
    page.title = "Sistema de Gestión - Transporte Montenegro"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.window.maximized = True
    page.bgcolor = "#F0F4F8"  # Fondo gris slate suave que elimina el blanco deslumbrante sin modificar vistas

    # Agrupamos todas las vistas en una lista que coincide con el orden del menú
    vistas = [
        TableroView(),
        FletesView(),
        MaestrosView(),
        MantenimientoView(),
        NominaView(),
        ConfiguracionView()
    ]

    # Contenedor central dinámico
    area_central = ft.Container(
        expand=True,
        content=vistas[0], # Arranca mostrando el Tablero
        padding=20
    )

    # Lógica centralizada para cambiar de pantalla y refrescar datos automáticamente
    def cambiar_modulo(e):
        indice = e.control.selected_index
        vista_seleccionada = vistas[indice]
        
        # Invocar la actualización automática de datos de la vista destino
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

    # Instanciamos el menú y le pasamos nuestra función
    rail = MenuLateral(al_cambiar_ruta=cambiar_modulo)
    contenedor_rail = ft.Container(
        content=rail,
        bgcolor="#1E293B",
        width=125
    )
    
    # Ensamblaje de la interfaz
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

if __name__ == "__main__":
    ft.run(main)