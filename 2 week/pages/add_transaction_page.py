import flet as ft
from db import db_manager
import datetime
from icons import get_icon_by_name  # Assuming you have this from accounts page


def AddTransactionView(page: ft.Page):
    """
    Вьюшка для добавления новой транзакции (расход/доход).
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/add_transaction", [ft.Text("Не авторизован")])

    # Retrieve context from session
    initial_type = page.session.get("add_transaction_type") or "expense"
    initial_account_id = page.session.get(
        "initial_account_id"
    )  # Get account ID from session

    if initial_account_id is None:
        # If somehow no account ID was passed, redirect or show error
        print(
            "AddTransactionView: No initial_account_id found in session, redirecting to /home"
        )  # Add logging
        page.go("/home")  # <<< THIS is causing the redirect
        return ft.View("/add_transaction", [ft.Text("Ошибка: Счет не выбран.")])

    # --- Data Fetching ---
    user_accounts = db_manager.get_accounts_by_user(user_id)
    if not user_accounts:
        page.go("/accounts")  # Redirect if no accounts exist
        page.show_snack_bar(ft.SnackBar(ft.Text("Сначала добавьте счет!"), open=True))
        return ft.View("/add_transaction", [ft.Text("Нет доступных счетов.")])

    # Find the initial account details to get currency symbol
    initial_account = next(
        (acc for acc in user_accounts if acc["account_id"] == initial_account_id),
        user_accounts[0],
    )
    initial_currency_symbol = (
        initial_account["currency_symbol"] if initial_account else "???"
    )

    # --- State Management ---
    selected_type = ft.Ref[str]()
    selected_type.current = initial_type

    selected_account_id = ft.Ref[int]()
    selected_account_id.current = initial_account_id

    selected_category_id = ft.Ref[int]()
    selected_date = ft.Ref[datetime.datetime]()
    selected_date.current = datetime.datetime.now()  # or your default

    # --- UI Controls ---
    amount_field = ft.TextField(
        label="Сумма",
        keyboard_type=ft.KeyboardType.NUMBER,
        value="0",
        width=400,
        text_align=ft.TextAlign.RIGHT,
        # suffix_text=initial_currency_symbol, # Update this dynamically
        # on_change=validate_input # Add validation later
    )
    currency_text = ft.Text(
        initial_currency_symbol, size=16, weight=ft.FontWeight.BOLD
    )  # Separate text for currency

    account_dropdown = ft.Dropdown(
        label="Счет",
        value=str(initial_account_id),  # Dropdown value must be string
        options=[
            ft.dropdown.Option(
                key=str(acc["account_id"]),
                text=f"{acc['name']} ({acc['balance']:.2f} {acc['currency_symbol']})",
            )
            for acc in user_accounts
        ],
        # on_change=handle_account_change # Add handler later
    )
    
    category_dropdown = ft.Dropdown(
        label="Категория",
        options=[
        ],
    )

    date_button = ft.ElevatedButton(
        text=selected_date.current.strftime("%d.%m.%Y"),  # Format date
        icon=ft.icons.CALENDAR_MONTH,
        # on_click=lambda e: date_picker.pick_date() # Add date picker later
    )
    date_picker = ft.DatePicker(
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime.now().replace(
            year=datetime.datetime.now().year + 5
        ),
        # on_change=handle_date_change, # Add handler later
        # on_dismiss=lambda e: print("Date picker dismissed"),
        current_date=selected_date.current,
    )
    page.overlay.append(date_picker)  # Add date picker to page overlay

    description_field = ft.TextField(label="Комментарий (необязательно)", max_lines=3)
    add_button = ft.ElevatedButton(text="Добавить", disabled=True)  # Initially disabled
    error_text = ft.Text("", color=ft.colors.RED)

    # --- Event Handlers & Logic ---

    def update_categories(transaction_type: str):
        """Fetches and updates categories based on type."""
        print(f"--- Updating categories ---") # Add print
        print(f"User ID: {user_id}, Transaction Type: {transaction_type}") # Add print
        categories = db_manager.get_categories_by_user_and_type(
            user_id, transaction_type
        )
        print(f"Categories fetched from DB: {categories}") # Add print: See what the DB returned

        category_dropdown.options = (
            [
                ft.dropdown.Option(key=str(cat["category_id"]), text=cat["name"])
                for cat in categories
            ]
            if categories
            else []
        )
        print(f"Dropdown options set to: {category_dropdown.options}") # Add print: Verify options list

        category_dropdown.value = None  # Reset selection
        selected_category_id.current = None
        validate_input()  # Re-validate after category change
        print(f"--- Triggering page update for categories ---") # Add print
        page.update()

    def handle_tab_change(e):
        """Update selected type and categories when tab changes."""
        new_index = e.control.selected_index
        selected_type.current = "expense" if new_index == 0 else "income"
        update_categories(selected_type.current)

    def handle_account_change(e):
        """Update selected account ID and currency symbol."""
        new_account_id = int(e.control.value)
        selected_account_id.current = new_account_id
        # Find the new currency symbol
        account = next(
            (acc for acc in user_accounts if acc["account_id"] == new_account_id), None
        )
        if account:
            currency_text.value = account["currency_symbol"]
        validate_input()  # Re-validate
        page.update()

    def handle_date_change(e):
        """Update selected date state and button text."""
        if e.control.value:
            selected_date.current = e.control.value  # Store the datetime object
            date_button.text = selected_date.current.strftime("%d.%m.%Y")
            validate_input()  # Re-validate
            page.update()

    def validate_input(*args):
        """Enable/disable add button based on required fields."""
        try:
            amount_val = float(amount_field.value) if amount_field.value else 0.0
        except ValueError:
            amount_val = 0.0  # Treat invalid input as 0 for validation

        is_valid = (
            amount_val > 0
            and account_dropdown.value is not None
            and category_dropdown.value is not None
            and selected_date.current is not None
        )
        add_button.disabled = not is_valid
        # Clear previous error if now valid
        if is_valid and error_text.value:
            error_text.value = ""

        page.update()

    def save_transaction(e):
        """Gathers data, calls DB function, and navigates back."""
        error_text.value = ""  # Clear previous errors
        # --- Validation (double check before saving) ---
        try:
            amount = float(amount_field.value)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
        except ValueError as ve:
            error_text.value = f"Неверная сумма: {ve}"
            page.update()
            return

        account_id_str = account_dropdown.value
        category_id_str = category_dropdown.value
        trans_date = selected_date.current
        trans_type = selected_type.current
        description = description_field.value

        if not account_id_str:
            error_text.value = "Выберите счет."
            page.update()
            return
        if not category_id_str:
            error_text.value = "Выберите категорию."
            page.update()
            return
        if not trans_date:
            error_text.value = "Выберите дату."  # Should not happen with default
            page.update()
            return
        # --- End Validation ---

        # Format date for DB (ISO 8601 recommended for SQLite TEXT)
        date_str = trans_date.strftime("%Y-%m-%d %H:%M:%S")

        # Call DB function
        success, message = db_manager.add_transaction(
            account_id=int(account_id_str),
            category_id=int(category_id_str),
            amount=amount,
            transaction_date=date_str,
            description=description,
            transaction_type=trans_type,
        )

        if success:
            page.go("/home")  # Go back to home page on success
            # Correct the method name here
            page.show_snack_bar(
                ft.SnackBar(ft.Text("Транзакция добавлена!"), open=True)
            )
        else:
            error_text.value = f"Ошибка сохранения: {message}"
            page.update()

    # --- Assign handlers ---
    amount_field.on_change = validate_input
    account_dropdown.on_change = handle_account_change
    category_dropdown.on_change = validate_input  # Just validate when category changes
    date_picker.on_change = handle_date_change
    add_button.on_click = save_transaction

    # --- Initial Setup ---
    update_categories(selected_type.current)  # Load initial categories

    # --- Page Layout ---
    return ft.View(
        "/add_transaction",
        [
            ft.AppBar(
                title=ft.Text("Добавление операции"),
                leading=ft.IconButton(
                    ft.icons.ARROW_BACK, on_click=lambda _: page.go("/home")
                ),
                bgcolor=ft.colors.with_opacity(
                    0.1, ft.colors.with_opacity(0.5, ft.colors.WHITE)
                ),  # Match theme if needed
            ),
            ft.Tabs(
                selected_index=0 if initial_type == "expense" else 1,
                on_change=handle_tab_change,
                tabs=[
                    ft.Tab(text="РАСХОДЫ"),
                    ft.Tab(text="ДОХОДЫ"),
                ],
            ),
            ft.Container(  # Add padding around the form
                padding=ft.padding.all(15),
                content=ft.Column(
                    [
                        ft.Row(  # Amount and Currency
                            [
                                amount_field,
                                currency_text,
                                # ft.IconButton(ft.icons.CALCULATE_OUTLINED) # Optional calculator
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        account_dropdown,
                        category_dropdown,
                        date_button,
                        description_field,
                        # Add Tags, Photo later if needed
                        ft.Divider(height=10, color=ft.colors.with_opacity(0.5, ft.colors.WHITE)),
                        error_text,
                        ft.Row(  # Center the add button
                            [add_button], alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE,  # Allow scrolling on small screens
                ),
            ),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,  # View level scroll
        # bgcolor=ft.colors.GREEN_900 # Match theme if needed
    )
