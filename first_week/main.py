import flet as ft

anime_list = [
        {
            "title": "Киберпанк: Бегущие по краю",
            "poster": "https://kinopoisk-ru.clstorage.net/",
            "release_date": "13 сентября 2022 года",
            "description": "Действия аниме-сериала происходят в будущем, в вольном мегаполисе Найт-Сити, расположенном на западе Северной Америки. Город страдает от повсеместной коррупции, многие люди одержимы высокими технологиями и разного рода кибернетическими имплантатами. Помимо этого, в нём также большие проблемы с преступностью, дискриминацией по разным признакам и безопасностью населения.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Как и ожидалось, моя школьная романтическая жизнь не удалась",
            "poster": "https://kinopoisk-ru.clstorage.net/",
            "release_date": "5 апреля 2013",
            "description": "Старшеклассник Хатиман Хикигая — интроверт, циник и пессимист. Он уверен, что дружба, любовь и прочие социальные отношения — полная чушь. После написанного Хатиманом уничижительного эссе, его в качестве наказания отправляют прямиком в клуб волонтёров, где ему придётся вместе с красавицей школы Юкино Юкиноситой решать проблемы других людей.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Моб Психо 100",
            "poster": "https://kinopoisk-ru.clstorage.net/",
            "release_date": "11 июля 2016",
            "description": "Шигэо Кагэяма вроде бы обычный японский школьник — стеснительный, старающийся не привлекать внимания, не блещущий умом, красотой или чувством юмора. И самое большое его желание — привлечь внимание любимой девушки. Но! У этого восьмиклассника есть экстрасенсорные способности. С детства он взглядом гнет ложки и передвигает предметы. И пусть общественность пока этого не оценила, зато выгоду в этом очень скоро нашел его «ментальный наставник», эксплуатирующий способности Кагэямы себе на поживу.Как будет искать свой путь в этом привычно жестоком мире юный экстрасенс — нам и предстоит увидеть.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Невероятные приключения ДжоДжо",
            "poster": "https://kinopoisk-ru.clstorage.net/",
            "release_date": "4 октября 2012",
            "description": "История девяти частей манги разворачивается вокруг приключений Джонатана Джостара и его потомков: каждая часть представляет читателю отдельную историю и нового героя, способного применять в бою сверхъестественные способности.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Опасность в моём сердце",
            "poster": "https://kinopoisk-ru.clstorage.net/",
            "release_date": "9 ноября 2022",
            "description": "У тихого и замкнутого школьника Кётаро Итикавы весьма богатое воображение, ведь он постоянно представляет, как убивает одноклассников различными способами, и особенно часто — самую красивую девочку класса Анну Ямаду. Однажды он случайно сталкивается с Анной в библиотеке, и с удивлением отмечает, что она очень милая и забавная. Постепенно Кётаро начинает испытывать к девушке новые для себя чувства.",
            "opinion": "ABSOLUTE CINEMA",
        },
    ]


def main(page: ft.Page):
    page.bgcolor = ft.colors.TRANSPARENT
    page.bg_gradient = ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[ft.Colors.BLUE_GREY_900, ft.Colors.WHITE, ft.Colors.BLUE_400])

    def create_anime_card(anime):
        print(f"Попытка загрузить изображение: {anime['poster']}")
        poster = ft.Image(src=anime["poster"], width=200, height=300, fit=ft.ImageFit.CONTAIN, error_content=ft.Text("Изображение не загрузилось", color=ft.colors.RED))
        title = ft.Text(anime["title"], size=18, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
        button = ft.ElevatedButton("Подробнее", on_click=lambda _: page.go(f"/details/{anime_list.index(anime)}"), style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)))
        return ft.Container(content=ft.Column([poster, title, button], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=250, height=500, gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[ft.colors.GREY_700, ft.colors.GREY_800]), border_radius=10, padding=10, shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color=ft.colors.BLACK54, offset=ft.Offset(0, 4)))

    cards = [create_anime_card(anime) for anime in anime_list]
    top_row = ft.Row(cards[:3], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    bottom_row = ft.Row(cards[3:], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    gallery_title = ft.Text("Галерея аниме", size=24, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE)
    back_button = ft.ElevatedButton("Назад", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)))
    gallery_content = ft.Column([gallery_title, back_button, top_row, bottom_row], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, scroll=ft.ScrollMode.AUTO)
    gallery_container = ft.Container(content=gallery_content, alignment=ft.alignment.center, expand=True)

    welcome_text = ft.Text("Добро пожаловать в виртуальный музей моих любимых аниме!", size=24, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
    welcome_button = ft.ElevatedButton("Перейти в галерею", on_click=lambda _: page.go("/gallery"), style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)))
    welcome_container = ft.Container(content=ft.Column([welcome_text, welcome_button], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), alignment=ft.alignment.center, expand=True)

    def create_details_page(anime):
        poster = ft.Image(src=anime["poster"], width=400, height=400, fit=ft.ImageFit.CONTAIN)
        title = ft.Text(anime["title"], size=28, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
        release_date = ft.Text(f"Дата выхода: {anime['release_date']}", size=18, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
        description_block = ft.Container(content=ft.Text(anime["description"], size=16, text_align=ft.TextAlign.JUSTIFY, color=ft.colors.WHITE), gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[ft.colors.GREY_700, ft.colors.GREY_800]), padding=20, border_radius=10, width=600, shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color=ft.colors.BLACK54, offset=ft.Offset(0, 4)))
        opinion_block = ft.Container(content=ft.Text(anime["opinion"], size=16, text_align=ft.TextAlign.JUSTIFY, color=ft.colors.WHITE), gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[ft.colors.GREY_700, ft.colors.GREY_800]), padding=20, border_radius=10, width=600, shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color=ft.colors.BLACK54, offset=ft.Offset(0, 4)))
        back_button = ft.ElevatedButton("Назад", on_click=lambda _: page.go("/gallery"), style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)))
        return ft.Container(content=ft.Column([poster, title, release_date, description_block, opinion_block, back_button], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, scroll=ft.ScrollMode.AUTO), alignment=ft.alignment.center, expand=True)

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", [welcome_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER, vertical_alignment=ft.MainAxisAlignment.CENTER, bgcolor=ft.colors.TRANSPARENT))
        elif page.route == "/gallery":
            page.views.append(ft.View("/gallery", [gallery_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER, vertical_alignment=ft.MainAxisAlignment.CENTER, bgcolor=ft.colors.TRANSPARENT))
        elif page.route.startswith("/details/"):
            try:
                index = int(page.route.split("/")[-1])
                if 0 <= index < len(anime_list):
                    details_container = create_details_page(anime_list[index])
                    page.views.append(ft.View(f"/details/{index}", [details_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER, vertical_alignment=ft.MainAxisAlignment.CENTER, bgcolor=ft.colors.TRANSPARENT))
                else:
                    page.go("/gallery")
            except ValueError:
                page.go("/gallery")
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)
