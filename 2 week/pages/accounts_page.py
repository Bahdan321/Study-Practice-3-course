import flet as ft
from db import db_manager
from icons import get_icon_by_name

def AccountsView(page: ft.Page):
    """
    Представление для управления счетами пользователя.
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/accounts", [ft.Text("Ошибка: Пользователь не авторизован.")])

    accounts_list_view = ft.ListView(spacing=10, auto_scroll=True)

    def load_accounts():
        """
        Загружает счета из базы данных и обновляет список.
        """
        print("Загрузка счетов для представления /accounts...")
        accounts_list_view.controls.clear()
        user_accounts = db_manager.get_accounts_by_user(user_id)
        if not user_accounts:
            accounts_list_view.controls.append(
                ft.Container(
                    ft.Text("У вас пока нет счетов."),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for acc in user_accounts:
                accounts_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(get_icon_by_name(acc["icon"])),
                        title=ft.Text(acc["name"]),
                        subtitle=ft.Text(
                            f"{acc['description'] if acc['description'] else ''}"
                        ),
                        trailing=ft.Text(
                            f"{acc['balance']:.2f} {acc['currency_symbol']}"
                        ),
                    )
                )
        if page.controls:
             page.update()

    def go_to_add_account(e):
        page.go("/accounts/add")

    load_accounts()

    return ft.View(
        "/accounts",
        [
            ft.AppBar(
                title=ft.Text("Мои счета"),
                actions=[
                    ft.IconButton(
                        ft.icons.ARROW_BACK,
                        tooltip="Назад",
                        on_click=lambda _: page.go("/home"),
                    ),
                ],
            ),
            ft.Column(
                [
                    ft.Container(
                        content=accounts_list_view,
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Добавить счет",
                            icon=ft.icons.ADD_CARD_OUTLINED,
                            on_click=go_to_add_account,
                            height=50,
                            width=250
                        ),
                        padding=ft.padding.only(top=10, bottom=20),
                        alignment=ft.alignment.center
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0,
    )
