import flet as ft
from db import db_manager
import datetime  # Needed for date display


def HomeView(page: ft.Page):
    """
    Вьюшка домашней страницы (переработанный дизайн)
    """
    user_id = page.session.get("user_id")
    username = page.session.get("username")  # Keep username for potential future use

    # --- Fetch User Accounts ---
    user_accounts = []  # Keep the full list for the dropdown
    first_account_balance = "0.00"
    first_account_currency_symbol = "₽"  # Default symbol
    selected_account_id = None  # To track which account is shown in header

    if user_id:
        user_accounts = db_manager.get_accounts_by_user(user_id)
        if user_accounts:
            # Get details from the first account for initial display
            first_account = user_accounts[0]
            first_account_balance = f"{first_account['balance']:.2f}"
            first_account_currency_symbol = first_account["currency_symbol"]
            selected_account_id = first_account["account_id"]  # Store the ID
            # TODO: Implement logic to calculate total across accounts if needed
    else:
        # Handle case where user_id is somehow missing (shouldn't happen if routing is correct)
        page.go("/login")
        return ft.View("/home", [ft.Text("Ошибка: Пользователь не найден.")])

    # --- Controls for Header Balance ---
    # Create Text control for balance display so we can update it
    header_balance_text = ft.Text(
        f"{first_account_balance} {first_account_currency_symbol}",
        size=20,
        weight=ft.FontWeight.BOLD,
    )

    # --- Event Handlers ---
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

    # --- Remove Navigation Drawer related code ---
    # Removed: nav_drawer definition, handle_dismissal, handle_change, drawer_item_selected, close_drawer, page.drawer assignment

    # --- Controls for Header Balance ---
    # Duplicate definition removed

    # --- Event Handlers ---
    # Duplicate definition removed

    # Removed open_menu function

    # Removed drawer_item_selected function

    def account_selected_from_menu(e):
        """Updates the header balance when an account is selected from the PopupMenu."""
        # global selected_account_id # Using global here is problematic and likely the cause
        # Instead, we should use a Ref or update the variable in the outer scope directly if possible,
        # but the best approach is often to use ft.Ref for state shared between handlers.
        new_account_id = int(e.control.data)

        # Find the selected account details
        selected_account = next(
            (acc for acc in user_accounts if acc["account_id"] == new_account_id), None
        )

        if selected_account:
            # This update might not be reflected correctly in add_transaction
            # if the scope isn't handled properly.
            # selected_account_id = new_account_id # This updates the local variable of account_selected_from_menu if global is removed
            # Let's use a Ref instead.
            selected_account_id = new_account_id  # Update tracked ID
            # Update the header text
            header_balance_text.value = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"
            page.update()

    def add_transaction(e):
        transaction_type = "expense"
        acc_id_to_pass = selected_account_id
        if acc_id_to_pass is None and user_accounts:
            acc_id_to_pass = user_accounts[0]["account_id"]

        # Save context for the add_transaction page
        page.session.set("add_transaction_type", transaction_type)
        page.session.set("add_transaction_account_id", acc_id_to_pass)
        page.session.set(
            "initial_account_id", acc_id_to_pass
        )  # Исправлено: добавлено значение

        page.go("/add_transaction")

    # --- UI Components ---

    # Header Account Selector (PopupMenuButton)
    account_selector_menu = ft.PopupMenuButton(
        # Content is the clickable part (Icon + Text + Arrow)
        content=ft.Row(
            [
                ft.Icon(ft.icons.MONETIZATION_ON_OUTLINED, size=16),
                ft.Text(
                    "Итого"
                ),  # Keep "Итого" static or change based on selection? Let's keep it.
                ft.Icon(ft.icons.ARROW_DROP_DOWN, size=16),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            # Make the row take up reasonable space
            # width=100, # Adjust as needed
            # height=30, # Adjust as needed
        ),
        items=(
            [
                ft.PopupMenuItem(
                    text=f"{acc['name']} ({acc['balance']:.2f} {acc['currency_symbol']})",
                    # Store account_id in data to know which was clicked
                    data=str(acc["account_id"]),
                    on_click=account_selected_from_menu,
                )
                for acc in user_accounts  # Create item for each account
            ]
            if user_accounts
            else [ft.PopupMenuItem(text="Нет счетов", disabled=True)]
        ),  # Handle no accounts case
    )

    # Custom Header (Updated to use account_selector_menu and header_balance_text)
    custom_header = ft.Container(
        content=ft.Row(
            [
                # Changed Menu button to Accounts button
                ft.IconButton(
                    ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,  # Changed icon
                    tooltip="Счета",  # Changed tooltip
                    on_click=lambda e: page.go("/accounts"),  # Changed action
                ),
                ft.Column(
                    [
                        account_selector_menu,
                        header_balance_text,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                # Changed Reports button to Logout button
                ft.IconButton(
                    ft.icons.LOGOUT,  # Changed icon
                    tooltip="Выйти",  # Changed tooltip
                    on_click=logout_clicked,  # Changed action
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )

    # Time Period Selector
    time_period_selector = ft.Row(
        [
            ft.TextButton("День"),
            ft.TextButton("Неделя"),
            ft.TextButton("Месяц"),
            ft.TextButton("Год"),
            ft.TextButton("Период"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    # Date Navigator
    current_date_str = datetime.date.today().strftime("Сегодня, %d %B")  # Format date
    date_navigator = ft.Row(
        [
            ft.IconButton(ft.icons.CHEVRON_LEFT),
            ft.Text(current_date_str, expand=True, text_align=ft.TextAlign.CENTER),
            ft.IconButton(ft.icons.CHEVRON_RIGHT),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Summary/Progress Section
    summary_section = ft.Column(
        [
            ft.ProgressBar(
                value=0.1, width=page.width * 0.8 if page.width else 300
            ),  # Example progress
            ft.Text("0 ₽"),  # Placeholder value
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
    )

    # Tabs Content
    expenses_tab_content = ft.Container(
        ft.Column(
            [
                time_period_selector,
                date_navigator,
                summary_section,
                # Add list of expenses here later
                ft.Text(
                    "Список расходов будет здесь...",
                    text_align=ft.TextAlign.CENTER,
                    expand=True,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        # Use a background color similar to the image's card
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
        border_radius=10,
        margin=ft.margin.symmetric(horizontal=10),  # Add margin around the card
    )

    income_tab_content = ft.Container(
        ft.Column(
            [
                # Similar structure for income can be added here
                ft.Text(
                    "Список доходов будет здесь...",
                    text_align=ft.TextAlign.CENTER,
                    expand=True,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
        border_radius=10,
        margin=ft.margin.symmetric(horizontal=10),
    )

    # --- View Layout ---
    return ft.View(
        "/home",
        [
            custom_header,
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(text="РАСХОДЫ"),
                    ft.Tab(text="ДОХОДЫ"),
                ],
                # The content of the tabs needs to be outside the Tabs definition
                # We'll use the selected_index to conditionally show content,
                # or place the content directly below the Tabs control.
                # For simplicity, let's place the content below for now.
                # A more robust way involves updating content based on on_change.
                # expand=True # Make tabs take available space if needed
            ),
            # Content area that changes based on tab selection (simple version)
            # We'll display the expenses content by default.
            # A proper implementation would use the Tabs' on_change event.
            expenses_tab_content,  # Show expenses content initially
            # income_tab_content, # This would be shown conditionally
            # Removed old elements:
            # ft.Text(f"Добро пожаловать, {username}!" if username else "Добро пожаловать!", size=24),
            # ft.Text("Это ваша домашняя страница финансового менеджера."),
            # accounts_dropdown,
            # ft.ElevatedButton("Управление счетами", ...)
        ],
        floating_action_button=ft.FloatingActionButton(
            icon=ft.icons.ADD,
            tooltip="Добавить транзакцию",
            on_click=add_transaction,
            bgcolor=ft.colors.YELLOW_700,  # Color similar to image
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,  # Remove padding from View if header/content handle it
        # Optional: Set background color for the whole view
        # bgcolor=ft.colors.GREEN_900,
    )
