import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class DatabaseManager:
    """
    Класс для работы с базой данных
    """
    def __init__(self, db_name="finance_manager.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """
        Создает таблицы в базе данных, если они не существуют
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Users" (
                "user_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "username" TEXT NOT NULL UNIQUE,
                "email" TEXT NOT NULL UNIQUE,
                "password_hash" TEXT NOT NULL,
                "role" VARCHAR DEFAULT 'user'
            );
        """
        )
        self.conn.commit()

    def add_user(self, username, email, password):
        """
        Создает нового пользователя
        """
        password_hash = generate_password_hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Username '{username}' or Email '{email}' already exists.")
            return False

    def get_user_by_username_or_email(self, identifier):
        """
        Получает пользователя по имени пользователя или почте
        """
        self.cursor.execute(
            "SELECT user_id, username, email, password_hash, role FROM Users WHERE username = ? OR email = ?",
            (identifier, identifier),
        )
        user_data = self.cursor.fetchone()
        if user_data:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, user_data))
        return None

    def verify_user(self, identifier, password):
        """
        Верифицирует пользователя
        """
        user = self.get_user_by_username_or_email(identifier)
        if user and check_password_hash(user["password_hash"], password):
            return user  # Return user data if password is correct
        return None

    def close_connection(self):
        """
        Закрывает соединение с базой данных
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

db_manager = DatabaseManager()
