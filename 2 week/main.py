import flet as ft
from pages.login_page import LoginView
from pages.registration_page import RegistrationView
from pages.home_page import HomeView

def main(page: ft.Page):
    page.title = "Персональный финансовый менеджер"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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
        print(f"Route changed to: {page.route}")
        page.views.clear()
        if page.route in views:
            if page.route == "/home" and not page.session.contains_key("user_id"):
                print("User not logged in, redirecting to /login")
                page.views.append(views["/login"])
                page.go("/login")
            else:
                page.views.append(views[page.route])
        else:
            print(f"Unknown route '{page.route}', redirecting to /login")
            page.views.append(views["/login"])
            page.go("/login")

        page.update()

    def view_pop(view):
        """
        Возвращает на предыдущую вьюшку
        """
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)