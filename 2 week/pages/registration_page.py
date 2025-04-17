import flet as ft
from db import db_manager

def RegistrationView(page: ft.Page):
    """
    Вьюшка для регистрации пользователей
    """

    username_field = ft.TextField(label="Имя пользователя", width=300)
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(value="", color=ft.colors.RED)

    def register_clicked(e):
        """
        Регистрация пользователя
        """
        username = username_field.value
        email = email_field.value
        password = password_field.value
        error_text.value = ""

        if not username or not email or not password:
            error_text.value = "Пожалуйста, заполните все поля."
            page.update()
            return

        success = db_manager.add_user(username, email, password)

        if success:
            print(f"User {username} registered successfully.")
            username_field.value = ""
            email_field.value = ""
            password_field.value = ""
            page.go("/login")
        else:
            error_text.value = "Ошибка регистрации. Имя пользователя или email уже существует."
            page.update()


    def go_to_login(e):
        """
        Переход на страницу входа
        """
        page.go("/login")

    return ft.View(
        "/register",
        [
            ft.Column(
                [
                    ft.Text("Регистрация", size=30),
                    username_field,
                    email_field,
                    password_field,
                    ft.ElevatedButton("Зарегистрироваться", on_click=register_clicked),
                    error_text,
                    ft.TextButton("Уже есть аккаунт? Войти", on_click=go_to_login),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )