import flet as ft
from db import db_manager, TransactionType  # Import TransactionType
import datetime
from dateutil.relativedelta import relativedelta  # For easy date manipulation


def HomeView(page: ft.Page):
    """
    Вьюшка домашней страницы (переработанный дизайн)
    """
    user_id = page.session.get("user_id")
    username = page.session.get("username")

    # --- Refs for UI elements that need updating ---
    header_balance_text = ft.Ref[ft.Text]()
    transactions_list_view = ft.Ref[ft.ListView]()
    summary_text = ft.Ref[ft.Text]()
    # progress_bar = ft.Ref[ft.ProgressBar]() # Add if you implement progress logic
    date_navigator_text = ft.Ref[ft.Text]()
    tabs_control = ft.Ref[ft.Tabs]()
    # Add refs for period buttons if you want to visually indicate selection
    day_button = ft.Ref[ft.TextButton]()
    week_button = ft.Ref[ft.TextButton]()
    month_button = ft.Ref[ft.TextButton]()
    year_button = ft.Ref[ft.TextButton]()
    period_button = ft.Ref[ft.TextButton]()  # For custom period later

    # --- State Variables ---
    # Use page.session or page.client_storage if state needs to persist across views/reloads
    # For view-specific state, local variables are fine if managed carefully.
    # Let's store them locally for now.
    current_state = {
        "selected_account_id": None,
        "selected_account_currency": "₽",
        "current_tab_index": 0,  # 0: Expenses, 1: Income
        "current_period_type": "day",  # 'day', 'week', 'month', 'year'
        "current_date": datetime.date.today(),  # The reference date for period calculation
        "current_offset": 0,
    }

    # --- Fetch User Accounts and Set Initial/Persisted State ---
    user_accounts = []
    initial_header_balance = "0.00 ₽" # Default if no accounts
    selected_account_id_from_session = page.session.get("selected_account_id")
    found_account_from_session = False

    if user_id:
        user_accounts = db_manager.get_accounts_by_user(user_id)
        if user_accounts:
            selected_account = None
            # Try to find the account stored in the session
            if selected_account_id_from_session:
                selected_account = next(
                    (acc for acc in user_accounts if acc["account_id"] == selected_account_id_from_session), None
                )

            if selected_account:
                # Found a valid account from session
                current_state["selected_account_id"] = selected_account["account_id"]
                current_state["selected_account_currency"] = selected_account["currency_symbol"]
                initial_header_balance = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"
                found_account_from_session = True
                print(f"Restored selected account from session: {selected_account['account_id']}") # Debug log
            else:
                # Account from session not found or no session value, use the first account as default
                if selected_account_id_from_session:
                    page.session.remove("selected_account_id") # Clear invalid session ID
                    print(f"Cleared invalid account ID {selected_account_id_from_session} from session.") # Debug log

                first_account = user_accounts[0]
                current_state["selected_account_id"] = first_account["account_id"]
                current_state["selected_account_currency"] = first_account["currency_symbol"]
                initial_header_balance = f"{first_account['balance']:.2f} {first_account['currency_symbol']}"
                # Store the default selected account ID in the session
                page.session.set("selected_account_id", first_account["account_id"])
                print(f"Set default account and stored in session: {first_account['account_id']}") # Debug log

        else: # User has no accounts
             current_state["selected_account_id"] = None
             current_state["selected_account_currency"] = "₽" # Or get default from config
             initial_header_balance = "0.00 ₽"
             if selected_account_id_from_session:
                 page.session.remove("selected_account_id") # Clear session if no accounts exist

    else: # No user_id
        page.go("/login")
        # Return a valid View object even on redirect
        return ft.View("/home", [ft.Text("Перенаправление на страницу входа...")])

    # --- Helper Functions ---
    def get_date_range(period_type: str, ref_date: datetime.date):
        """Calculates start and end dates based on period type and reference date."""
        start_date = ref_date
        end_date = ref_date
        display_str = ref_date.strftime("%d %B %Y")  # Default for day

        if period_type == "day":
            start_date = ref_date
            end_date = ref_date
            display_str = ref_date.strftime("%d %B %Y")
        elif period_type == "week":
            start_date = ref_date - datetime.timedelta(days=ref_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            display_str = (
                f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
            )
        elif period_type == "month":
            start_date = ref_date.replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - datetime.timedelta(
                days=1
            )
            display_str = ref_date.strftime("%B %Y")
        elif period_type == "year":
            start_date = ref_date.replace(month=1, day=1)
            end_date = ref_date.replace(month=12, day=31)
            display_str = ref_date.strftime("%Y")
        # Add 'custom' handling later if needed

        return start_date, end_date, display_str

    def on_period_button_click(e, period: str):
        """Handles clicks on Day, Week, Month, Year buttons."""
        current_state["current_period_type"] = period
        # Reset date to today when changing period type for simplicity,
        # or implement more complex logic to keep the relative period.
        current_state["current_date"] = datetime.date.today()
        update_transaction_display()

    def on_date_nav_click(e, direction: int):
        """Handles clicks on the date navigation arrows."""
        delta = None
        period = current_state["current_period_type"]
        if period == "day":
            delta = datetime.timedelta(days=1)
        elif period == "week":
            delta = datetime.timedelta(weeks=1)
        elif period == "month":
            delta = relativedelta(months=1)
        elif period == "year":
            delta = relativedelta(years=1)

        if delta:
            # Ensure current_date is a date object before adding delta
            if isinstance(current_state["current_date"], datetime.datetime):
                current_state["current_date"] = current_state["current_date"].date()
            current_state["current_date"] += delta * direction
            update_transaction_display()

    # Add the on_tab_change handler
    def on_tab_change(e):
        """Handles tab selection changes."""
        new_index = e.control.selected_index
        current_state["current_tab_index"] = new_index
        print(f"Tab changed to index: {new_index}")  # Debug log
        update_transaction_display()  # Refresh content for the new tab

    # --- Date Picker Logic ---
    def handle_date_picked(e):
        """Updates the current_date state when a date is picked from the calendar."""
        if date_picker.value:
            # Convert datetime from picker to date
            selected_date = date_picker.value.date()
            print(f"Date picked: {selected_date}")
            current_state["current_date"] = selected_date
            update_transaction_display()
        # No need to close manually, DatePicker closes on selection

    def open_date_picker(e):
        """Opens the date picker, setting its initial value."""
        # Ensure current_date is a date object
        current_ref_date = current_state["current_date"]
        if isinstance(current_ref_date, datetime.datetime):
            current_ref_date = current_ref_date.date()

        # Convert date to datetime for the picker
        date_picker.value = datetime.datetime.combine(
            current_ref_date, datetime.time.min
        )
        date_picker.update()  # Ensure value is set before picking
        page.open(date_picker)  # Use page.open for DatePicker
        # date_picker.pick_date() # pick_date is for the old dialog-based picker

    # --- Date Picker Control ---
    date_picker = ft.DatePicker(
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime.now().replace(
            year=datetime.datetime.now().year + 5
        ),
        on_change=handle_date_picked,
        # current_date is set dynamically before opening
        help_text="Выберите дату",
        cancel_text="Отмена",
        confirm_text="Выбрать",
    )
    # Add the DatePicker to the page's overlay collection
    page.overlay.append(date_picker)
    # --- End Date Picker Logic ---

    def update_transaction_display():
        """Fetches and displays transactions based on current state."""
        print(f"Updating display. State: {current_state}")  # Debug log
        if not current_state["selected_account_id"]:
            print("No account selected, skipping update.")
            # Clear list and summary if needed
            if transactions_list_view.current:
                transactions_list_view.current.controls.clear()
                transactions_list_view.current.controls.append(ft.Text("Выберите счет"))
            if summary_text.current:
                summary_text.current.value = (
                    f"0.00 {current_state['selected_account_currency']}"
                )
            if date_navigator_text.current:
                date_navigator_text.current.value = "Нет данных"
            # Update button styles even if no account selected
            all_period_buttons = {
                "day": day_button,
                "week": week_button,
                "month": month_button,
                "year": year_button,
                "custom": period_button,
            }
            for period, button_ref in all_period_buttons.items():
                if button_ref.current:
                    button_ref.current.style = ft.ButtonStyle(
                        color=(
                            ft.colors.WHITE
                            if period == current_state["current_period_type"]
                            else ft.colors.with_opacity(0.5, ft.colors.WHITE)
                        )
                    )

            page.update()
            return

        # Determine transaction type based on tab
        transaction_type = (
            TransactionType.expense
            if current_state["current_tab_index"] == 0
            else TransactionType.income
        )

        # Ensure current_date is a date object
        ref_date = current_state["current_date"]
        if isinstance(ref_date, datetime.datetime):
            ref_date = ref_date.date()
            current_state["current_date"] = ref_date  # Update state if needed

        # Calculate date range
        start_date, end_date, display_str = get_date_range(
            current_state["current_period_type"], ref_date
        )

        # Update date navigator text
        if date_navigator_text.current:
            date_navigator_text.current.value = display_str

        # Fetch data from DB
        # Assuming get_transactions_summary returns a tuple (list_of_transactions, total_sum)
        transactions, total_sum = db_manager.get_transactions_summary(
            user_id=user_id,
            account_id=current_state["selected_account_id"],
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Update summary text
        if summary_text.current:
            summary_text.current.value = (
                f"{total_sum:.2f} {current_state['selected_account_currency']}"
            )

        # Update transaction list view
        if transactions_list_view.current:
            transactions_list_view.current.controls.clear()
            if transactions:
                for t in transactions:
                    # Format date nicely for display
                    t_date = datetime.datetime.fromisoformat(t["transaction_date"])
                    date_str = t_date.strftime("%d %b")  # e.g., 15 Jul
                    transactions_list_view.current.controls.append(
                        ft.ListTile(
                            # leading=ft.Icon(get_icon_by_name(t.get("category_icon", "Default"))), # Need category icons map
                            leading=ft.Icon(ft.icons.CATEGORY),  # Placeholder icon
                            title=ft.Text(t.get("category_name", "N/A")),
                            subtitle=ft.Text(t.get("description", "")),
                            trailing=ft.Column(
                                [
                                    ft.Text(
                                        f"{t['amount']:.2f} {current_state['selected_account_currency']}",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(date_str, size=10),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2,
                            ),
                            # Add on_click handler for editing/deleting transactions later
                            # on_click=lambda e, tid=t['transaction_id']: edit_transaction(tid)
                        )
                    )
            else:
                transactions_list_view.current.controls.append(
                    ft.Container(
                        ft.Text(f"Нет {transaction_type.value} за этот период."),
                        alignment=ft.alignment.center,
                        padding=20,
                    )
                )

        # Update progress bar (add logic later if needed)
        # if progress_bar.current: progress_bar.current.value = ...

        # Update button styles
        all_period_buttons = {
            "day": day_button,
            "week": week_button,
            "month": month_button,
            "year": year_button,
            "custom": period_button,
        }
        for period, button_ref in all_period_buttons.items():
            if button_ref.current:
                button_ref.current.style = ft.ButtonStyle(
                    color=(
                        ft.colors.WHITE
                        if period == current_state["current_period_type"]
                        else ft.colors.with_opacity(0.5, ft.colors.WHITE)
                    )
                )

        page.update()

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
        new_account_id = int(e.control.data)

        # Find the selected account details
        selected_account = next(
            (acc for acc in user_accounts if acc["account_id"] == new_account_id), None
        )

        if selected_account:
            # Update state
            current_state["selected_account_id"] = new_account_id
            current_state["selected_account_currency"] = selected_account[
                "currency_symbol"
            ]
            # --- Store selected account ID in session ---
            page.session.set("selected_account_id", new_account_id)
            # --- End Store selected account ID in session ---

            # Update the header text directly via Ref
            if header_balance_text.current:
                header_balance_text.current.value = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"

            print(
                f"Account changed to: {new_account_id}. Stored in session. Triggering display update."
            )  # Debug log
            update_transaction_display()  # Refresh transactions for the new account

    def go_to_add_account(e):
        """Closes the dialog and navigates to the add account page."""
        # Close the dialog first if it's open
        if page.dialog and page.dialog.open:
            page.dialog.open = False
            page.update()  # Update to close dialog before navigating
        page.go("/accounts/add")

    def close_dialog(e):
        """Closes the dialog."""
        if page.dialog:  # Check if dialog exists
            page.dialog.open = False
            page.update()

    def add_transaction(e):
        # Check if the user has any accounts FIRST
        if not user_accounts:
            print("Нет счетов")
            # If no accounts, show an alert dialog
            alert_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Нет счетов"),
                content=ft.Text("Сначала добавьте счет, чтобы создать транзакцию."),
                actions=[
                    ft.ElevatedButton(
                        "Добавить счет",
                        on_click=go_to_add_account,  # Use the updated handler
                    ),
                    ft.TextButton("Отмена", on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = alert_dialog  # Assign to page.dialog
            page.dialog.open = True
            page.update()
            return  # Stop further execution

        # --- If accounts exist, proceed as before ---
        transaction_type = "expense"  # Default to expense for the main button
        acc_id_to_pass = current_state["selected_account_id"]
        # This check might be redundant now if selected_account_id is always set when user_accounts exist
        # but kept for safety.
        if acc_id_to_pass is None and user_accounts:
            acc_id_to_pass = user_accounts[0]["account_id"]

        # Save context for the add_transaction page
        page.session.set("add_transaction_type", transaction_type)
        # Ensure we pass a valid account ID
        page.session.set("add_transaction_account_id", acc_id_to_pass)
        # Set initial_account_id as well, seems required by add_transaction_page
        page.session.set("initial_account_id", acc_id_to_pass)

        print(
            f"Navigating to /add_transaction with account_id: {acc_id_to_pass}"
        )  # Debug log
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
            # wrap=False, # Prevent wrapping
        ),
        items=(
            [
                ft.PopupMenuItem(
                    data=acc["account_id"],  # Use data to pass the ID
                    text=f"{acc['name']} ({acc['balance']:.2f} {acc['currency_symbol']})",
                    on_click=account_selected_from_menu,
                )
                for acc in user_accounts
            ]
            if user_accounts
            else [ft.PopupMenuItem(text="Нет счетов", disabled=True)]
        ),
        tooltip="Выбрать счет",
    )

    # Header Balance Display
    header_balance_display = ft.Row(
        [
            account_selector_menu,
            ft.Text(
                ref=header_balance_text,
                value=initial_header_balance,  # Use the correctly initialized value
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Period Buttons
    period_buttons_row = ft.Row(
        [
            ft.TextButton(
                ref=day_button,
                text="День",
                on_click=lambda e: on_period_button_click(e, "day"),
                style=ft.ButtonStyle(
                    color=ft.colors.with_opacity(0.5, ft.colors.WHITE)
                ),  # Initial style
            ),
            ft.TextButton(
                ref=week_button,
                text="Неделя",
                on_click=lambda e: on_period_button_click(e, "week"),
                style=ft.ButtonStyle(
                    color=ft.colors.with_opacity(0.5, ft.colors.WHITE)
                ),  # Initial style
            ),
            ft.TextButton(
                ref=month_button,
                text="Месяц",
                on_click=lambda e: on_period_button_click(e, "month"),
                style=ft.ButtonStyle(color=ft.colors.WHITE),  # Default selected
            ),
            ft.TextButton(
                ref=year_button,
                text="Год",
                on_click=lambda e: on_period_button_click(e, "year"),
                style=ft.ButtonStyle(
                    color=ft.colors.with_opacity(0.5, ft.colors.WHITE)
                ),  # Initial style
            ),
            # ft.TextButton(ref=period_button, text="Период", on_click=lambda e: on_period_button_click(e, "custom")), # Add later
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )

    # Date Navigator
    date_navigator_row = ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.ARROW_LEFT,
                on_click=lambda e: on_date_nav_click(e, -1),
                tooltip="Предыдущий период",
                icon_color=ft.colors.WHITE,
            ),
            # Wrap the Text in a Container to make it clickable
            ft.Container(
                content=ft.Text(
                    ref=date_navigator_text,
                    value="Загрузка...",  # Initial text
                    weight=ft.FontWeight.BOLD,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                ),
                on_click=open_date_picker,  # Open calendar on click
                tooltip="Выбрать дату",
                expand=True,  # Allow text to take available space
                alignment=ft.alignment.center,
                ink=True,  # Add ripple effect on click
            ),
            ft.IconButton(
                icon=ft.icons.ARROW_RIGHT,
                on_click=lambda e: on_date_nav_click(e, 1),
                tooltip="Следующий период",
                icon_color=ft.colors.WHITE,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Summary Text (Total Expenses/Income for period)
    summary_display = ft.Text(
        ref=summary_text,
        value="0.00 ₽",  # Initial value
        size=24,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    # Tabs for Expenses/Income
    tabs = ft.Tabs(
        ref=tabs_control,
        selected_index=current_state["current_tab_index"],
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="Расходы"),
            ft.Tab(text="Доходы"),
        ],
        expand=True,
    )

    # Transaction List
    transaction_list = ft.ListView(
        ref=transactions_list_view,
        expand=True,
        spacing=5,
        padding=10,
        auto_scroll=True,
        controls=[ft.Text("Загрузка транзакций...")],  # Initial placeholder
    )

    # --- Initial Data Load ---
    # Call update_transaction_display once after the UI is built
    # to populate the initial data based on default state.
    # We need to ensure the refs are available, so we might call it
    # slightly later or handle the initial state differently.
    # Let's call it explicitly after defining the view structure.

    # --- View Structure ---
    view = ft.View(
        "/home",
        [
            ft.AppBar(
                title=ft.Text(f"Привет, {username}!"),
                center_title=True,
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE10),
                actions=[
                    ft.IconButton(
                        icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                        tooltip="Мои счета",
                        on_click=lambda _: page.go("/accounts"),
                    ),
                    ft.IconButton(
                        icon=ft.icons.LOGOUT,
                        tooltip="Выход",
                        on_click=logout_clicked,
                    ),
                ],
            ),
            # Main content area
            ft.Container(
                # Use a gradient or solid color background
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900],
                ),
                padding=ft.padding.only(top=10, bottom=0, left=15, right=15),
                expand=True,  # Make container fill available space
                content=ft.Column(
                    [
                        # Balance and Account Selector
                        header_balance_display,
                        ft.Divider(
                            height=10,
                            color=ft.colors.with_opacity(0.5, ft.colors.WHITE24),
                        ),
                        # Period Buttons
                        period_buttons_row,
                        # Date Navigator
                        date_navigator_row,
                        ft.Divider(
                            height=10,
                            color=ft.colors.with_opacity(0.5, ft.colors.WHITE24),
                        ),
                        # Summary (Total for period)
                        summary_display,
                        # Tabs Container
                        ft.Container(
                            tabs, # The ft.Tabs control is already defined with expand=True
                            border_radius=ft.border_radius.all(5),
                            padding=ft.padding.only(top=5),
                            # --- Add expand=True to make the container fill horizontal space ---
                            expand=True,
                            # --- End Add expand=True ---
                        ),
                    ],
                    spacing=10,  # Spacing between header elements
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            # Transaction List Area (takes remaining space)
            ft.Container(
                transaction_list,
                expand=True,  # Allow list to fill space below header
                padding=ft.padding.only(
                    bottom=70
                ),  # Add padding below list to avoid FAB overlap
            ),
        ],
        # Floating Action Button for adding transactions
        floating_action_button=ft.FloatingActionButton(
            icon=ft.icons.ADD,
            tooltip="Добавить транзакцию",
            on_click=add_transaction,
            bgcolor=ft.colors.BLUE_ACCENT_700,
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_FLOAT,
        padding=0,  # Remove padding from View itself
        bgcolor=ft.colors.BLUE_GREY_900,  # Background for the whole view area
    )

    # --- Trigger Initial Update ---
    # Ensure the page is ready before updating
    def initial_load(e=None):
        print("Performing initial transaction display update...")
        update_transaction_display()

    # Schedule the initial load slightly after the view is potentially rendered
    # Using page.run_task or similar might be more robust if available,
    # but a simple call here often works for initial setup.
    # Alternatively, Flet might have a specific lifecycle hook for this.
    # For now, let's call it directly. Consider page.on_load if issues arise.
    initial_load()

    return view


# Ensure db_manager.get_transactions_summary exists and returns (list, float)
# Example stub if needed:
# class MockDbManager:
#     def get_transactions_summary(self, user_id, account_id, transaction_type, start_date, end_date):
#         print(f"DB Query: Get {transaction_type.value} for account {account_id} from {start_date} to {end_date}")
#         # Simulate data
#         if transaction_type == Transaction
