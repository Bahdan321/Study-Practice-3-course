import flet as ft
from pages.login_page import LoginView
from pages.registration_page import RegistrationView
from pages.home_page import HomeView
from pages.accounts_page import AccountsView
from pages.add_account_page import AddAccountView
from pages.edit_account_page import EditAccountView # Import the new edit view
from db import db_manager
import time
import re # Import regex for route parsing

def main(page: ft.Page):
    page.title = "Персональный финансовый менеджер"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def try_auto_login():
        """
        Проверяет наличие токена в локальном хранилище и пытается выполнить автоматический вход.
        """
        time.sleep(0.1)
        stored_token = page.client_storage.get("session_token")
        if stored_token:
            print(f"Found stored token: {stored_token[:8]}...")
            user = db_manager.get_user_by_session_token(stored_token)
            if user:
                print(f"Token valid. Logging in user: {user['username']}")
                page.session.set("user_id", user['user_id'])
                page.session.set("username", user['username'])
                page.session.set("session_token", stored_token)
                return True
            else:
                print("Stored token is invalid or expired. Removing.")
                page.client_storage.remove("session_token")
        return False

    # --- Route Definitions ---
    # Use a dictionary for simple routes
    simple_view_factories = {
        "/login": LoginView,
        "/register": RegistrationView,
        "/home": HomeView,
        "/accounts": AccountsView,
        "/accounts/add": AddAccountView
    }
    # Define protected routes
    protected_routes = ["/home", "/accounts", "/accounts/add", "/accounts/edit/"] # Add base edit route

    # --- Route Change Logic ---
    def route_change(route):
        """
        Меняет вьюшку в зависимости от роута, handling parameterized routes.
        """
        print(f"Route change requested for: {page.route}")

        is_logged_in = page.session.contains_key("user_id")
        current_route = page.route

        # Check if user is logged in for protected routes
        is_protected = any(current_route.startswith(pr) for pr in protected_routes)
        if is_protected and not is_logged_in:
            print(f"User not logged in (route_change check for {current_route}), redirecting to /login")
            page.views.clear()
            page.views.append(simple_view_factories["/login"](page))
            page.update()
            return # Stop further processing

        # --- Route Matching ---
        page.views.clear()
        target_view = None

        # 1. Check simple routes first
        if current_route in simple_view_factories:
            target_view = simple_view_factories[current_route](page)

        # 2. Check for edit account route (/accounts/edit/<id>)
        else:
            edit_match = re.match(r"/accounts/edit/(\d+)", current_route)
            if edit_match:
                try:
                    account_id = int(edit_match.group(1))
                    print(f"Matched edit route for account ID: {account_id}")
                    # Pass the extracted account_id to the EditAccountView factory
                    target_view = EditAccountView(page, account_id)
                except (ValueError, IndexError):
                    print(f"Error parsing account ID from route: {current_route}")
                    # Handle error - maybe show a 'not found' view or redirect
                    target_view = ft.View(current_route, [ft.Text("Invalid Account ID")])


        # --- Append View or Handle Unknown Route ---
        if target_view:
            page.views.append(target_view)
        else:
            # Unknown route
            print(f"Unknown route '{current_route}', redirecting...")
            default_route = "/home" if is_logged_in else "/login"
            page.views.append(simple_view_factories[default_route](page))
            # Consider page.go(default_route) if you want a full redirect feel

        page.update()


    # --- View Pop Logic ---
    def view_pop(view):
        """
        Возвращает на предыдущую вьюшку
        """
        page.views.pop()
        if not page.views:
            print("View stack empty, going to login.")
            page.views.append(simple_view_factories["/login"](page))
            page.go("/login")
        else:
            top_view = page.views[-1]
            # Navigate to the route of the view now at the top
            # This handles navigating back from edit/add pages correctly
            page.go(top_view.route)


    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Initial Navigation ---
    if try_auto_login():
        page.go("/home")
    else:
        page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)