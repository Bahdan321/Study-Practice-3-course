import flet as ft
from db import db_manager

def HomeView(page: ft.Page):
    """
    Вьюшка домашней страницы
    """
    username = page.session.get("username")

    def logout_clicked(e):
        """
        Выход из аккаунта, удаление сессии и токена.
        """
        token = page.session.get("session_token")
        if token:
            db_manager.delete_session(token)
            page.client_storage.remove("session_token")
            print("Persistent session token removed from DB and local storage.")

        page.session.clear()
        page.go("/login")

    def go_to_accounts(e):
        page.go("/accounts")

    return ft.View(
        "/home",
        [
            ft.AppBar(title=ft.Text("Домашняя страница"), actions=[
                ft.IconButton(ft.icons.LOGOUT, tooltip="Выйти", on_click=logout_clicked)
            ]),
            ft.Column(
                [
                    ft.Text(f"Добро пожаловать, {username}!" if username else "Добро пожаловать!", size=24),
                    ft.Text("Это ваша домашняя страница финансового менеджера."),
                    ft.ElevatedButton(
                        "Управление счетами",
                        icon=ft.icons.ACCOUNT_BALANCE_WALLET,
                        on_click=go_to_accounts
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )