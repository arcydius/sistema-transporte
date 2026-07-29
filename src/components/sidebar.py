import flet as ft

def MenuLateral(al_cambiar_ruta, al_cerrar_sesion=None):
    color_inactivo = "#94A3B8"  # Gris plata brillante de alto contraste
    color_activo = "white"

    trailing_control = None
    if al_cerrar_sesion:
        trailing_control = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color="#EF4444",
                tooltip="Cerrar Sesión",
                on_click=al_cerrar_sesion
            ),
            padding=ft.Padding.only(bottom=15),
            margin=ft.Margin.only(top=20)
        )

    return ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=125,  # Ancho suficiente fijo para que 'Mantenimiento' en negrita no redimensione el sidebar
        min_extended_width=200,
        bgcolor="#1E293B",  # Fondo Azul Marino Slate
        indicator_color="#3B82F6",  # Cápsula Azul Vibrante
        unselected_label_text_style=ft.TextStyle(color=color_inactivo, size=12),
        selected_label_text_style=ft.TextStyle(color=color_activo, weight=ft.FontWeight.BOLD, size=12),
        on_change=al_cambiar_ruta,
        trailing=trailing_control,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.DASHBOARD, color=color_activo),
                label="Tablero"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.LOCAL_SHIPPING_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.LOCAL_SHIPPING, color=color_activo),
                label="Fletes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.FOLDER_SHARED_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.FOLDER_SHARED, color=color_activo),
                label="Maestros"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.BUILD_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.BUILD, color=color_activo),
                label="Mantenimiento"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.MONETIZATION_ON_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.MONETIZATION_ON, color=color_activo),
                label="Nómina"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=color_inactivo),
                selected_icon=ft.Icon(ft.Icons.SETTINGS, color=color_activo),
                label="Configuración"
            ),
        ],
    )