import flet as ft

def MenuLateral(al_cambiar_ruta):
    return ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        on_change=al_cambiar_ruta, # Recibe la función que cambia las pantallas
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Tablero"),
            ft.NavigationRailDestination(icon=ft.Icons.LOCAL_SHIPPING_OUTLINED, selected_icon=ft.Icons.LOCAL_SHIPPING, label="Fletes"),
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER_SHARED_OUTLINED, selected_icon=ft.Icons.FOLDER_SHARED, label="Maestros"),
            ft.NavigationRailDestination(icon=ft.Icons.BUILD_OUTLINED, selected_icon=ft.Icons.BUILD, label="Mantenimiento"),
            ft.NavigationRailDestination(icon=ft.Icons.MONETIZATION_ON_OUTLINED, selected_icon=ft.Icons.MONETIZATION_ON, label="Nómina"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configuración"),
        ],
    )