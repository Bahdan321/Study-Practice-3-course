import flet as ft
from db import db_manager

def LoginView(page: ft.Page):
    """
    Вьюшка для авторизации пользователей
    """

    identifier_field = ft.TextField(label="Имя пользователя или Email", width=300)
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(value="", color=ft.colors.RED)

    def login_clicked(e):
        """
        Вход в аккаунт пользователя
        """
        identifier = identifier_field.value
        password = password_field.value
        error_text.value = ""

        if not identifier or not password:
            error_text.value = "Пожалуйста, заполните все поля."
            page.update()
            return

        user = db_manager.verify_user(identifier, password)

        if user:
            print(f"User {user['username']} logged in successfully.")
            page.session.set("user_id", user['user_id'])
            page.session.set("username", user['username'])
            page.go("/home")
        else:
            error_text.value = "Неверное имя пользователя/email или пароль."
            page.update()

    def go_to_register(e):
        """
        Переход на страницу регистрации
        """
        page.go("/register")

    return ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text("Вход", size=30),
                    identifier_field,
                    password_field,
                    ft.ElevatedButton("Войти", on_click=login_clicked),
                    error_text,
                    ft.TextButton("Нет аккаунта? Зарегистрироваться", on_click=go_to_register),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )