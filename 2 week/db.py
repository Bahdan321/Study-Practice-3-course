import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import datetime


class DatabaseManager:
    """
    Класс для работы с базой данных
    """

    def __init__(self, db_name="finance_manager.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
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

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Sessions" (
                "session_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER NOT NULL,
                "token" TEXT NOT NULL UNIQUE,
                "expires_at" DATETIME NOT NULL,
                FOREIGN KEY ("user_id") REFERENCES "Users"("user_id") ON DELETE CASCADE
            );
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_session_token ON Sessions(token);
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
            "SELECT * FROM Users WHERE username = ? OR email = ?",
            (identifier, identifier),
        )
        user_data = self.cursor.fetchone()
        return user_data

    def verify_user(self, identifier, password):
        """
        Верифицирует пользователя
        """
        user = self.get_user_by_username_or_email(identifier)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None


    def create_session(self, user_id, duration_days=30):
        """
        Создание сессии
        """
        token = secrets.token_hex(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(days=duration_days)
        try:
            self.cursor.execute(
                "INSERT INTO Sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires_at),
            )
            self.conn.commit()
            return token
        except sqlite3.Error as e:
            print(f"Error creating session: {e}")
            return None

    def get_user_by_session_token(self, token):
        """
        Валидация пользователя по токену
        """
        now = datetime.datetime.now()
        self.cursor.execute(
            """
            SELECT u.* FROM Users u
            JOIN Sessions s ON u.user_id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
            """,
            (token, now),
        )
        user_data = self.cursor.fetchone()
        if user_data:
            return user_data
        else:
            self.cursor.execute("DELETE FROM Sessions WHERE token = ?", (token,))
            self.conn.commit()
            return None

    def delete_session(self, token):
        """
        Удаляет сессию по токену
        """
        try:
            self.cursor.execute("DELETE FROM Sessions WHERE token = ?", (token,))
            self.conn.commit()
            print(f"Session token {token[:8]}... deleted.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting session token {token[:8]}...: {e}")
            return False

    def delete_all_user_sessions(self, user_id):
        """
        Удаляет все сессии пользователя
        """
        try:
            self.cursor.execute("DELETE FROM Sessions WHERE user_id = ?", (user_id,))
            self.conn.commit()
            print(f"All sessions for user_id {user_id} deleted.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting sessions for user_id {user_id}: {e}")
            return False

    def close_connection(self):
        """
        Закрывает соединение с базой данных
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


db_manager = DatabaseManager()
