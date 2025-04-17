import flet as ft
from db import db_manager

def HomeView(page: ft.Page):
    """
    Вьюшка домашней страницы
    """

    def logout_clicked(e):
        """
        Выход из аккаунта, удаление сессии и токена.
        """
        token = page.session.get("session_token")
        print("Пользователь: ",token)
        
        if token:
            db_manager.delete_session(token)
            page.client_storage.remove("session_token")
            print("Persistent session token removed from DB and local storage.")

        page.session.clear()
        page.go("/login")

    return ft.View(
        "/home",
        [
            ft.AppBar(title=ft.Text("Домашняя страница"), actions=[
                ft.IconButton(ft.icons.LOGOUT, tooltip="Выйти", on_click=logout_clicked)
            ]),
            ft.Column(
                [
                    ft.Text(f"Добро пожаловать, {page.session.get("username")}!" if page.session.get("username") else "Добро пожаловать!", size=24),
                    ft.Text("Это ваша домашняя страница финансового менеджера."),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )