import flet as ft
from db import db_manager
from icons import get_icon_by_name
import functools # Import functools for partial

def AccountsView(page: ft.Page):
    """
    Представление для управления счетами пользователя.
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/accounts", [ft.Text("Ошибка: Пользователь не авторизован.")])

    accounts_list_view = ft.ListView(spacing=10, auto_scroll=True)

    # --- Functions ---
    def go_to_edit_account(account_id: int, e: ft.ControlEvent):
        """Navigates to the edit page for the specific account."""
        print(f"Navigating to edit account ID: {account_id}")
        page.go(f"/accounts/edit/{account_id}") # Use f-string for dynamic route

    def load_accounts():
        """Fetches accounts from DB and updates the ListView."""
        print("Loading accounts for /accounts view...")
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
                edit_handler = functools.partial(go_to_edit_account, acc['account_id'])
                accounts_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(get_icon_by_name(acc["icon"])),
                        # Wrap the title Text in a Container with expand=True
                        title=ft.Container(
                            content=ft.Text(acc["name"]),
                            expand=True # Allow the title to use available horizontal space
                        ),
                        subtitle=ft.Text(
                            f"{acc['description'] if acc['description'] else ''}"
                        ),
                        trailing=ft.Row(
                            [
                                ft.Text(
                                    f"{acc['balance']:.2f} {acc['currency_symbol']}"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT_OUTLINED,
                                    tooltip="Редактировать",
                                    on_click=edit_handler
                                )
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.END
                        )
                    )
                )
        if page.controls:
             page.update()

    def go_to_add_account(e):
        page.go("/accounts/add")

    # --- Initial Load ---
    load_accounts()

    # --- View Layout ---
    return ft.View(
        "/accounts",
        [
            ft.AppBar(
                title=ft.Text("Мои счета"),
                bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
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
        bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
    )
