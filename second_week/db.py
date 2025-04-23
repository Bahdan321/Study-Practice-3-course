import os
import datetime
import secrets
import sqlite3
import bcrypt
from enum import Enum
from typing import Any, Iterable
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, or_, func, update, delete, and_
from sqlalchemy.sql import functions
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession, joinedload

from models.base import Base
from models.user import User, UserRole
from models.session import Session
from models.currency import Currency
from models.account import Account
from models.category import Category, TransactionType
from models.transaction import Transaction

load_dotenv()


# --- Enum’ы ------------------------------------------------------------------


class Role(Enum):
    user = "user"
    admin = "admin"


class TransactionType(Enum):
    expense = "expense"
    income = "income"


# --- Класс‑обёртка ------------------------------------------------------------


class DatabaseManager:
    """
    Упрощённый аналог DatabaseManager, но на чистом sqlite3.
    """

    def __init__(self, db_file: str = "finance_manager.db") -> None:
        self.db_file = db_file
        # Важно включить поддержку foreign keys
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

        self._create_tables()
        self._populate_default_currencies()
        self._populate_default_categories()

    # ----------------------------- service -----------------------------------

    def _exec(
        self,
        sql: str,
        params=None,
        many=False,
        fetch: str | None = None,  # None | "one" | "all"
    ):
        with self.conn:  # автоматически коммитит/ролбэкит
            cur = self.conn.cursor()
            if many:
                cur.executemany(sql, params or [])
            else:
                cur.execute(sql, params or [])

            if fetch == "one":
                res = cur.fetchone()
            elif fetch == "all":
                res = cur.fetchall()
            else:
                res = cur
            return res

            res = cur.rowcount  # для INSERT/UPDATE/DELETE

            # Убираем закрытие курсора, чтобы избежать ошибки
            # cur.close()
            return res

    # --------------------------- schema & mock data --------------------------

    def _create_tables(self):
        """Создание всех необходимых таблиц (если ещё нет)."""
        schema = """

        CREATE TABLE IF NOT EXISTS users (
            user_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role         TEXT NOT NULL DEFAULT 'user'           -- Role enum
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            token        TEXT UNIQUE NOT NULL,
            expires_at   TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS currencies (
            currency_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            code         TEXT UNIQUE NOT NULL,
            name         TEXT NOT NULL,
            symbol       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS accounts (
            account_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            name         TEXT NOT NULL,
            balance      REAL NOT NULL DEFAULT 0,
            currency_id  INTEGER NOT NULL,
            description  TEXT,
            icon         TEXT,
            FOREIGN KEY (user_id)     REFERENCES users(user_id)      ON DELETE CASCADE,
            FOREIGN KEY (currency_id) REFERENCES currencies(currency_id)
        );

        CREATE TABLE IF NOT EXISTS categories (
            category_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,                           -- NULL => дефолт
            name         TEXT NOT NULL,
            type         TEXT NOT NULL,                     -- TransactionType
            icon         TEXT,
            UNIQUE(user_id, name, type),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id      INTEGER NOT NULL,
            category_id     INTEGER NOT NULL,
            amount          REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            description     TEXT,
            type            TEXT NOT NULL,                 -- TransactionType
            FOREIGN KEY (account_id)  REFERENCES accounts(account_id)  ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );
        """
        self.conn.executescript(schema)
        self.conn.commit()

    def _populate_default_currencies(self):
        sql_count = "SELECT COUNT(*) FROM currencies;"
        count = self._exec(sql_count, fetch="one")[0]
        if count:
            return
        data = [
            ("RUB", "Российский рубль", "₽"),
            ("USD", "Доллар США", "$"),
            ("EUR", "Евро", "€"),
        ]
        self._exec(
            "INSERT INTO currencies (code, name, symbol) VALUES (?, ?, ?);",
            data,
            many=True,
        )
        self.conn.commit()

    def _populate_default_categories(self):
        sql_count = "SELECT COUNT(*) FROM categories WHERE user_id IS NULL;"
        count = self._exec(sql_count, fetch="one")[0]
        if count:
            return
        data = [
            ("Продукты", "expense", "shopping_cart"),
            ("Транспорт", "expense", "directions_bus"),
            ("Жилье", "expense", "home"),
            ("Кафе и рестораны", "expense", "restaurant"),
            ("Развлечения", "expense", "local_movies"),
            ("Одежда", "expense", "checkroom"),
            ("Здоровье", "expense", "local_hospital"),
            ("Подарки", "expense", "card_giftcard"),
            ("Другое (Расходы)", "expense", "category"),
            ("Зарплата", "income", "work"),
            ("Подарки", "income", "card_giftcard"),
            ("Инвестиции", "income", "trending_up"),
            ("Другое (Доходы)", "income", "category"),
        ]
        self._exec(
            "INSERT INTO categories (user_id, name, type, icon) VALUES (NULL, ?, ?, ?);",
            data,
            many=True,
        )
        self.conn.commit()

    # ----------------------------- USERS -------------------------------------

    def add_user(self, username: str, email: str, password: str):
        try:
            # Хешируем пароль с помощью bcrypt
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            # Сохраняем хеш как строку в БД (декодируем из байтов)
            hpw = hashed_password.decode("utf-8")
            self._exec(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?);",
                (username, email, hpw),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print("Integrity error:", e)
            return False

    def verify_user(self, identifier: str, password: str):
        row = self._exec(
            "SELECT * FROM users WHERE username = ? OR email = ?;",
            (identifier, identifier),
            fetch="one",
        )
        if row:
            stored_hash_bytes = row["password_hash"].encode("utf-8")
            password_bytes = password.encode("utf-8")
            # Проверяем пароль с помощью bcrypt
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                return {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "role": row["role"],
                }
        return None

    # ---------------------------- SESSIONS -----------------------------------

    def create_session(self, user_id: int, duration_days: int = 30):
        token = secrets.token_hex(32)
        expires_at = (
            datetime.datetime.utcnow() + datetime.timedelta(days=duration_days)
        ).isoformat()
        self._exec(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?);",
            (user_id, token, expires_at),
        )
        self.conn.commit()
        return token

    def get_user_by_session_token(self, token: str):
        row = self._exec(
            """
            SELECT u.* FROM sessions s
            JOIN users u ON u.user_id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?;
            """,
            (token, datetime.datetime.utcnow().isoformat()),
            fetch="one",
        )
        if row:
            return {
                "user_id": row["user_id"],
                "username": row["username"],
                "email": row["email"],
                "role": row["role"],
            }
        return None

    def delete_session(self, token: str):
        cur = self._exec("DELETE FROM sessions WHERE token = ?;", (token,))
        self.conn.commit()
        return cur.rowcount > 0

    # --------------------------- CURRENCIES ----------------------------------

    def get_currencies(self):
        cur = self._exec("SELECT * FROM currencies ORDER BY code;")
        return [dict(row) for row in cur.fetchall()]

    # ---------------------------- ACCOUNTS -----------------------------------

    def get_accounts_by_user(self, user_id: int):
        sql = """
        SELECT a.*, c.code AS currency_code, c.symbol AS currency_symbol
        FROM accounts a
        JOIN currencies c ON c.currency_id = a.currency_id
        WHERE a.user_id = ?
        ORDER BY a.name;
        """
        return [dict(r) for r in self._exec(sql, (user_id,)).fetchall()]

    def get_account_by_id(self, account_id: int, user_id: int):
        sql = """
        SELECT a.*, c.code AS currency_code, c.symbol AS currency_symbol
        FROM accounts a
        JOIN currencies c ON c.currency_id = a.currency_id
        WHERE a.account_id = ? AND a.user_id = ?;
        """
        row = self._exec(sql, (account_id, user_id), fetch="one")
        return dict(row) if row else None

    def add_account(self, user_id, name, balance, currency_id, description, icon):
        try:
            self._exec(
                """
                INSERT INTO accounts
                (user_id, name, balance, currency_id, description, icon)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (user_id, name, balance, currency_id, description, icon),
            )
            self.conn.commit()
            return True, "Account added"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def update_account(
        self, account_id, user_id, name, balance, currency_id, description, icon
    ):
        cur = self._exec(
            "UPDATE accounts SET name=?, balance=?, currency_id=?, description=?, icon=? "
            "WHERE account_id=? AND user_id=?;",
            (name, balance, currency_id, description, icon, account_id, user_id),
        )
        self.conn.commit()
        if cur.rowcount:
            return True, "Updated"
        return False, "Account not found or access denied"

    def delete_account(self, account_id: int, user_id: int):
        try:
            # удаляем транзакции
            self._exec("DELETE FROM transactions WHERE account_id = ?;", (account_id,))
            # удаляем счёт
            cur = self._exec(
                "DELETE FROM accounts WHERE account_id = ? AND user_id = ?;",
                (account_id, user_id),
            )
            self.conn.commit()
            if cur.rowcount:
                return True, "Deleted"
            return False, "Account not found or access denied"
        except Exception as e:
            self.conn.rollback()
            return False, f"DB error: {e}"

    # --------------------------- CATEGORIES ----------------------------------

    def get_categories_by_user_and_type(
        self, user_id: int, category_type: TransactionType
    ):
        if not isinstance(category_type, TransactionType):
            category_type = TransactionType(category_type)
        sql = """
        SELECT * FROM categories
        WHERE (user_id = ? OR user_id IS NULL) AND type = ?
        ORDER BY CASE WHEN user_id IS NULL THEN 1 ELSE 0 END DESC, name;
        """
        cur = self._exec(sql, (user_id, category_type.value))
        return [dict(r) for r in cur.fetchall()]

    def add_category(
        self,
        user_id: int,
        name: str,
        type_: TransactionType,
        icon: str | None = None,
    ):
        if not isinstance(type_, TransactionType):
            type_ = TransactionType(type_)
        try:
            self._exec(
                "INSERT INTO categories (user_id, name, type, icon) VALUES (?, ?, ?, ?);",
                (user_id, name.strip(), type_.value, icon),
            )
            self.conn.commit()
            cat_id = self._exec("SELECT last_insert_rowid();", fetch="one")[0]
            return {
                "category_id": cat_id,
                "user_id": user_id,
                "name": name.strip(),
                "type": type_.value,
                "icon": icon,
            }, None
        except sqlite3.IntegrityError:
            return None, f"Категория '{name}' уже существует."
        except Exception as e:
            self.conn.rollback()
            return None, str(e)

    # -------------------------- TRANSACTIONS ---------------------------------

    def add_transaction(
        self,
        account_id: int,
        category_id: int,
        amount: float,
        transaction_date,
        description: str,
        transaction_type: TransactionType,
    ):
        if not isinstance(transaction_type, TransactionType):
            transaction_type = TransactionType(transaction_type)
        if amount <= 0:
            return False, "Amount must be positive"
        # date -> iso
        if isinstance(transaction_date, datetime.datetime):
            dt_iso = transaction_date.isoformat()
        elif isinstance(transaction_date, str):
            dt_iso = transaction_date
        else:
            return False, "Invalid date"
        try:
            # проверяем счёт и категорию
            acc = self._exec(
                "SELECT balance FROM accounts WHERE account_id = ?;", (account_id,)
            ).fetchone()
            cat = self._exec(
                "SELECT 1 FROM categories WHERE category_id = ?;", (category_id,)
            ).fetchone()
            if not acc:
                return False, "Account not found"
            if not cat:
                return False, "Category not found"

            new_balance = (
                acc["balance"] + amount
                if transaction_type == TransactionType.income
                else acc["balance"] - amount
            )

            # всё в транзакции
            cur = self.conn.cursor()
            try:
                cur.execute(
                    """
                    INSERT INTO transactions
                    (account_id, category_id, amount, transaction_date, description, type)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        account_id,
                        category_id,
                        amount,
                        dt_iso,
                        description,
                        transaction_type.value,
                    ),
                )
                cur.execute(
                    "UPDATE accounts SET balance = ? WHERE account_id = ?;",
                    (new_balance, account_id),
                )
                self.conn.commit()
            finally:
                cur.close()

            return True, "OK"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def get_transactions_by_account(
        self, account_id: int, user_id: int, limit: int = 50, offset: int = 0
    ):
        # Проверка принадлежности счёта
        row = self._exec(
            "SELECT 1 FROM accounts WHERE account_id=? AND user_id=?;",
            (account_id, user_id),
        ).fetchone()
        if not row:
            return []
        sql = """
        SELECT t.*, c.name AS category_name, c.icon AS category_icon
        FROM transactions t
        LEFT JOIN categories c ON c.category_id = t.category_id
        WHERE t.account_id = ?
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
        LIMIT ? OFFSET ?;
        """
        cur = self._exec(sql, (account_id, limit, offset))
        return [dict(r) for r in cur.fetchall()]

    def update_transaction(self, transaction_id, user_id, **kwargs):
        print("update_transaction: not implemented for sqlite yet")
        return False, "Not implemented"

    def delete_transaction(self, transaction_id, user_id):
        print("delete_transaction: not implemented for sqlite yet")
        return False, "Not implemented"

    def get_transactions_summary(
        self,
        user_id: int,
        account_id: int,
        transaction_type: TransactionType,
        start_date: datetime.date,
        end_date: datetime.date,
    ):
        if not isinstance(transaction_type, TransactionType):
            transaction_type = TransactionType(transaction_type)
        # проверка счёта
        acc = self._exec(
            "SELECT 1 FROM accounts WHERE account_id=? AND user_id=?;",
            (account_id, user_id),
        ).fetchone()
        if not acc:
            return [], 0.0

        start_dt = datetime.datetime.combine(start_date, datetime.time.min).isoformat()
        end_dt = datetime.datetime.combine(end_date, datetime.time.max).isoformat()

        sql_tx = """
        SELECT t.*, c.name AS category_name, c.icon AS category_icon
        FROM transactions t
        LEFT JOIN categories c ON c.category_id = t.category_id
        WHERE t.account_id = ?
          AND t.type = ?
          AND t.transaction_date BETWEEN ? AND ?
        ORDER BY t.transaction_date DESC, t.transaction_id DESC;
        """
        tx = [
            dict(r)
            for r in self._exec(
                sql_tx, (account_id, transaction_type.value, start_dt, end_dt)
            ).fetchall()
        ]

        total = self._exec(
            """
            SELECT COALESCE(SUM(amount), 0) FROM transactions
            WHERE account_id = ? AND type = ? AND transaction_date BETWEEN ? AND ?;
            """,
            (account_id, transaction_type.value, start_dt, end_dt),
        ).fetchone()[0]

        return tx, total


# class DatabaseManager:
#     """
#     Класс для работы с базой данных PostgreSQL через SQLAlchemy (синхронный).
#     """

#     def __init__(self, sqlite: bool = False):
#         if sqlite:
#             print("SQLITE!!!")
#             db_url = "sqlite:///finance_manager.db"
#             self.engine = create_engine(db_url, echo=False)
#             self.SessionFactory = sessionmaker(bind=self.engine)
#             self._populate_default_currencies()
#             self._populate_default_categories()
#         else:
#             db_user = os.getenv("DB_USER")
#             db_password = os.getenv("DB_PASSWORD")
#             db_host = os.getenv("DB_HOST")
#             db_port = os.getenv("DB_PORT")
#             db_name = os.getenv("DB_NAME")
#             if not all([db_user, db_password, db_host, db_port, db_name]):
#                 raise ValueError("Database connection details missing in .env file")
#             db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#             self.engine = create_engine(db_url, echo=False)
#             self.SessionFactory = sessionmaker(bind=self.engine)
#             self._populate_default_currencies()
#             self._populate_default_categories()

#     def _create_tables(self):
#         """Создает таблицы, определенные в models через Base.metadata."""
#         try:
#             print("TABLES")
#             Base.metadata.create_all(self.engine)
#             print("Tables checked/created successfully.")
#         except Exception as e:
#             print(f"Error creating tables: {e}")
#             raise

#     def _get_session(self) -> SQLAlchemySession:
#         """Создает и возвращает новую сессию."""
#         return self.SessionFactory()

#     def _populate_default_currencies(self):
#         """Добавляет дефолтные валюты, если таблица пуста."""
#         with self._get_session() as session:
#             try:
#                 count = session.execute(select(func.count(Currency.currency_id))).scalar_one_or_none()
#                 if count is None or count == 0:
#                     default_currencies = [
#                         Currency(code="RUB", name="Российский рубль", symbol="₽"),
#                         Currency(code="USD", name="Доллар США", symbol="$"),
#                         Currency(code="EUR", name="Евро", symbol="€"),
#                     ]
#                     session.add_all(default_currencies)
#                     session.commit()
#                     print("Default currencies added.")
#             except Exception as e:
#                 print(f"Error populating default currencies: {e}")
#                 session.rollback()

#     def _populate_default_categories(self):
#         """Добавляет дефолтные категории расходов и доходов, если их нет."""
#         with self._get_session() as session:
#             try:
#                 count = session.execute(
#                     select(func.count(Category.category_id)).where(Category.user_id == None)
#                 ).scalar_one_or_none()
#                 if count is None or count == 0:
#                     default_categories = [
#                         Category(user_id=None, name="Продукты", type=TransactionType.expense, icon="shopping_cart"),
#                         Category(user_id=None, name="Транспорт", type=TransactionType.expense, icon="directions_bus"),
#                         Category(user_id=None, name="Жилье", type=TransactionType.expense, icon="home"),
#                         Category(user_id=None, name="Кафе и рестораны", type=TransactionType.expense, icon="restaurant"),
#                         Category(user_id=None, name="Развлечения", type=TransactionType.expense, icon="local_movies"),
#                         Category(user_id=None, name="Одежда", type=TransactionType.expense, icon="checkroom"),
#                         Category(user_id=None, name="Здоровье", type=TransactionType.expense, icon="local_hospital"),
#                         Category(user_id=None, name="Подарки", type=TransactionType.expense, icon="card_giftcard"),
#                         Category(user_id=None, name="Другое (Расходы)", type=TransactionType.expense, icon="category"),
#                         Category(user_id=None, name="Зарплата", type=TransactionType.income, icon="work"),
#                         Category(user_id=None, name="Подарки", type=TransactionType.income, icon="card_giftcard"),
#                         Category(user_id=None, name="Инвестиции", type=TransactionType.income, icon="trending_up"),
#                         Category(user_id=None, name="Другое (Доходы)", type=TransactionType.income, icon="category"),
#                     ]
#                     session.add_all(default_categories)
#                     session.commit()
#                     print("Default categories added.")
#             except Exception as e:
#                 print(f"Error populating default categories: {e}")
#                 session.rollback()

#     def add_user(self, username, email, password):
#         """Добавляет нового пользователя в базу данных."""
#         hashed_password = generate_password_hash(password)
#         new_user = User(username=username, email=email, password_hash=hashed_password)
#         with self._get_session() as session:
#             try:
#                 session.add(new_user)
#                 session.commit()
#                 print(f"User '{username}' added successfully.")
#                 return True
#             except Exception as e:
#                 print(f"Error adding user '{username}': {e}")
#                 session.rollback()
#                 return False

#     def verify_user(self, identifier, password):
#         """Проверяет учетные данные пользователя по имени или email."""
#         with self._get_session() as session:
#             try:
#                 stmt = select(User).where(
#                     or_(User.username == identifier, User.email == identifier)
#                 )
#                 user = session.execute(stmt).scalar_one_or_none()
#                 if user and check_password_hash(user.password_hash, password):
#                     return {
#                         "user_id": user.user_id,
#                         "username": user.username,
#                         "email": user.email,
#                         "role": user.role.value,
#                     }
#                 return None
#             except Exception as e:
#                 print(f"Error verifying user '{identifier}': {e}")
#                 return None

#     def create_session(self, user_id, duration_days=30):
#         """Создает постоянный токен сессии для пользователя."""
#         token = secrets.token_hex(32)
#         expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=duration_days)
#         new_session = Session(user_id=user_id, token=token, expires_at=expires_at)
#         with self._get_session() as session:
#             try:
#                 session.add(new_session)
#                 session.commit()
#                 print(f"Session created for user_id {user_id}, token: {token[:8]}...")
#                 return token
#             except Exception as e:
#                 print(f"Error creating session for user_id {user_id}: {e}")
#                 session.rollback()
#                 return None

#     def get_user_by_session_token(self, token):
#         """Получает данные пользователя по действующему токену сессии."""
#         with self._get_session() as session:
#             try:
#                 stmt = (
#                     select(Session)
#                     .where(
#                         Session.token == token,
#                         Session.expires_at > datetime.datetime.utcnow(),
#                     )
#                     .options(joinedload(Session.user))
#                 )
#                 valid_session = session.execute(stmt).scalar_one_or_none()
#                 if valid_session and valid_session.user:
#                     user = valid_session.user
#                     return {
#                         "user_id": user.user_id,
#                         "username": user.username,
#                         "email": user.email,
#                         "role": user.role.value,
#                     }
#                 return None
#             except Exception as e:
#                 print(f"Error validating session token '{token[:8]}...': {e}")
#                 return None

#     def delete_session(self, token):
#         """Удаляет токен сессии (выход из системы)."""
#         with self._get_session() as session:
#             try:
#                 stmt = delete(Session).where(Session.token == token)
#                 result = session.execute(stmt)
#                 session.commit()
#                 if result.rowcount > 0:
#                     print(f"Session token '{token[:8]}...' deleted.")
#                     return True
#                 else:
#                     print(f"Session token '{token[:8]}...' not found.")
#                     return False
#             except Exception as e:
#                 print(f"Error deleting session token '{token[:8]}...': {e}")
#                 session.rollback()
#                 return False

#     def get_currencies(self):
#         """Получает все доступные валюты."""
#         with self._get_session() as session:
#             try:
#                 stmt = select(Currency).order_by(Currency.code)
#                 currencies = session.execute(stmt).scalars().all()
#                 return [
#                     {
#                         "currency_id": c.currency_id,
#                         "code": c.code,
#                         "name": c.name,
#                         "symbol": c.symbol,
#                     }
#                     for c in currencies
#                 ]
#             except Exception as e:
#                 print(f"Error retrieving currencies: {e}")
#                 return []

#     def get_accounts_by_user(self, user_id):
#         """Получает все счета для конкретного пользователя с информацией о валюте."""
#         with self._get_session() as session:
#             try:
#                 stmt = (
#                     select(Account)
#                     .where(Account.user_id == user_id)
#                     .options(joinedload(Account.currency))
#                     .order_by(Account.name)
#                 )
#                 accounts = session.execute(stmt).scalars().all()
#                 return [
#                     {
#                         "account_id": acc.account_id,
#                         "user_id": acc.user_id,
#                         "name": acc.name,
#                         "balance": acc.balance,
#                         "currency_id": acc.currency_id,
#                         "description": acc.description,
#                         "icon": acc.icon,
#                         "currency_code": acc.currency.code,
#                         "currency_symbol": acc.currency.symbol,
#                     }
#                     for acc in accounts
#                 ]
#             except Exception as e:
#                 print(f"Error retrieving accounts for user_id {user_id}: {e}")
#                 return []

#     def get_account_by_id(self, account_id, user_id):
#         """Получает конкретный счет по его ID, проверяя принадлежность пользователю."""
#         with self._get_session() as session:
#             try:
#                 stmt = (
#                     select(Account)
#                     .where(Account.account_id == account_id, Account.user_id == user_id)
#                     .options(joinedload(Account.currency))
#                 )
#                 account = session.execute(stmt).scalar_one_or_none()
#                 if account:
#                     return {
#                         "account_id": account.account_id,
#                         "user_id": account.user_id,
#                         "name": account.name,
#                         "balance": account.balance,
#                         "currency_id": account.currency_id,
#                         "description": account.description,
#                         "icon": account.icon,
#                         "currency_code": account.currency.code,
#                         "currency_symbol": account.currency.symbol,
#                     }
#                 return None
#             except Exception as e:
#                 print(f"Error retrieving account ID {account_id} for user_id {user_id}: {e}")
#                 return None

#     def add_account(self, user_id, name, balance, currency_id, description, icon):
#         """Добавляет новый счет для пользователя."""
#         new_account = Account(
#             user_id=user_id,
#             name=name,
#             balance=balance,
#             currency_id=currency_id,
#             description=description,
#             icon=icon,
#         )
#         with self._get_session() as session:
#             try:
#                 session.add(new_account)
#                 session.commit()
#                 print(f"Account '{name}' added successfully for user_id {user_id}.")
#                 return True, "Account added successfully."
#             except Exception as e:
#                 print(f"Error adding account '{name}' for user_id {user_id}: {e}")
#                 session.rollback()
#                 return False, f"Database error: {e}"

#     def update_account(self, account_id, user_id, name, balance, currency_id, description, icon):
#         """Обновляет существующий счет с проверкой принадлежности."""
#         with self._get_session() as session:
#             try:
#                 stmt_select = select(Account).where(
#                     Account.account_id == account_id, Account.user_id == user_id
#                 )
#                 account_to_update = session.execute(stmt_select).scalar_one_or_none()
#                 if not account_to_update:
#                     print(f"Account ID {account_id} not found or does not belong to user_id {user_id}.")
#                     return False, "Account not found or access denied."
#                 account_to_update.name = name
#                 account_to_update.balance = balance
#                 account_to_update.currency_id = currency_id
#                 account_to_update.description = description
#                 account_to_update.icon = icon
#                 session.commit()
#                 print(f"Account ID {account_id} updated successfully for user_id {user_id}.")
#                 return True, "Account updated successfully."
#             except Exception as e:
#                 print(f"Error updating account ID {account_id} for user_id {user_id}: {e}")
#                 session.rollback()
#                 return False, f"Database error: {e}"

#     def delete_account(self, account_id, user_id):
#         """
#         Удаляет счет и все связанные с ним транзакции с проверкой принадлежности.
#         Возвращает (True, "Сообщение об успехе") или (False, "Сообщение об ошибке").
#         """
#         with self._get_session() as session:
#             try:
#                 account_to_delete = session.execute(
#                     select(Account).where(Account.account_id == account_id, Account.user_id == user_id)
#                 ).scalar_one_or_none()
#                 if not account_to_delete:
#                     return False, "Account not found or access denied."
#                 stmt_delete_transactions = delete(Transaction).where(Transaction.account_id == account_id)
#                 result_trans = session.execute(stmt_delete_transactions)
#                 print(f"Deleted {result_trans.rowcount} transactions for account ID {account_id}.")
#                 session.delete(account_to_delete)
#                 session.commit()
#                 print(f"Account ID {account_id} deleted successfully for user_id {user_id}.")
#                 return True, "Account and associated transactions deleted successfully."
#             except Exception as e:
#                 session.rollback()
#                 print(f"Error deleting account ID {account_id} for user_id {user_id}: {e}")
#                 return False, f"Database error during deletion: {e}"

#     def get_categories_by_user_and_type(self, user_id, category_type: TransactionType):
#         """
#         Получает категории для пользователя по типу (расход/доход),
#         включая дефолтные категории (user_id IS NULL).
#         """
#         if not isinstance(category_type, TransactionType):
#             try:
#                 category_type = TransactionType(category_type)
#             except ValueError:
#                 print(f"Invalid category type provided: {category_type}")
#                 return []
#         with self._get_session() as session:
#             try:
#                 stmt = (
#                     select(Category)
#                     .where(
#                         or_(Category.user_id == user_id, Category.user_id == None),
#                         Category.type == category_type,
#                     )
#                     .order_by(Category.user_id.desc().nullslast(), Category.name)
#                 )
#                 categories = session.execute(stmt).scalars().all()
#                 return [
#                     {
#                         "category_id": cat.category_id,
#                         "user_id": cat.user_id,
#                         "name": cat.name,
#                         "type": cat.type.value,
#                         "icon": cat.icon,
#                     }
#                     for cat in categories
#                 ]
#             except Exception as e:
#                 print(f"Error retrieving categories for user {user_id}, type {category_type.value}: {e}")
#                 return []

#     def add_transaction(self, account_id, category_id, amount, transaction_date, description, transaction_type: TransactionType):
#         """
#         Добавляет новую транзакцию и атомарно обновляет баланс счета.
#         Возвращает (True, "Сообщение об успехе") или (False, "Сообщение об ошибке").
#         """
#         if not isinstance(transaction_type, TransactionType):
#             try:
#                 transaction_type = TransactionType(transaction_type)
#             except ValueError:
#                 return False, "Invalid transaction type."
#         if amount <= 0:
#             return False, "Amount must be positive."
#         if isinstance(transaction_date, str):
#             try:
#                 transaction_date = datetime.datetime.fromisoformat(transaction_date.replace(" ", "T"))
#             except ValueError as e:
#                 print(f"Error parsing transaction date string '{transaction_date}': {e}")
#                 return False, "Invalid date format."
#         elif not isinstance(transaction_date, datetime.datetime):
#             return False, "Invalid transaction date type."
#         with self._get_session() as session:
#             try:
#                 account_to_update = session.get(Account, account_id)
#                 if not account_to_update:
#                     raise ValueError(f"Account with ID {account_id} not found.")
#                 category_exists = session.get(Category, category_id)
#                 if not category_exists:
#                     raise ValueError(f"Category with ID {category_id} not found.")
#                 new_transaction = Transaction(
#                     account_id=account_id,
#                     category_id=category_id,
#                     amount=amount,
#                     transaction_date=transaction_date,
#                     description=description,
#                     type=transaction_type,
#                 )
#                 session.add(new_transaction)
#                 if transaction_type == TransactionType.income:
#                     account_to_update.balance += amount
#                 else:
#                     account_to_update.balance -= amount
#                 session.commit()
#                 print(f"Transaction ({transaction_type.value}) of {amount} added for account ID {account_id}. New balance: {account_to_update.balance}")
#                 return True, "Transaction added successfully."
#             except Exception as e:
#                 session.rollback()
#                 print(f"Error adding transaction or updating balance: {e}")
#                 if "violates foreign key constraint" in str(e):
#                     if "fk_transactions_account_id_accounts" in str(e):
#                         return False, f"Error: Account with ID {account_id} does not exist."
#                     elif "fk_transactions_category_id_categories" in str(e):
#                         return False, f"Error: Category with ID {category_id} does not exist."
#                 elif isinstance(e, ValueError):
#                     return False, str(e)
#                 else:
#                     return False, f"Database error: {e}"

#     def get_transactions_by_account(self, account_id, user_id, limit=50, offset=0):
#         """Получает недавние транзакции для конкретного счета, принадлежащего пользователю."""
#         with self._get_session() as session:
#             try:
#                 account = session.execute(
#                     select(Account.account_id).where(Account.account_id == account_id, Account.user_id == user_id)
#                 ).scalar_one_or_none()
#                 if account is None:
#                     print(f"Access denied or account {account_id} not found for user {user_id}.")
#                     return []
#                 stmt = (
#                     select(Transaction)
#                     .where(Transaction.account_id == account_id)
#                     .options(joinedload(Transaction.category))
#                     .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
#                     .limit(limit)
#                     .offset(offset)
#                 )
#                 transactions = session.execute(stmt).scalars().all()
#                 return [
#                     {
#                         "transaction_id": t.transaction_id,
#                         "account_id": t.account_id,
#                         "category_id": t.category_id,
#                         "amount": t.amount,
#                         "transaction_date": t.transaction_date.isoformat(),
#                         "description": t.description,
#                         "type": t.type.value,
#                         "category_name": (t.category.name if t.category else "Deleted Category"),
#                         "category_icon": (t.category.icon if t.category else None),
#                     }
#                     for t in transactions
#                 ]
#             except Exception as e:
#                 print(f"Error retrieving transactions for account {account_id}: {e}")
#                 return []

#     def update_transaction(self, transaction_id, user_id, **kwargs):
#         """
#         Заглушка для обновления транзакции.
#         Необходима тщательная обработка корректировки баланса.
#         """
#         print(f"Warning: update_transaction (ID: {transaction_id}) not fully implemented.")
#         return False, "Update transaction functionality not yet implemented."

#     def delete_transaction(self, transaction_id, user_id):
#         """
#         Заглушка для удаления транзакции.
#         Необходима тщательная обработка корректировки баланса.
#         """
#         print(f"Warning: delete_transaction (ID: {transaction_id}) not fully implemented.")
#         return False, "Delete transaction functionality not yet implemented."

#     def get_transactions_summary(self, user_id: int, account_id: int, transaction_type: TransactionType, start_date: datetime.date, end_date: datetime.date):
#         """
#         Получает транзакции для конкретного счета, типа и в указанном диапазоне дат,
#         и вычисляет общую сумму за этот период.
#         Возвращает кортеж: (список транзакций, общая сумма)
#         """
#         if not isinstance(transaction_type, TransactionType):
#             try:
#                 transaction_type = TransactionType(transaction_type)
#             except ValueError:
#                 print(f"Invalid transaction type provided: {transaction_type}")
#                 return [], 0.0
#         end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
#         start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
#         with self._get_session() as session:
#             try:
#                 account_check = session.execute(
#                     select(Account.account_id).where(Account.account_id == account_id, Account.user_id == user_id)
#                 ).scalar_one_or_none()
#                 if account_check is None:
#                     print(f"Access denied or account {account_id} not found for user {user_id}.")
#                     return [], 0.0
#                 stmt_transactions = (
#                     select(Transaction)
#                     .where(
#                         and_(
#                             Transaction.account_id == account_id,
#                             Transaction.type == transaction_type,
#                             Transaction.transaction_date >= start_datetime,
#                             Transaction.transaction_date <= end_datetime,
#                         )
#                     )
#                     .options(joinedload(Transaction.category))
#                     .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
#                 )
#                 transactions_result = session.execute(stmt_transactions).scalars().all()
#                 stmt_sum = select(functions.sum(Transaction.amount)).where(
#                     and_(
#                         Transaction.account_id == account_id,
#                         Transaction.type == transaction_type,
#                         Transaction.transaction_date >= start_datetime,
#                         Transaction.transaction_date <= end_datetime,
#                     )
#                 )
#                 total_sum_result = session.execute(stmt_sum).scalar_one_or_none()
#                 total_sum = total_sum_result if total_sum_result is not None else 0.0
#                 formatted_transactions = [
#                     {
#                         "transaction_id": t.transaction_id,
#                         "account_id": t.account_id,
#                         "category_id": t.category_id,
#                         "amount": t.amount,
#                         "transaction_date": t.transaction_date.isoformat(),
#                         "description": t.description,
#                         "type": t.type.value,
#                         "category_name": (t.category.name if t.category else "N/A"),
#                         "category_icon": (t.category.icon if t.category else None),
#                     }
#                     for t in transactions_result
#                 ]
#                 return formatted_transactions, total_sum
#             except Exception as e:
#                 print(f"Error retrieving transaction summary for account {account_id}: {e}")
#                 session.rollback()
#                 return [], 0.0

#     def add_category(self, user_id: int, name: str, type: TransactionType, icon: str | None = None):
#         """Добавляет новую пользовательскую категорию для конкретного пользователя."""
#         if not isinstance(type, TransactionType):
#             try:
#                 type = TransactionType(type)
#             except ValueError:
#                 return None, "Invalid category type."
#         new_category = Category(
#             user_id=user_id,
#             name=name.strip(),
#             type=type,
#             icon=icon,
#         )
#         with self._get_session() as session:
#             try:
#                 session.add(new_category)
#                 session.commit()
#                 session.refresh(new_category)
#                 print(f"Custom category '{name}' added for user_id {user_id}.")
#                 return {
#                     "category_id": new_category.category_id,
#                     "user_id": new_category.user_id,
#                     "name": new_category.name,
#                     "type": new_category.type.value,
#                     "icon": new_category.icon,
#                 }, None
#             except Exception as e:
#                 session.rollback()
#                 print(f"Error adding category '{name}' for user {user_id}: {e}")
#                 if "uq_user_category_name_type" in str(e):
#                     return None, f"Категория с именем '{name}' и типом '{type.value}' уже существует."
#                 else:
#                     return None, f"Ошибка базы данных: {e}"
#             except Exception as e:
#                 session.rollback()
#                 print(f"Error adding category '{name}' for user {user_id}: {e}")
#                 return None, f"Произошла ошибка: {e}"


db_manager = DatabaseManager()
print("DatabaseManager instance created and initialized.")
db_manager._create_tables()
