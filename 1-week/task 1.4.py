class Comment:
    def __init__(self, comment_id, author, post, content):
        self.comment_id = comment_id
        self.author = author
        self.post = post
        self.content = content


class Post:
    def __init__(self, post_id, author, content):
        self.post_id = post_id
        self.author = author
        self.content = content
        self.comments = []

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def remove_comment(self, comment: Comment):
        if comment in self.comments:
            self.comments.remove(comment)


class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.posts = []
        self.comments = []

    def add_post(self, post: Post):
        self.posts.append(post)

    def remove_post(self, post: Post):
        if post in self.posts:
            self.posts.remove(post)

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def remove_comment(self, comment: Comment):
        if comment in self.comments:
            self.comments.remove(comment)


evg = User(1, "ЕвгенийMazda")
egor = User(2, "ЕгорBenz")


post1 = Post(101, evg, "Емае, шяс бы бахнуть по 1000км на Мазде")
evg.add_post(post1)


comment1 = Comment(
    201, egor, post1, "Евгений, а ниче тот факт, что ты на Мазде? А я на Бензе"
)
post1.add_comment(comment1)
egor.add_comment(comment1)


print(f"Пост {post1.post_id} от {post1.author.username}: {post1.content}")
for comment in post1.comments:
    print(
        f"Комментарий {comment.comment_id} от {comment.author.username}: {comment.content}"
    )


post1.remove_comment(comment1)
egor.remove_comment(comment1)


print(f"Комментарии к посту {post1.post_id}: {len(post1.comments)}")
