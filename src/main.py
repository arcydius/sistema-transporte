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

    # Lógica centralizada para cambiar de pantalla
    def cambiar_modulo(e):
        indice = e.control.selected_index
        area_central.content = vistas[indice]
        page.update()

    # Instanciamos el menú y le pasamos nuestra función
    rail = MenuLateral(al_cambiar_ruta=cambiar_modulo)
    
    # Ensamblaje de la interfaz
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                expand=True,
                controls=[
                    ft.SelectionArea(content=rail),
                    ft.VerticalDivider(width=1),
                    area_central, 
                ],
            ),
        )
    )

if __name__ == "__main__":
    ft.run(main)