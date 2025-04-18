import flet as ft
from db import db_manager, TransactionType # Import TransactionType
import datetime
from dateutil.relativedelta import relativedelta # For easy date manipulation

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
    period_button = ft.Ref[ft.TextButton]() # For custom period later

    # --- State Variables ---
    # Use page.session or page.client_storage if state needs to persist across views/reloads
    # For view-specific state, local variables are fine if managed carefully.
    # Let's store them locally for now.
    current_state = {
        "selected_account_id": None,
        "selected_account_currency": "₽",
        "current_tab_index": 0, # 0: Expenses, 1: Income
        "current_period_type": "month", # 'day', 'week', 'month', 'year', 'custom'
        "current_date": datetime.date.today(), # The reference date for period calculation
        "current_offset": 0,
    }

    initial_header_balance = "0.00 ₽"
    if current_state["selected_account_id"]:
         selected_account = next((acc for acc in user_accounts if acc["account_id"] == current_state["selected_account_id"]), None)
         if selected_account:
              initial_header_balance = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"

    # --- Fetch User Accounts ---
    user_accounts = []
    if user_id:
        user_accounts = db_manager.get_accounts_by_user(user_id)
        if user_accounts:
            first_account = user_accounts[0]
            current_state["selected_account_id"] = first_account["account_id"]
            current_state["selected_account_currency"] = first_account["currency_symbol"]
            # Initial balance display is set in the control definition below
        # else: # No accounts exist yet, handled by add_transaction check
            # pass
    else:
        page.go("/login")
        return ft.View("/home", [ft.Text("Ошибка: Пользователь не найден.")])

    # --- Helper Functions ---
    def get_date_range(period_type: str, ref_date: datetime.date):
        """Calculates start and end dates based on period type and reference date."""
        start_date = ref_date
        end_date = ref_date
        display_str = ref_date.strftime("%d %B %Y") # Default for day

        if period_type == "day":
            start_date = ref_date
            end_date = ref_date
            display_str = ref_date.strftime("%d %B %Y")
        elif period_type == "week":
            start_date = ref_date - datetime.timedelta(days=ref_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            display_str = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
        elif period_type == "month":
            start_date = ref_date.replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - datetime.timedelta(days=1)
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
            current_state["current_date"] += (delta * direction)
            update_transaction_display()

    # Add the on_tab_change handler
    def on_tab_change(e):
        """Handles tab selection changes."""
        new_index = e.control.selected_index
        current_state["current_tab_index"] = new_index
        print(f"Tab changed to index: {new_index}") # Debug log
        update_transaction_display() # Refresh content for the new tab

    def update_transaction_display():
        """Fetches and displays transactions based on current state."""
        print(f"Updating display. State: {current_state}") # Debug log
        if not current_state["selected_account_id"]:
            print("No account selected, skipping update.")
            # Clear list and summary if needed
            if transactions_list_view.current:
                transactions_list_view.current.controls.clear()
                transactions_list_view.current.controls.append(ft.Text("Выберите счет"))
            if summary_text.current:
                summary_text.current.value = f"0.00 {current_state['selected_account_currency']}"
            if date_navigator_text.current:
                 date_navigator_text.current.value = "Нет данных"
            # Update button styles even if no account selected
            all_period_buttons = {
                "day": day_button, "week": week_button, "month": month_button, "year": year_button, "custom": period_button
            }
            for period, button_ref in all_period_buttons.items():
                if button_ref.current:
                    button_ref.current.style = ft.ButtonStyle(color=ft.colors.WHITE if period == current_state["current_period_type"] else ft.colors.with_opacity(0.5, ft.colors.WHITE))

            page.update()
            return

        # Determine transaction type based on tab
        transaction_type = (
            TransactionType.expense
            if current_state["current_tab_index"] == 0
            else TransactionType.income
        )

        # Calculate date range
        start_date, end_date, display_str = get_date_range(
            current_state["current_period_type"], current_state["current_date"]
        )

        # Update date navigator text
        if date_navigator_text.current:
            date_navigator_text.current.value = display_str

        # Fetch data from DB
        transactions, total_sum = db_manager.get_transactions_summary(
            user_id=user_id,
            account_id=current_state["selected_account_id"],
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Update summary text
        if summary_text.current:
            summary_text.current.value = f"{total_sum:.2f} {current_state['selected_account_currency']}"

        # Update transaction list view
        if transactions_list_view.current:
            transactions_list_view.current.controls.clear()
            if transactions:
                for t in transactions:
                    # Format date nicely for display
                    t_date = datetime.datetime.fromisoformat(t['transaction_date'])
                    date_str = t_date.strftime("%d %b") # e.g., 15 Jul
                    transactions_list_view.current.controls.append(
                        ft.ListTile(
                            # leading=ft.Icon(get_icon_by_name(t.get("category_icon", "Default"))), # Need category icons map
                            leading=ft.Icon(ft.icons.CATEGORY), # Placeholder icon
                            title=ft.Text(t.get("category_name", "N/A")),
                            subtitle=ft.Text(t.get("description", "")),
                            trailing=ft.Column(
                                [
                                    ft.Text(f"{t['amount']:.2f} {current_state['selected_account_currency']}", weight=ft.FontWeight.BOLD),
                                    ft.Text(date_str, size=10)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2
                            )
                            # Add on_click handler for editing/deleting transactions later
                            # on_click=lambda e, tid=t['transaction_id']: edit_transaction(tid)
                        )
                    )
            else:
                transactions_list_view.current.controls.append(
                    ft.Container(
                        ft.Text(f"Нет {transaction_type.value} за этот период."),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )

        # Update progress bar (add logic later if needed)
        # if progress_bar.current: progress_bar.current.value = ...

        # Update button styles
        all_period_buttons = {
            "day": day_button, "week": week_button, "month": month_button, "year": year_button, "custom": period_button
        }
        for period, button_ref in all_period_buttons.items():
            if button_ref.current:
                 button_ref.current.style = ft.ButtonStyle(color=ft.colors.WHITE if period == current_state["current_period_type"] else ft.colors.with_opacity(0.5, ft.colors.WHITE))


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
        # global selected_account_id # Using global here is problematic and likely the cause
        # Instead, we should use a Ref or update the variable in the outer scope directly if possible,
        # but the best approach is often to use ft.Ref for state shared between handlers.
        new_account_id = int(e.control.data)

        # Find the selected account details
        selected_account = next(
            (acc for acc in user_accounts if acc["account_id"] == new_account_id), None
        )

        if selected_account:
            # Update state
            current_state["selected_account_id"] = new_account_id
            current_state["selected_account_currency"] = selected_account["currency_symbol"]

            # Update the header text directly via Ref
            if header_balance_text.current:
                 header_balance_text.current.value = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"

            print(f"Account changed to: {new_account_id}. Triggering display update.") # Debug log
            update_transaction_display() # Refresh transactions for the new account
            # No need for page.update() here, update_transaction_display handles it

    def go_to_add_account(e):
        """Closes the dialog and navigates to the add account page."""
        page.update()
        page.go("/accounts/add")

    def close_dialog(e):
        """Closes the dialog."""
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
                        on_click=go_to_add_account,
                    ),
                    ft.TextButton("Отмена", on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(alert_dialog)
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
                        # Use Ref for balance text
                        ft.Text(
                            ref=header_balance_text,
                            value=initial_header_balance, # Set initial value
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
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
            ft.TextButton("День", ref=day_button, on_click=lambda e: on_period_button_click(e, "day"), data="day"),
            ft.TextButton("Неделя", ref=week_button, on_click=lambda e: on_period_button_click(e, "week"), data="week"),
            ft.TextButton("Месяц", ref=month_button, on_click=lambda e: on_period_button_click(e, "month"), data="month"),
            ft.TextButton("Год", ref=year_button, on_click=lambda e: on_period_button_click(e, "year"), data="year"),
            ft.TextButton("Период", ref=period_button, on_click=lambda e: on_period_button_click(e, "custom"), data="custom", disabled=True), # Disable custom for now
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    # Date Navigator
    # Use the Ref for the text part
    date_navigator = ft.Row(
        [
            ft.IconButton(ft.icons.CHEVRON_LEFT, on_click=lambda e: on_date_nav_click(e, -1), tooltip="Предыдущий период"),
            ft.Text(ref=date_navigator_text, value="Загрузка...", expand=True, text_align=ft.TextAlign.CENTER), # Use Ref
            ft.IconButton(ft.icons.CHEVRON_RIGHT, on_click=lambda e: on_date_nav_click(e, 1), tooltip="Следующий период"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Summary/Progress Section
    # Use the Ref for the summary text
    summary_section = ft.Column(
        [
            # ft.ProgressBar(ref=progress_bar, value=0.1, width=page.width * 0.8 if page.width else 300), # Uncomment if using progress bar
            ft.Text(ref=summary_text, value="0.00 ₽", size=18, weight=ft.FontWeight.BOLD), # Use Ref
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
    )

    # --- Define the main content area that updates ---
    tab_content_area = ft.Column(
        [
            time_period_selector,
            date_navigator,
            summary_section,
            ft.Divider(height=1, color=ft.colors.with_opacity(0.5, ft.colors.WHITE)), # Optional divider
            # The ListView will display transactions based on the selected tab/period
            ft.Container( # Wrap ListView for better control, especially with expand
                content=ft.ListView(ref=transactions_list_view, spacing=5, auto_scroll=False),
                expand=True, # Make the list view fill available vertical space
                # Add padding if needed
                # padding=ft.padding.only(top=10)
            )
        ],
        spacing=10,
        # Make the column itself expand to fill space below the tabs
        expand=True,
        # Add horizontal padding to the whole content area
        # horizontal_alignment=ft.CrossAxisAlignment.STRETCH, # Stretch children horizontally
        # width=page.width - 20 if page.width else None # Adjust width if needed
    )

    # --- Initial data load ---
    # Call this *after* all controls using Refs are defined
    # and *after* initial state is set
    if user_id and current_state["selected_account_id"]:
        # Set initial balance text based on the first/selected account
        selected_account = next((acc for acc in user_accounts if acc["account_id"] == current_state["selected_account_id"]), None)
        if selected_account and header_balance_text.current:
             header_balance_text.current.value = f"{selected_account['balance']:.2f} {selected_account['currency_symbol']}"
        # Load initial transactions
        update_transaction_display()
    elif user_id: # User exists but has no accounts
        update_transaction_display() # Call to display "No accounts" message etc.


    # --- View Layout ---
    return ft.View(
        "/home",
        [
            custom_header,
            ft.Tabs(
                ref=tabs_control, # Add Ref
                selected_index=current_state["current_tab_index"], # Use state
                on_change=on_tab_change, # Connect handler
                animation_duration=300,
                tabs=[
                    ft.Tab(text="РАСХОДЫ"),
                    ft.Tab(text="ДОХОДЫ"),
                ],
                # Add styling for tabs if desired
                # label_color=ft.colors.YELLOW_700,
                # unselected_label_color=ft.colors.with_opacity(0.7, ft.colors.WHITE),
                # indicator_color=ft.colors.YELLOW_700,
            ),
            # Display the content area which updates dynamically
            ft.Container( # Wrap content area for padding/margin
                content=tab_content_area,
                padding=ft.padding.symmetric(horizontal=10), # Add padding around the content
                expand=True # Ensure this container also expands
            )
        ],
        floating_action_button=ft.FloatingActionButton(
            icon=ft.icons.ADD,
            tooltip="Добавить транзакцию",
            on_click=add_transaction,
            bgcolor=ft.colors.YELLOW_700,
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,
        # Removed scroll=ft.ScrollMode.AUTO from View, let ListView handle scrolling
    )
