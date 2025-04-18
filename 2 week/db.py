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
        self.conn.row_factory = (
            sqlite3.Row
        )  # Удобно для доступа к данным по имени столбца
        self.cursor = self.conn.cursor()
        # Включаем поддержку внешних ключей для целостности данных
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        self._populate_default_currencies()
        # Опционально: Добавить стандартные категории при первом запуске
        self._populate_default_categories()

    def _create_tables(self):
        """
        Создает таблицы в базе данных, если они отсутствуют
        """
        # --- Существующие таблицы ---
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

        # --- НОВЫЕ ТАБЛИЦЫ ---

        # Таблица категорий
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Categories" (
                "category_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "type" TEXT NOT NULL CHECK(type IN ('income', 'expense')), -- Тип: доход или расход
                "icon" TEXT, -- Иконка категории (опционально)
                FOREIGN KEY ("user_id") REFERENCES "Users"("user_id") ON DELETE CASCADE,
                UNIQUE(user_id, name, type) -- Категория должна быть уникальной для пользователя и типа
            );
            """
        )
        self.cursor.execute(
            """
             CREATE INDEX IF NOT EXISTS idx_category_user_type ON Categories(user_id, type);
            """
        )

        # Таблица транзакций
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Transactions" (
                "transaction_id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "account_id" INTEGER NOT NULL,
                "category_id" INTEGER, -- Может быть NULL, если категория удалена
                "amount" REAL NOT NULL CHECK(amount > 0), -- Сумма всегда положительная
                "transaction_date" TEXT NOT NULL, -- Храним как TEXT в формате ISO (YYYY-MM-DD HH:MM:SS)
                "description" TEXT,
                "type" TEXT NOT NULL CHECK(type IN ('income', 'expense')), -- Тип транзакции (дублирует тип категории для простоты и надежности)
                "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP, -- Дата создания записи
                FOREIGN KEY ("account_id") REFERENCES "Accounts"("account_id") ON DELETE CASCADE, -- Если счет удален, транзакции тоже
                FOREIGN KEY ("category_id") REFERENCES "Categories"("category_id") ON DELETE SET NULL -- Если категория удалена, связь обнуляется
            );
            """
        )
        self.cursor.execute(
            """
             CREATE INDEX IF NOT EXISTS idx_transaction_account_date ON Transactions(account_id, transaction_date);
            """
        )
        self.cursor.execute(
            """
             CREATE INDEX IF NOT EXISTS idx_transaction_category ON Transactions(category_id);
             """
        )
        self.cursor.execute(
            """
             CREATE INDEX IF NOT EXISTS idx_transaction_type ON Transactions(type);
             """
        )

        self.conn.commit()
        print("Проверка и создание таблиц завершены.")
        self._populate_default_currencies()
        self._populate_default_categories()

    def _populate_default_currencies(self):
        """
        Заполняет таблицу валют стандартными значениями, если она пуста
        """
        self.cursor.execute("SELECT COUNT(*) FROM Currencies")
        count = self.cursor.fetchone()[0]
        if count == 0:
            default_currencies = [
                ("USD", "US Dollar", "$"),
                ("EUR", "Euro", "€"),
                ("RUB", "Russian Ruble", "₽"),
                # Добавьте другие по необходимости
            ]
            try:
                self.cursor.executemany(
                    "INSERT INTO Currencies (code, name, symbol) VALUES (?, ?, ?)",
                    default_currencies,
                )
                self.conn.commit()
                print("Стандартные валюты добавлены.")
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении стандартных валют: {e}")
                self.conn.rollback()

    def _populate_default_categories(self):
        """Adds default expense and income categories if none exist."""
        self.cursor.execute("SELECT COUNT(*) FROM Categories WHERE user_id IS NULL")
        count = self.cursor.fetchone()[0]
        if count == 0:
            default_categories = [
                # Expenses
                (None, "Продукты", "expense", "shopping_cart"),
                (None, "Транспорт", "expense", "directions_bus"),
                (None, "Жилье", "expense", "home"),
                (None, "Кафе и рестораны", "expense", "restaurant"),
                (None, "Развлечения", "expense", "local_movies"),
                (None, "Одежда", "expense", "checkroom"),
                (None, "Здоровье", "expense", "local_hospital"),
                (None, "Подарки", "expense", "card_giftcard"),
                (None, "Другое (Расходы)", "expense", "category"),
                # Income
                (None, "Зарплата", "income", "work"),
                (None, "Подарки", "income", "card_giftcard"),
                (None, "Инвестиции", "income", "trending_up"),
                (None, "Другое (Доходы)", "income", "category"),
            ]
            try:
                self.cursor.executemany(
                    "INSERT INTO Categories (user_id, name, type, icon) VALUES (?, ?, ?, ?)",
                    default_categories,
                )
                self.conn.commit()
                print("Стандартные категории добавлены.")
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении стандартных категорий: {e}")
                self.conn.rollback()

    # --- Методы для пользователей, сессий, счетов (остаются без изменений) ---
    def add_user(self, username, email, password):
        password_hash = generate_password_hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            self.conn.commit()
            user_id = self.cursor.lastrowid
            # Можно добавить стандартные категории для нового пользователя
            # self._add_default_categories_for_user(user_id)
            return True, user_id  # Возвращаем ID для возможного использования
        except sqlite3.IntegrityError:
            print(
                f"Ошибка: Имя пользователя '{username}' или Email '{email}' уже существует."
            )
            return False, None
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            self.conn.rollback()
            return False, None

    # ... (get_user_by_username_or_email, verify_user, create_session, etc. остаются тут) ...
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
        # Продлеваем сессию при каждом запросе (опционально)
        # if user_data:
        #     new_expires_at = datetime.datetime.now() + datetime.timedelta(days=30) # или другое время
        #     self.cursor.execute("UPDATE Sessions SET expires_at = ? WHERE token = ?", (new_expires_at, token))
        #     self.conn.commit()
        # else:
        #     # Удаляем просроченные или невалидные токены
        #     self.cursor.execute("DELETE FROM Sessions WHERE token = ? OR expires_at <= ?", (token, now))
        #     self.conn.commit()
        if not user_data:
            self.cursor.execute("DELETE FROM Sessions WHERE token = ?", (token,))
            self.conn.commit()

        return user_data

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
            self.cursor.execute(
                "SELECT currency_id, code, name, symbol FROM Currencies ORDER BY code"
            )
            # Преобразуем sqlite3.Row в словари для совместимости, если нужно
            # return [dict(row) for row in self.cursor.fetchall()]
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
                (user_id, name, balance, currency_id, description, icon),
            )
            self.conn.commit()
            print(f"Счет '{name}' успешно добавлен для пользователя с ID {user_id}.")
            return True, self.cursor.lastrowid  # Возвращаем статус и ID
        except sqlite3.Error as e:
            print(
                f"Ошибка при добавлении счета '{name}' для пользователя с ID {user_id}: {e}"
            )
            self.conn.rollback()
            return False, None

    def get_accounts_by_user(self, user_id):
        """
        Возвращает список всех счетов пользователя с информацией о валюте.
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    a.account_id, a.name, a.balance, a.description, a.icon,
                    c.currency_id, c.code as currency_code, c.symbol as currency_symbol
                FROM Accounts a
                JOIN Currencies c ON a.currency_id = c.currency_id
                WHERE a.user_id = ?
                ORDER BY a.name
                """,
                (user_id,),
            )
            # Преобразуем sqlite3.Row в словари для удобства в Flet
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка при получении счетов для пользователя с ID {user_id}: {e}")
            return []

    def get_account_by_id(self, account_id, user_id):
        """Получает один счет по его ID, убедившись, что он принадлежит пользователю."""
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
                (account_id, user_id),
            )
            # Преобразуем sqlite3.Row в словарь или None
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(
                f"Ошибка при получении счета {account_id} для пользователя {user_id}: {e}"
            )
            return None

    def update_account(
        self, account_id, user_id, name, balance, currency_id, description, icon
    ):
        """Обновляет существующий счет пользователя. Возвращает True при успехе, False при ошибке."""
        try:
            self.cursor.execute(
                """
                UPDATE Accounts
                SET name = ?, balance = ?, currency_id = ?, description = ?, icon = ?
                WHERE account_id = ? AND user_id = ?
                """,
                (name, balance, currency_id, description, icon, account_id, user_id),
            )
            self.conn.commit()
            # Проверяем, была ли строка действительно обновлена
            if self.cursor.rowcount > 0:
                print(f"Счет ID {account_id} успешно обновлен для user_id {user_id}.")
                return True
            else:
                # Это может произойти, если account_id не существует или не принадлежит пользователю
                print(
                    f"Счет ID {account_id} не найден или не принадлежит user_id {user_id}. Обновление не выполнено."
                )
                return False
        except sqlite3.Error as e:
            print(
                f"Ошибка при обновлении счета ID {account_id} для user_id {user_id}: {e}"
            )
            self.conn.rollback()
            return False

    def delete_account(self, account_id, user_id):
        """Удаляет счет пользователя. Благодаря ON DELETE CASCADE, связанные транзакции тоже удалятся."""
        try:
            # Дополнительная проверка, что счет принадлежит пользователю (хотя CASCADE сделает свое дело)
            self.cursor.execute(
                "DELETE FROM Accounts WHERE account_id = ? AND user_id = ?",
                (account_id, user_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(
                    f"Счет ID {account_id} и связанные транзакции удалены для user_id {user_id}."
                )
                return True
            else:
                print(
                    f"Счет ID {account_id} не найден или не принадлежит user_id {user_id}. Удаление не выполнено."
                )
                return False
        except sqlite3.Error as e:
            print(
                f"Ошибка при удалении счета ID {account_id} для user_id {user_id}: {e}"
            )
            self.conn.rollback()
            return False

    # --- НОВЫЕ МЕТОДЫ ---

    def add_category(self, user_id, name, type, icon=None):
        """Добавляет новую категорию для пользователя."""
        if type not in ("income", "expense"):
            print(
                f"Ошибка: Неверный тип категории '{type}'. Должен быть 'income' или 'expense'."
            )
            return False, "Неверный тип категории."
        try:
            self.cursor.execute(
                """
                INSERT INTO Categories (user_id, name, type, icon)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, name, type, icon),
            )
            self.conn.commit()
            print(
                f"Категория '{name}' ({type}) добавлена для пользователя ID {user_id}."
            )
            return True, "Категория успешно добавлена."
        except sqlite3.IntegrityError:
            print(
                f"Ошибка: Категория '{name}' ({type}) уже существует для пользователя ID {user_id}."
            )
            self.conn.rollback()
            return False, "Категория с таким именем и типом уже существует."
        except sqlite3.Error as e:
            print(
                f"Ошибка при добавлении категории '{name}' для пользователя ID {user_id}: {e}"
            )
            self.conn.rollback()
            return False, f"Ошибка базы данных: {e}"

    def get_categories_by_user_and_type(self, user_id, transaction_type):
        """
        Возвращает список категорий пользователя И стандартных категорий
        для указанного типа ('income' или 'expense').
        Стандартные категории имеют user_id = NULL.
        """
        if transaction_type not in ("income", "expense"):
            print(
                f"Ошибка: Неверный тип транзакции '{transaction_type}' при запросе категорий."
            )
            return []
        try:
            self.cursor.execute(
                """
                SELECT category_id, name, icon, user_id -- Добавил user_id для отладки, если нужно
                FROM Categories
                WHERE (user_id = ? OR user_id IS NULL) -- Ищем категории пользователя ИЛИ стандартные
                AND type = ?
                ORDER BY user_id DESC, name -- Опционально: сначала пользовательские, потом стандартные, или просто по имени
                """,
                (user_id, transaction_type),
            )
            # Возвращаем список словарей для удобства использования в Flet
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(
                f"Ошибка при получении категорий типа '{transaction_type}' для пользователя ID {user_id} (включая стандартные): {e}"
            )
            return []

    def get_category_by_id(self, category_id, user_id):
        """Получает одну категорию по ID, проверяя принадлежность пользователю."""
        try:
            self.cursor.execute(
                """
                SELECT category_id, user_id, name, type, icon
                FROM Categories
                WHERE category_id = ? AND user_id = ?
                """,
                (category_id, user_id),
            )
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(
                f"Ошибка при получении категории ID {category_id} для пользователя {user_id}: {e}"
            )
            return None

    def update_category(self, category_id, user_id, name, icon=None):
        """Обновляет имя и иконку категории. Тип категории менять не позволяем через этот метод."""
        try:
            self.cursor.execute(
                """
                UPDATE Categories
                SET name = ?, icon = ?
                WHERE category_id = ? AND user_id = ?
                """,
                (name, icon, category_id, user_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(
                    f"Категория ID {category_id} обновлена для пользователя {user_id}."
                )
                return True
            else:
                print(
                    f"Категория ID {category_id} не найдена или не принадлежит пользователю {user_id}."
                )
                return False
        except sqlite3.IntegrityError:  # Если новое имя уже занято
            print(
                f"Ошибка: Категория с именем '{name}' уже существует для этого пользователя и типа."
            )
            self.conn.rollback()
            return False
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении категории ID {category_id}: {e}")
            self.conn.rollback()
            return False

    def delete_category(self, category_id, user_id):
        """
        Удаляет категорию.
        Транзакции, связанные с этой категорией, будут иметь category_id = NULL
        (из-за ON DELETE SET NULL).
        """
        try:
            # Убедимся, что категория принадлежит пользователю перед удалением
            self.cursor.execute(
                "DELETE FROM Categories WHERE category_id = ? AND user_id = ?",
                (category_id, user_id),
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Категория ID {category_id} удалена для пользователя {user_id}.")
                return True
            else:
                print(
                    f"Категория ID {category_id} не найдена или не принадлежит пользователю {user_id}."
                )
                return False
        except sqlite3.Error as e:
            print(f"Ошибка при удалении категории ID {category_id}: {e}")
            self.conn.rollback()
            return False

    def add_transaction(
        self,
        account_id,
        category_id,
        amount,
        transaction_date,
        description,
        transaction_type,
    ):
        """
        Добавляет транзакцию и обновляет баланс счета.
        Возвращает (True, "Сообщение об успехе") или (False, "Сообщение об ошибке").
        """
        if transaction_type not in ("income", "expense"):
            return False, "Неверный тип транзакции."
        if amount <= 0:
            return False, "Сумма должна быть положительной."

        # Начинаем транзакцию базы данных для атомарности
        try:
            self.cursor.execute("BEGIN TRANSACTION")

            # 1. Добавляем запись в таблицу транзакций
            self.cursor.execute(
                """
                INSERT INTO Transactions (account_id, category_id, amount, transaction_date, description, type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    category_id,
                    amount,
                    transaction_date,
                    description,
                    transaction_type,
                ),
            )
            transaction_id = self.cursor.lastrowid  # Получаем ID добавленной транзакции

            # 2. Обновляем баланс счета
            if transaction_type == "income":
                update_sql = (
                    "UPDATE Accounts SET balance = balance + ? WHERE account_id = ?"
                )
            else:  # expense
                update_sql = (
                    "UPDATE Accounts SET balance = balance - ? WHERE account_id = ?"
                )

            self.cursor.execute(update_sql, (amount, account_id))

            # Проверяем, что счет был обновлен (что он существует)
            if self.cursor.rowcount == 0:
                # Если счет не найден, откатываем транзакцию
                raise sqlite3.Error(
                    f"Счет с ID {account_id} не найден при обновлении баланса."
                )

            # Завершаем транзакцию базы данных
            self.conn.commit()
            print(
                f"Транзакция ID {transaction_id} ({transaction_type}) на сумму {amount} добавлена для счета ID {account_id}."
            )
            return True, "Транзакция успешно добавлена."

        except sqlite3.Error as e:
            # Если произошла ошибка, откатываем все изменения
            self.conn.rollback()
            print(f"Ошибка при добавлении транзакции или обновлении баланса: {e}")
            # Возвращаем конкретную ошибку, если это ошибка внешнего ключа для категории
            if "FOREIGN KEY constraint failed" in str(e) and "Categories" in str(e):
                return (
                    False,
                    f"Ошибка: Выбранная категория (ID {category_id}) не существует.",
                )
            elif "FOREIGN KEY constraint failed" in str(e) and "Accounts" in str(e):
                return False, f"Ошибка: Выбранный счет (ID {account_id}) не существует."
            else:
                return False, f"Ошибка базы данных при добавлении транзакции: {e}"

    # --- Методы для получения и управления транзакциями (можно добавить позже) ---

    def get_transactions_by_account(self, account_id, user_id, limit=50, offset=0):
        """Получает последние транзакции для конкретного счета пользователя."""
        # Сначала проверим, принадлежит ли счет пользователю
        account = self.get_account_by_id(account_id, user_id)
        if not account:
            print(
                f"Ошибка: Счет {account_id} не найден или не принадлежит пользователю {user_id}."
            )
            return []
        try:
            self.cursor.execute(
                """
                 SELECT
                     t.transaction_id, t.account_id, t.category_id, t.amount,
                     t.transaction_date, t.description, t.type, t.created_at,
                     c.name as category_name, c.icon as category_icon
                 FROM Transactions t
                 LEFT JOIN Categories c ON t.category_id = c.category_id -- LEFT JOIN на случай удаленной категории
                 WHERE t.account_id = ?
                 ORDER BY t.transaction_date DESC, t.transaction_id DESC
                 LIMIT ? OFFSET ?
                 """,
                (account_id, limit, offset),
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка при получении транзакций для счета {account_id}: {e}")
            return []

    # Метод для обновления транзакции (сложнее, т.к. надо пересчитывать балансы)
    # Метод для удаления транзакции (тоже требует пересчета баланса)


# Создаем экземпляр менеджера базы данных (обычно делается один раз при старте приложения)
db_manager = DatabaseManager()
