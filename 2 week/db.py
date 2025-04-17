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
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        self._populate_default_currencies()

    def _create_tables(self):
        """
        Создает таблицы в базе данных, если они отсутствуют
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
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Currencies" (
                "currency_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "code" TEXT NOT NULL UNIQUE,
                "name" TEXT,
                "symbol" TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Accounts" (
                "account_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "balance" REAL NOT NULL DEFAULT 0,
                "currency_id" INTEGER NOT NULL,
                "description" TEXT,
                "icon" TEXT,
                FOREIGN KEY ("user_id") REFERENCES "Users"("user_id") ON DELETE CASCADE,
                FOREIGN KEY ("currency_id") REFERENCES "Currencies"("currency_id") ON DELETE NO ACTION
            );
            """
        )
        self.conn.commit()

    def _populate_default_currencies(self):
        """
        Заполняет таблицу валют стандартными значениями, если она пуста
        """
        self.cursor.execute("SELECT COUNT(*) FROM Currencies")
        count = self.cursor.fetchone()[0]
        if count == 0:
            default_currencies = [
                ('USD', 'US Dollar', '$'),
                ('EUR', 'Euro', '€'),
                ('RUB', 'Russian Ruble', '₽')
            ]
            try:
                self.cursor.executemany(
                    "INSERT INTO Currencies (code, name, symbol) VALUES (?, ?, ?)",
                    default_currencies
                )
                self.conn.commit()
                print("Стандартные валюты добавлены.")
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении стандартных валют: {e}")
                self.conn.rollback()

    def add_user(self, username, email, password):
        """
        Добавляет нового пользователя
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
            print(f"Ошибка: Имя пользователя '{username}' или Email '{email}' уже существует.")
            return False

    def get_user_by_username_or_email(self, identifier):
        """
        Возвращает данные пользователя по имени пользователя или email
        """
        self.cursor.execute(
            "SELECT * FROM Users WHERE username = ? OR email = ?",
            (identifier, identifier),
        )
        user_data = self.cursor.fetchone()
        return user_data

    def verify_user(self, identifier, password):
        """
        Проверяет пользователя по имени пользователя или email и паролю
        """
        user = self.get_user_by_username_or_email(identifier)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None

    def create_session(self, user_id, duration_days=30):
        """
        Создает сессию для пользователя
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
            print(f"Ошибка при создании сессии: {e}")
            return None

    def get_user_by_session_token(self, token):
        """
        Возвращает данные пользователя по токену сессии
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
            print(f"Сессия с токеном {token[:8]}... удалена.")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении сессии с токеном {token[:8]}...: {e}")
            return False

    def delete_all_user_sessions(self, user_id):
        """
        Удаляет все сессии пользователя
        """
        try:
            self.cursor.execute("DELETE FROM Sessions WHERE user_id = ?", (user_id,))
            self.conn.commit()
            print(f"Все сессии для пользователя с ID {user_id} удалены.")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении сессий для пользователя с ID {user_id}: {e}")
            return False

    def close_connection(self):
        """
        Закрывает соединение с базой данных
        """
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто.")

    def get_currencies(self):
        """
        Возвращает список всех доступных валют
        """
        try:
            self.cursor.execute("SELECT currency_id, code, name, symbol FROM Currencies ORDER BY code")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка валют: {e}")
            return []

    def add_account(self, user_id, name, balance, currency_id, description, icon):
        """
        Добавляет новый счет для пользователя
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO Accounts (user_id, name, balance, currency_id, description, icon)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, name, balance, currency_id, description, icon)
            )
            self.conn.commit()
            print(f"Счет '{name}' успешно добавлен для пользователя с ID {user_id}.")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении счета '{name}' для пользователя с ID {user_id}: {e}")
            self.conn.rollback()
            return False

    def get_accounts_by_user(self, user_id):
        """
        Возвращает список всех счетов пользователя
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    a.account_id, a.name, a.balance, a.description, a.icon,
                    c.code as currency_code, c.symbol as currency_symbol
                FROM Accounts a
                JOIN Currencies c ON a.currency_id = c.currency_id
                WHERE a.user_id = ?
                ORDER BY a.name
                """,
                (user_id,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении счетов для пользователя с ID {user_id}: {e}")
            return []

    def get_account_by_id(self, account_id, user_id):
        """Fetches a single account by its ID, ensuring it belongs to the user."""
        try:
            self.cursor.execute(
                """
                SELECT
                    a.account_id, a.user_id, a.name, a.balance, a.currency_id,
                    a.description, a.icon,
                    c.code as currency_code, c.symbol as currency_symbol
                FROM Accounts a
                JOIN Currencies c ON a.currency_id = c.currency_id
                WHERE a.account_id = ? AND a.user_id = ?
                """,
                (account_id, user_id)
            )
            return self.cursor.fetchone() # Returns a single sqlite3.Row or None
        except sqlite3.Error as e:
            print(f"Error fetching account {account_id} for user {user_id}: {e}")
            return None

    def update_account(self, account_id, user_id, name, balance, currency_id, description, icon):
        """Updates an existing account for a user. Returns True on success, False on failure."""
        try:
            self.cursor.execute(
                """
                UPDATE Accounts
                SET name = ?, balance = ?, currency_id = ?, description = ?, icon = ?
                WHERE account_id = ? AND user_id = ?
                """,
                (name, balance, currency_id, description, icon, account_id, user_id)
            )
            self.conn.commit()
            # Check if any row was actually updated
            if self.cursor.rowcount > 0:
                print(f"Account ID {account_id} updated successfully for user_id {user_id}.")
                return True
            else:
                # This might happen if the account_id doesn't exist or doesn't belong to the user
                print(f"Account ID {account_id} not found or does not belong to user_id {user_id}. No update performed.")
                return False
        except sqlite3.Error as e:
            print(f"Error updating account ID {account_id} for user_id {user_id}: {e}")
            self.conn.rollback()
            return False

db_manager = DatabaseManager()
