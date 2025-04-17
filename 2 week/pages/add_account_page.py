import flet as ft
from db import db_manager
from icons import get_icon_names

def AddAccountView(page: ft.Page):
    """
    Вьюшка для добавления нового счета.
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/accounts/add", [ft.Text("Не авторизован")])

    currencies = db_manager.get_currencies()
    icon_names = get_icon_names()

    account_name_field = ft.TextField(label="Название счета", autofocus=True, width=350)
    account_balance_field = ft.TextField(
        label="Начальный баланс", keyboard_type=ft.KeyboardType.NUMBER, value="0", width=350
    )
    account_currency_dropdown = ft.Dropdown(
        label="Валюта",
        options=(
            [
                ft.dropdown.Option(
                    key=str(c["currency_id"]), text=f"{c['code']} ({c['symbol']})"
                )
                for c in currencies
            ]
            if currencies
            else []
        ),
        value=str(currencies[0]["currency_id"]) if currencies else None,
        width=350
    )
    account_description_field = ft.TextField(label="Описание (необязательно)", width=350)
    account_icon_dropdown = ft.Dropdown(
        label="Иконка",
        options=[ft.dropdown.Option(key=name, text=name) for name in icon_names],
        value=icon_names[0] if icon_names else None,
        width=350
    )
    add_account_error_text = ft.Text(value="", color=ft.colors.RED, width=350)

    def save_new_account_and_go_back(e):
        """
        Проверяет ввод, сохраняет новый счет и возвращает на предыдущую страницу.
        """
        name = account_name_field.value
        balance_str = account_balance_field.value
        currency_id = account_currency_dropdown.value
        description = account_description_field.value
        icon = account_icon_dropdown.value
        add_account_error_text.value = ""

        if not name:
            add_account_error_text.value = "Название счета не может быть пустым."
            page.update()
            return
        try:
            balance = float(balance_str) if balance_str else 0.0
        except ValueError:
            add_account_error_text.value = "Неверный формат баланса."
            page.update()
            return
        if not currency_id:
            add_account_error_text.value = "Выберите валюту."
            page.update()
            return
        if not icon:
            add_account_error_text.value = "Выберите иконку."
            page.update()
            return

        success = db_manager.add_account(
            user_id=user_id,
            name=name,
            balance=balance,
            currency_id=int(currency_id),
            description=description,
            icon=icon,
        )

        if success:
            print(f"Счет '{name}' успешно добавлен. Возврат на /accounts.")
            page.go("/accounts")
        else:
            add_account_error_text.value = "Ошибка при сохранении счета в базе данных."
            page.update()

    def cancel_and_go_back(e):
        """
        Возвращает на предыдущую страницу без сохранения.
        """
        page.go("/accounts")

    return ft.View(
        "/accounts/add",
        [
            ft.AppBar(title=ft.Text("Добавить новый счет"), actions=[]),
            ft.Column(
                [
                    account_name_field,
                    account_balance_field,
                    account_currency_dropdown,
                    account_icon_dropdown,
                    account_description_field,
                    add_account_error_text,
                    ft.Row(
                        [
                            ft.ElevatedButton("Отмена", on_click=cancel_and_go_back),
                            ft.ElevatedButton("Сохранить", on_click=save_new_account_and_go_back),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.ADAPTIVE
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=10
    )
