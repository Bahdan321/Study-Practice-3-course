import flet as ft
from db import db_manager
import datetime # Needed for date display

def HomeView(page: ft.Page):
    """
    Вьюшка домашней страницы (переработанный дизайн)
    """
    user_id = page.session.get("user_id")
    username = page.session.get("username") # Keep username for potential future use

    # --- Fetch User Accounts ---
    first_account_balance = "0.00"
    first_account_currency_symbol = "₽" # Default symbol
    if user_id:
        user_accounts = db_manager.get_accounts_by_user(user_id)
        if user_accounts:
            # Get details from the first account for display
            first_account = user_accounts[0]
            first_account_balance = f"{first_account['balance']:.2f}"
            first_account_currency_symbol = first_account['currency_symbol']
            # TODO: Implement logic to calculate total across accounts or select account
    else:
        # Handle case where user_id is somehow missing (shouldn't happen if routing is correct)
        page.go("/login")
        return ft.View("/home", [ft.Text("Ошибка: Пользователь не найден.")])


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

    def open_menu(e):
        # TODO: Implement drawer or menu functionality
        print("Menu button clicked")
        pass

    def open_reports(e):
        # TODO: Implement navigation to reports page
        print("Reports button clicked")
        pass

    def add_transaction(e):
        # TODO: Implement navigation or dialog for adding transactions
        print("Add transaction button clicked")
        pass

    # --- UI Components ---

    # Custom Header
    custom_header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(ft.icons.MENU, tooltip="Меню", on_click=open_menu),
                ft.Column(
                    [
                        ft.Row( # Row for "Итого" and dropdown arrow
                            [
                                ft.Icon(ft.icons.MONETIZATION_ON_OUTLINED, size=16), # Icon similar to image
                                ft.Text("Итого"),
                                ft.Icon(ft.icons.ARROW_DROP_DOWN, size=16),
                            ],
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Text(
                            f"{first_account_balance} {first_account_currency_symbol}",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0, # Reduce spacing between rows in the column
                ),
                ft.IconButton(ft.icons.RECEIPT_LONG_OUTLINED, tooltip="Отчеты", on_click=open_reports), # Icon similar to image
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        # Optional: Add background color if needed
        # bgcolor=ft.colors.GREEN_700,
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
        alignment=ft.MainAxisAlignment.SPACE_AROUND
    )

    # Date Navigator
    current_date_str = datetime.date.today().strftime("Сегодня, %d %B") # Format date
    date_navigator = ft.Row(
        [
            ft.IconButton(ft.icons.CHEVRON_LEFT),
            ft.Text(current_date_str, expand=True, text_align=ft.TextAlign.CENTER),
            ft.IconButton(ft.icons.CHEVRON_RIGHT),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Summary/Progress Section
    summary_section = ft.Column(
        [
            ft.ProgressBar(value=0.1, width=page.width*0.8 if page.width else 300), # Example progress
            ft.Text("0 ₽"), # Placeholder value
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
                ft.Text("Список расходов будет здесь...", text_align=ft.TextAlign.CENTER, expand=True),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        # Use a background color similar to the image's card
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
        border_radius=10,
        margin=ft.margin.symmetric(horizontal=10) # Add margin around the card
    )

    income_tab_content = ft.Container(
         ft.Column(
            [
                # Similar structure for income can be added here
                ft.Text("Список доходов будет здесь...", text_align=ft.TextAlign.CENTER, expand=True),
            ],
             spacing=15,
             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         ),
        padding=10,
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
        border_radius=10,
        margin=ft.margin.symmetric(horizontal=10)
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
            expenses_tab_content, # Show expenses content initially
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
            bgcolor=ft.colors.YELLOW_700 # Color similar to image
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0, # Remove padding from View if header/content handle it
        # Optional: Set background color for the whole view
        # bgcolor=ft.colors.GREEN_900,
    )