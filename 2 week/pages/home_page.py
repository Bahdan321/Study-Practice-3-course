import flet as ft

def HomeView(page: ft.Page):
    """Creates the Home View (placeholder)."""

    username = page.session.get("username") # Get username from session if needed

    def logout_clicked(e):
        """Handles logout."""
        # Clear session data
        page.session.clear()
        # Redirect to login page
        page.go("/login")

    return ft.View(
        "/home", # Route for this view
        [
            ft.AppBar(title=ft.Text("Домашняя страница"), actions=[
                ft.IconButton(ft.icons.LOGOUT, tooltip="Выйти", on_click=logout_clicked)
            ]),
            ft.Column(
                [
                    ft.Text(f"Добро пожаловать, {username}!" if username else "Добро пожаловать!", size=24),
                    ft.Text("Это ваша домашняя страница финансового менеджера."),
                    # Add more content here later
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START, # Align content to the top
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )