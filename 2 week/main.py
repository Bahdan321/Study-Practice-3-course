import flet as ft
from pages.login_page import LoginView
from pages.registration_page import RegistrationView
from pages.home_page import HomeView
from pages.accounts_page import AccountsView
from pages.add_account_page import AddAccountView
from db import db_manager
import time

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

    view_factories = {
        "/login": LoginView,
        "/register": RegistrationView,
        "/home": HomeView,
        "/accounts": AccountsView,
        "/accounts/add": AddAccountView
    }

    def route_change(route):
        """
        Меняет вьюшку в зависимости от роута
        """
        print(f"Route change requested for: {page.route}")

        target_view_factory = view_factories.get(page.route)

        is_logged_in = page.session.contains_key("user_id")
        protected_routes = ["/home", "/accounts", "/accounts/add"]

        page.views.clear()

        if target_view_factory:
            if page.route in protected_routes and not is_logged_in:
                print(f"User not logged in (route_change check for {page.route}), redirecting to /login")
                page.views.append(view_factories["/login"](page))
            else:
                page.views.append(target_view_factory(page))
        else:
            print(f"Unknown route '{page.route}', redirecting...")
            default_route = "/home" if is_logged_in else "/login"
            page.views.append(view_factories[default_route](page))

        page.update()


    def view_pop(view):
        """
        Возвращает на предыдущую вьюшку
        """
        page.views.pop()
        if not page.views:
            print("View stack empty, going to login.")
            page.views.append(view_factories["/login"](page))
            page.go("/login")
        else:
            top_view = page.views[-1]

            page.go(top_view.route)


    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if try_auto_login():
        page.go("/home")
    else:
        page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)