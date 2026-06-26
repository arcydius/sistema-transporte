import flet as ft

def main(page: ft.Page):
    # Configuración básica del sistema
    page.title = "Sistema de Gestión - Transporte Montenegro"
    page.theme_mode = ft.ThemeMode.LIGHT 

    # --- 1. CONTENIDO DINÁMICO (LAS PANTALLAS) ---
    txt_tablero = ft.Text("Panel Principal: Alertas y Gráficos (Dashboard)", size=30)
    txt_fletes = ft.Text("Módulo de Fletes: Registro de Viajes", size=30)
    txt_choferes = ft.Text("Gestión de Choferes: Directorio", size=30)

    # Contenedor central que cambiará mágicamente
    area_central = ft.Container(
        expand=True,
        content=txt_tablero, # Arranca mostrando el tablero
        padding=20
    )

    # --- 2. LÓGICA DE CAMBIO DE MÓDULO ---
    def cambiar_modulo(e):
        indice = e.control.selected_index
        if indice == 0:
            area_central.content = txt_tablero
        elif indice == 1:
            area_central.content = txt_fletes
        elif indice == 2:
            area_central.content = txt_choferes
            
        page.update() # Refrescamos la pantalla

    # --- 3. TU MENÚ LATERAL FUNCIONAL ---
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        on_change=cambiar_modulo, # Conectamos tu menú a nuestra función
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Tablero",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCAL_SHIPPING_OUTLINED,
                selected_icon=ft.Icons.LOCAL_SHIPPING,
                label="Fletes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINE,
                selected_icon=ft.Icons.PEOPLE,
                label="Choferes",
            ),
        ],
    )

    
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                expand=True,
                controls=[
                    ft.SelectionArea(content=rail),
                    ft.VerticalDivider(width=1),
                    area_central, # Aquí inyectamos el área que cambia, reemplazando tu "Body!"
                ],
            ),
        )
    )

if __name__ == "__main__":
    ft.run(main)