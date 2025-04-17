import flet as ft
from db import db_manager

def LoginView(page: ft.Page):
    """
    Вьюшка для авторизации пользователей
    """

    identifier_field = ft.TextField(label="Имя пользователя или Email", width=300)
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=300)
    remember_me_checkbox = ft.Checkbox(label="Запомнить меня", value=False,width=300)
    error_text = ft.Text(value="", color=ft.colors.RED)

    def login_clicked(e):
        """
        Вход в аккаунт пользователя
        """
        identifier = identifier_field.value
        password = password_field.value
        remember_me = remember_me_checkbox.value
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

            if remember_me:
                token = db_manager.create_session(user['user_id'])
                if token:
                    page.client_storage.set("session_token", token)
                    page.session.set("session_token", token)
                    print(f"Persistent session created, token stored locally: {token[:8]}...")
                else:
                    print("Failed to create persistent session token.")
            else:
                page.client_storage.remove("session_token")
                page.session.remove("session_token")

            page.go("/home")
        else:
            error_text.value = "Неверное имя пользователя/email или пароль."
            page.client_storage.remove("session_token")
            page.session.remove("session_token")
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
                    remember_me_checkbox,
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