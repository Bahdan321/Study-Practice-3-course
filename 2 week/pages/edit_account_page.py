import flet as ft
from db import db_manager
from icons import get_icon_names

# Note: This view now needs the account_id passed to it.
# The routing in main.py will handle extracting this.
def EditAccountView(page: ft.Page, account_id: int):
    """
    Вьюшка для редактирования существующего счета.
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View(f"/accounts/edit/{account_id}", [ft.Text("Не авторизован")])

    # --- Fetch existing account data ---
    account_data = db_manager.get_account_by_id(account_id, user_id)
    if not account_data:
        # Handle case where account doesn't exist or doesn't belong to user
        return ft.View(
            f"/accounts/edit/{account_id}",
            [
                ft.AppBar(title=ft.Text("Ошибка")),
                ft.Text(f"Счет с ID {account_id} не найден или не принадлежит вам."),
                ft.ElevatedButton("Назад к счетам", on_click=lambda _: page.go("/accounts"))
            ],
             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
             vertical_alignment=ft.MainAxisAlignment.CENTER
        )

    # --- Fetch necessary data for dropdowns ---
    currencies = db_manager.get_currencies()
    icon_names = get_icon_names()

    # --- Controls for Edit Account Form (pre-filled) ---
    account_name_field = ft.TextField(
        label="Название счета",
        value=account_data['name'], # Pre-fill
        autofocus=True,
        width=350
    )
    account_balance_field = ft.TextField(
        label="Баланс",
        value=str(account_data['balance']), # Pre-fill (convert to string)
        keyboard_type=ft.KeyboardType.NUMBER,
        width=350
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
        value=str(account_data['currency_id']), # Pre-fill (convert to string)
        width=350
    )
    account_description_field = ft.TextField(
        label="Описание (необязательно)",
        value=account_data['description'] or "", # Pre-fill (handle None)
        width=350
    )
    account_icon_dropdown = ft.Dropdown(
        label="Иконка",
        options=[ft.dropdown.Option(key=name, text=name) for name in icon_names],
        value=account_data['icon'], # Pre-fill
        width=350
    )
    edit_account_error_text = ft.Text(value="", color=ft.colors.RED, width=350)

    # --- Functions ---
    def save_updated_account(e):
        """Validates input, saves the updated account, and navigates back."""
        name = account_name_field.value
        balance_str = account_balance_field.value
        currency_id = account_currency_dropdown.value
        description = account_description_field.value
        icon = account_icon_dropdown.value
        edit_account_error_text.value = ""

        # --- Validation ---
        if not name:
            edit_account_error_text.value = "Название счета не может быть пустым."
            page.update()
            return
        try:
            balance = float(balance_str) if balance_str else 0.0
        except ValueError:
            edit_account_error_text.value = "Неверный формат баланса."
            page.update()
            return
        if not currency_id:
            edit_account_error_text.value = "Выберите валюту."
            page.update()
            return
        if not icon:
            edit_account_error_text.value = "Выберите иконку."
            page.update()
            return
        # --- End Validation ---

        # Call DB update function
        success = db_manager.update_account(
            account_id=account_id, # Use the account_id passed to the view
            user_id=user_id,
            name=name,
            balance=balance,
            currency_id=int(currency_id),
            description=description,
            icon=icon,
        )

        if success:
            print(f"Account ID {account_id} updated. Navigating back to /accounts.")
            page.go("/accounts")
        else:
            edit_account_error_text.value = "Ошибка при обновлении счета в базе данных."
            page.update()

    def cancel_and_go_back(e):
        """Navigates back to the accounts list page without saving."""
        page.go("/accounts")

    def close_dialog(e):
        """Closes the currently open dialog."""
        page.go("/accounts")

    def execute_delete_account(e):
        """Performs the actual deletion after confirmation."""
        close_dialog(e) # Close the confirmation dialog
        print(f"Attempting to delete account ID: {account_id}")
        success, message = db_manager.delete_account(account_id, user_id)
        if success:
            print(f"Account {account_id} deleted successfully.")
            page.go("/accounts") # Navigate back after successful deletion
        else:
            print(f"Error deleting account {account_id}: {message}")
            edit_account_error_text.value = f"Ошибка удаления: {message}"
            page.update()

    def confirm_delete_account(e):
        """Opens a confirmation dialog before deleting the account."""
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтвердите удаление"),
            content=ft.Text(f"Вы уверены, что хотите удалить счет '{account_data['name']}'?\nВсе связанные транзакции также будут удалены."),
            actions=[
                ft.TextButton("Отмена", on_click=close_dialog),
                ft.TextButton("Удалить", on_click=execute_delete_account, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(confirm_dialog)
        page.update()


    # --- View Layout ---
    return ft.View(
        # Route includes the specific account ID
        f"/accounts/edit/{account_id}",
        [
            ft.AppBar(
                title=ft.Text(f"Редактировать: {account_data['name']}"),
                bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
                ),
            ft.Column(
                [
                    account_name_field,
                    account_balance_field,
                    account_currency_dropdown,
                    account_icon_dropdown,
                    account_description_field,
                    edit_account_error_text,
                    ft.Row(
                        [
                            # Add Delete Button
                            ft.ElevatedButton(
                                "Удалить",
                                on_click=confirm_delete_account,
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.RED_700, # Make delete button stand out
                            ),
                            # Existing Buttons
                            ft.ElevatedButton("Отмена", on_click=cancel_and_go_back),
                            ft.ElevatedButton("Сохранить", on_click=save_updated_account),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        # Adjust spacing or width if needed
                        width=350 # Match width of fields for alignment
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
        padding=10,
        bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
    )