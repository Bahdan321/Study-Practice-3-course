import flet as ft
from pages.login_page import LoginView
from pages.registration_page import RegistrationView
from pages.home_page import HomeView
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

    # Все роуты
    views = {
        "/login": LoginView(page),
        "/register": RegistrationView(page),
        "/home": HomeView(page)
    }

    def route_change(route):
        """
        Меняет вюьюшку в зависимости от роута
        """
        print(f"Route change requested for: {page.route}")
        current_view = views.get(page.route)

        is_logged_in = page.session.contains_key("user_id")

        page.views.clear()
        if current_view:
            if page.route == "/home" and not is_logged_in:
                print("User not logged in (route_change check), redirecting to /login")
                page.views.append(views["/login"])
            else:
                page.views.append(current_view)
        else:
            print(f"Unknown route '{page.route}', showing login page")
            page.views.append(views["/login"])

        page.update()


    def view_pop(view):
        """
        Возвращает на предыдущую вьюшку
        """
        page.views.pop()
        if not page.views:
            page.views.append(views['/login'])
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