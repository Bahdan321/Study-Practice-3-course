import os
import datetime
import secrets
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, or_, func, update, delete, and_
from sqlalchemy.sql import functions
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession, joinedload
from werkzeug.security import generate_password_hash, check_password_hash

from models.base import Base
from models.user import User, UserRole
from models.session import Session
from models.currency import Currency
from models.account import Account
from models.category import Category, TransactionType
from models.transaction import Transaction

load_dotenv()


class DatabaseManager:
    """
    Класс для работы с базой данных PostgreSQL через SQLAlchemy (синхронный).
    """

    def __init__(self, sqlite: bool = False):
        if sqlite:
            print("SQLITE!!!")
            db_url = "sqlite:///finance_manager.db"
            self.engine = create_engine(db_url, echo=False)
            self.SessionFactory = sessionmaker(bind=self.engine)
            self._populate_default_currencies()
            self._populate_default_categories()
        else:
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_name = os.getenv("DB_NAME")
            if not all([db_user, db_password, db_host, db_port, db_name]):
                raise ValueError("Database connection details missing in .env file")
            db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(db_url, echo=False)
            self.SessionFactory = sessionmaker(bind=self.engine)
            self._populate_default_currencies()
            self._populate_default_categories()

    def _create_tables(self):
        """Создает таблицы, определенные в models через Base.metadata."""
        try:
            print("TABLES")
            Base.metadata.create_all(self.engine)
            print("Tables checked/created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    def _get_session(self) -> SQLAlchemySession:
        """Создает и возвращает новую сессию."""
        return self.SessionFactory()

    def _populate_default_currencies(self):
        """Добавляет дефолтные валюты, если таблица пуста."""
        with self._get_session() as session:
            try:
                count = session.execute(select(func.count(Currency.currency_id))).scalar_one_or_none()
                if count is None or count == 0:
                    default_currencies = [
                        Currency(code="RUB", name="Российский рубль", symbol="₽"),
                        Currency(code="USD", name="Доллар США", symbol="$"),
                        Currency(code="EUR", name="Евро", symbol="€"),
                    ]
                    session.add_all(default_currencies)
                    session.commit()
                    print("Default currencies added.")
            except Exception as e:
                print(f"Error populating default currencies: {e}")
                session.rollback()

    def _populate_default_categories(self):
        """Добавляет дефолтные категории расходов и доходов, если их нет."""
        with self._get_session() as session:
            try:
                count = session.execute(
                    select(func.count(Category.category_id)).where(Category.user_id == None)
                ).scalar_one_or_none()
                if count is None or count == 0:
                    default_categories = [
                        Category(user_id=None, name="Продукты", type=TransactionType.expense, icon="shopping_cart"),
                        Category(user_id=None, name="Транспорт", type=TransactionType.expense, icon="directions_bus"),
                        Category(user_id=None, name="Жилье", type=TransactionType.expense, icon="home"),
                        Category(user_id=None, name="Кафе и рестораны", type=TransactionType.expense, icon="restaurant"),
                        Category(user_id=None, name="Развлечения", type=TransactionType.expense, icon="local_movies"),
                        Category(user_id=None, name="Одежда", type=TransactionType.expense, icon="checkroom"),
                        Category(user_id=None, name="Здоровье", type=TransactionType.expense, icon="local_hospital"),
                        Category(user_id=None, name="Подарки", type=TransactionType.expense, icon="card_giftcard"),
                        Category(user_id=None, name="Другое (Расходы)", type=TransactionType.expense, icon="category"),
                        Category(user_id=None, name="Зарплата", type=TransactionType.income, icon="work"),
                        Category(user_id=None, name="Подарки", type=TransactionType.income, icon="card_giftcard"),
                        Category(user_id=None, name="Инвестиции", type=TransactionType.income, icon="trending_up"),
                        Category(user_id=None, name="Другое (Доходы)", type=TransactionType.income, icon="category"),
                    ]
                    session.add_all(default_categories)
                    session.commit()
                    print("Default categories added.")
            except Exception as e:
                print(f"Error populating default categories: {e}")
                session.rollback()

    def add_user(self, username, email, password):
        """Добавляет нового пользователя в базу данных."""
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        with self._get_session() as session:
            try:
                session.add(new_user)
                session.commit()
                print(f"User '{username}' added successfully.")
                return True
            except Exception as e:
                print(f"Error adding user '{username}': {e}")
                session.rollback()
                return False

    def verify_user(self, identifier, password):
        """Проверяет учетные данные пользователя по имени или email."""
        with self._get_session() as session:
            try:
                stmt = select(User).where(
                    or_(User.username == identifier, User.email == identifier)
                )
                user = session.execute(stmt).scalar_one_or_none()
                if user and check_password_hash(user.password_hash, password):
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,
                    }
                return None
            except Exception as e:
                print(f"Error verifying user '{identifier}': {e}")
                return None

    def create_session(self, user_id, duration_days=30):
        """Создает постоянный токен сессии для пользователя."""
        token = secrets.token_hex(32)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=duration_days)
        new_session = Session(user_id=user_id, token=token, expires_at=expires_at)
        with self._get_session() as session:
            try:
                session.add(new_session)
                session.commit()
                print(f"Session created for user_id {user_id}, token: {token[:8]}...")
                return token
            except Exception as e:
                print(f"Error creating session for user_id {user_id}: {e}")
                session.rollback()
                return None

    def get_user_by_session_token(self, token):
        """Получает данные пользователя по действующему токену сессии."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Session)
                    .where(
                        Session.token == token,
                        Session.expires_at > datetime.datetime.utcnow(),
                    )
                    .options(joinedload(Session.user))
                )
                valid_session = session.execute(stmt).scalar_one_or_none()
                if valid_session and valid_session.user:
                    user = valid_session.user
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,
                    }
                return None
            except Exception as e:
                print(f"Error validating session token '{token[:8]}...': {e}")
                return None

    def delete_session(self, token):
        """Удаляет токен сессии (выход из системы)."""
        with self._get_session() as session:
            try:
                stmt = delete(Session).where(Session.token == token)
                result = session.execute(stmt)
                session.commit()
                if result.rowcount > 0:
                    print(f"Session token '{token[:8]}...' deleted.")
                    return True
                else:
                    print(f"Session token '{token[:8]}...' not found.")
                    return False
            except Exception as e:
                print(f"Error deleting session token '{token[:8]}...': {e}")
                session.rollback()
                return False

    def get_currencies(self):
        """Получает все доступные валюты."""
        with self._get_session() as session:
            try:
                stmt = select(Currency).order_by(Currency.code)
                currencies = session.execute(stmt).scalars().all()
                return [
                    {
                        "currency_id": c.currency_id,
                        "code": c.code,
                        "name": c.name,
                        "symbol": c.symbol,
                    }
                    for c in currencies
                ]
            except Exception as e:
                print(f"Error retrieving currencies: {e}")
                return []

    def get_accounts_by_user(self, user_id):
        """Получает все счета для конкретного пользователя с информацией о валюте."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Account)
                    .where(Account.user_id == user_id)
                    .options(joinedload(Account.currency))
                    .order_by(Account.name)
                )
                accounts = session.execute(stmt).scalars().all()
                return [
                    {
                        "account_id": acc.account_id,
                        "user_id": acc.user_id,
                        "name": acc.name,
                        "balance": acc.balance,
                        "currency_id": acc.currency_id,
                        "description": acc.description,
                        "icon": acc.icon,
                        "currency_code": acc.currency.code,
                        "currency_symbol": acc.currency.symbol,
                    }
                    for acc in accounts
                ]
            except Exception as e:
                print(f"Error retrieving accounts for user_id {user_id}: {e}")
                return []

    def get_account_by_id(self, account_id, user_id):
        """Получает конкретный счет по его ID, проверяя принадлежность пользователю."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Account)
                    .where(Account.account_id == account_id, Account.user_id == user_id)
                    .options(joinedload(Account.currency))
                )
                account = session.execute(stmt).scalar_one_or_none()
                if account:
                    return {
                        "account_id": account.account_id,
                        "user_id": account.user_id,
                        "name": account.name,
                        "balance": account.balance,
                        "currency_id": account.currency_id,
                        "description": account.description,
                        "icon": account.icon,
                        "currency_code": account.currency.code,
                        "currency_symbol": account.currency.symbol,
                    }
                return None
            except Exception as e:
                print(f"Error retrieving account ID {account_id} for user_id {user_id}: {e}")
                return None

    def add_account(self, user_id, name, balance, currency_id, description, icon):
        """Добавляет новый счет для пользователя."""
        new_account = Account(
            user_id=user_id,
            name=name,
            balance=balance,
            currency_id=currency_id,
            description=description,
            icon=icon,
        )
        with self._get_session() as session:
            try:
                session.add(new_account)
                session.commit()
                print(f"Account '{name}' added successfully for user_id {user_id}.")
                return True, "Account added successfully."
            except Exception as e:
                print(f"Error adding account '{name}' for user_id {user_id}: {e}")
                session.rollback()
                return False, f"Database error: {e}"

    def update_account(self, account_id, user_id, name, balance, currency_id, description, icon):
        """Обновляет существующий счет с проверкой принадлежности."""
        with self._get_session() as session:
            try:
                stmt_select = select(Account).where(
                    Account.account_id == account_id, Account.user_id == user_id
                )
                account_to_update = session.execute(stmt_select).scalar_one_or_none()
                if not account_to_update:
                    print(f"Account ID {account_id} not found or does not belong to user_id {user_id}.")
                    return False, "Account not found or access denied."
                account_to_update.name = name
                account_to_update.balance = balance
                account_to_update.currency_id = currency_id
                account_to_update.description = description
                account_to_update.icon = icon
                session.commit()
                print(f"Account ID {account_id} updated successfully for user_id {user_id}.")
                return True, "Account updated successfully."
            except Exception as e:
                print(f"Error updating account ID {account_id} for user_id {user_id}: {e}")
                session.rollback()
                return False, f"Database error: {e}"

    def delete_account(self, account_id, user_id):
        """
        Удаляет счет и все связанные с ним транзакции с проверкой принадлежности.
        Возвращает (True, "Сообщение об успехе") или (False, "Сообщение об ошибке").
        """
        with self._get_session() as session:
            try:
                account_to_delete = session.execute(
                    select(Account).where(Account.account_id == account_id, Account.user_id == user_id)
                ).scalar_one_or_none()
                if not account_to_delete:
                    return False, "Account not found or access denied."
                stmt_delete_transactions = delete(Transaction).where(Transaction.account_id == account_id)
                result_trans = session.execute(stmt_delete_transactions)
                print(f"Deleted {result_trans.rowcount} transactions for account ID {account_id}.")
                session.delete(account_to_delete)
                session.commit()
                print(f"Account ID {account_id} deleted successfully for user_id {user_id}.")
                return True, "Account and associated transactions deleted successfully."
            except Exception as e:
                session.rollback()
                print(f"Error deleting account ID {account_id} for user_id {user_id}: {e}")
                return False, f"Database error during deletion: {e}"

    def get_categories_by_user_and_type(self, user_id, category_type: TransactionType):
        """
        Получает категории для пользователя по типу (расход/доход),
        включая дефолтные категории (user_id IS NULL).
        """
        if not isinstance(category_type, TransactionType):
            try:
                category_type = TransactionType(category_type)
            except ValueError:
                print(f"Invalid category type provided: {category_type}")
                return []
        with self._get_session() as session:
            try:
                stmt = (
                    select(Category)
                    .where(
                        or_(Category.user_id == user_id, Category.user_id == None),
                        Category.type == category_type,
                    )
                    .order_by(Category.user_id.desc().nullslast(), Category.name)
                )
                categories = session.execute(stmt).scalars().all()
                return [
                    {
                        "category_id": cat.category_id,
                        "user_id": cat.user_id,
                        "name": cat.name,
                        "type": cat.type.value,
                        "icon": cat.icon,
                    }
                    for cat in categories
                ]
            except Exception as e:
                print(f"Error retrieving categories for user {user_id}, type {category_type.value}: {e}")
                return []

    def add_transaction(self, account_id, category_id, amount, transaction_date, description, transaction_type: TransactionType):
        """
        Добавляет новую транзакцию и атомарно обновляет баланс счета.
        Возвращает (True, "Сообщение об успехе") или (False, "Сообщение об ошибке").
        """
        if not isinstance(transaction_type, TransactionType):
            try:
                transaction_type = TransactionType(transaction_type)
            except ValueError:
                return False, "Invalid transaction type."
        if amount <= 0:
            return False, "Amount must be positive."
        if isinstance(transaction_date, str):
            try:
                transaction_date = datetime.datetime.fromisoformat(transaction_date.replace(" ", "T"))
            except ValueError as e:
                print(f"Error parsing transaction date string '{transaction_date}': {e}")
                return False, "Invalid date format."
        elif not isinstance(transaction_date, datetime.datetime):
            return False, "Invalid transaction date type."
        with self._get_session() as session:
            try:
                account_to_update = session.get(Account, account_id)
                if not account_to_update:
                    raise ValueError(f"Account with ID {account_id} not found.")
                category_exists = session.get(Category, category_id)
                if not category_exists:
                    raise ValueError(f"Category with ID {category_id} not found.")
                new_transaction = Transaction(
                    account_id=account_id,
                    category_id=category_id,
                    amount=amount,
                    transaction_date=transaction_date,
                    description=description,
                    type=transaction_type,
                )
                session.add(new_transaction)
                if transaction_type == TransactionType.income:
                    account_to_update.balance += amount
                else:
                    account_to_update.balance -= amount
                session.commit()
                print(f"Transaction ({transaction_type.value}) of {amount} added for account ID {account_id}. New balance: {account_to_update.balance}")
                return True, "Transaction added successfully."
            except Exception as e:
                session.rollback()
                print(f"Error adding transaction or updating balance: {e}")
                if "violates foreign key constraint" in str(e):
                    if "fk_transactions_account_id_accounts" in str(e):
                        return False, f"Error: Account with ID {account_id} does not exist."
                    elif "fk_transactions_category_id_categories" in str(e):
                        return False, f"Error: Category with ID {category_id} does not exist."
                elif isinstance(e, ValueError):
                    return False, str(e)
                else:
                    return False, f"Database error: {e}"

    def get_transactions_by_account(self, account_id, user_id, limit=50, offset=0):
        """Получает недавние транзакции для конкретного счета, принадлежащего пользователю."""
        with self._get_session() as session:
            try:
                account = session.execute(
                    select(Account.account_id).where(Account.account_id == account_id, Account.user_id == user_id)
                ).scalar_one_or_none()
                if account is None:
                    print(f"Access denied or account {account_id} not found for user {user_id}.")
                    return []
                stmt = (
                    select(Transaction)
                    .where(Transaction.account_id == account_id)
                    .options(joinedload(Transaction.category))
                    .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
                    .limit(limit)
                    .offset(offset)
                )
                transactions = session.execute(stmt).scalars().all()
                return [
                    {
                        "transaction_id": t.transaction_id,
                        "account_id": t.account_id,
                        "category_id": t.category_id,
                        "amount": t.amount,
                        "transaction_date": t.transaction_date.isoformat(),
                        "description": t.description,
                        "type": t.type.value,
                        "category_name": (t.category.name if t.category else "Deleted Category"),
                        "category_icon": (t.category.icon if t.category else None),
                    }
                    for t in transactions
                ]
            except Exception as e:
                print(f"Error retrieving transactions for account {account_id}: {e}")
                return []

    def update_transaction(self, transaction_id, user_id, **kwargs):
        """
        Заглушка для обновления транзакции.
        Необходима тщательная обработка корректировки баланса.
        """
        print(f"Warning: update_transaction (ID: {transaction_id}) not fully implemented.")
        return False, "Update transaction functionality not yet implemented."

    def delete_transaction(self, transaction_id, user_id):
        """
        Заглушка для удаления транзакции.
        Необходима тщательная обработка корректировки баланса.
        """
        print(f"Warning: delete_transaction (ID: {transaction_id}) not fully implemented.")
        return False, "Delete transaction functionality not yet implemented."

    def get_transactions_summary(self, user_id: int, account_id: int, transaction_type: TransactionType, start_date: datetime.date, end_date: datetime.date):
        """
        Получает транзакции для конкретного счета, типа и в указанном диапазоне дат,
        и вычисляет общую сумму за этот период.
        Возвращает кортеж: (список транзакций, общая сумма)
        """
        if not isinstance(transaction_type, TransactionType):
            try:
                transaction_type = TransactionType(transaction_type)
            except ValueError:
                print(f"Invalid transaction type provided: {transaction_type}")
                return [], 0.0
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        with self._get_session() as session:
            try:
                account_check = session.execute(
                    select(Account.account_id).where(Account.account_id == account_id, Account.user_id == user_id)
                ).scalar_one_or_none()
                if account_check is None:
                    print(f"Access denied or account {account_id} not found for user {user_id}.")
                    return [], 0.0
                stmt_transactions = (
                    select(Transaction)
                    .where(
                        and_(
                            Transaction.account_id == account_id,
                            Transaction.type == transaction_type,
                            Transaction.transaction_date >= start_datetime,
                            Transaction.transaction_date <= end_datetime,
                        )
                    )
                    .options(joinedload(Transaction.category))
                    .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
                )
                transactions_result = session.execute(stmt_transactions).scalars().all()
                stmt_sum = select(functions.sum(Transaction.amount)).where(
                    and_(
                        Transaction.account_id == account_id,
                        Transaction.type == transaction_type,
                        Transaction.transaction_date >= start_datetime,
                        Transaction.transaction_date <= end_datetime,
                    )
                )
                total_sum_result = session.execute(stmt_sum).scalar_one_or_none()
                total_sum = total_sum_result if total_sum_result is not None else 0.0
                formatted_transactions = [
                    {
                        "transaction_id": t.transaction_id,
                        "account_id": t.account_id,
                        "category_id": t.category_id,
                        "amount": t.amount,
                        "transaction_date": t.transaction_date.isoformat(),
                        "description": t.description,
                        "type": t.type.value,
                        "category_name": (t.category.name if t.category else "N/A"),
                        "category_icon": (t.category.icon if t.category else None),
                    }
                    for t in transactions_result
                ]
                return formatted_transactions, total_sum
            except Exception as e:
                print(f"Error retrieving transaction summary for account {account_id}: {e}")
                session.rollback()
                return [], 0.0

    def add_category(self, user_id: int, name: str, type: TransactionType, icon: str | None = None):
        """Добавляет новую пользовательскую категорию для конкретного пользователя."""
        if not isinstance(type, TransactionType):
            try:
                type = TransactionType(type)
            except ValueError:
                return None, "Invalid category type."
        new_category = Category(
            user_id=user_id,
            name=name.strip(),
            type=type,
            icon=icon,
        )
        with self._get_session() as session:
            try:
                session.add(new_category)
                session.commit()
                session.refresh(new_category)
                print(f"Custom category '{name}' added for user_id {user_id}.")
                return {
                    "category_id": new_category.category_id,
                    "user_id": new_category.user_id,
                    "name": new_category.name,
                    "type": new_category.type.value,
                    "icon": new_category.icon,
                }, None
            except Exception as e:
                session.rollback()
                print(f"Error adding category '{name}' for user {user_id}: {e}")
                if "uq_user_category_name_type" in str(e):
                    return None, f"Категория с именем '{name}' и типом '{type.value}' уже существует."
                else:
                    return None, f"Ошибка базы данных: {e}"
            except Exception as e:
                session.rollback()
                print(f"Error adding category '{name}' for user {user_id}: {e}")
                return None, f"Произошла ошибка: {e}"


db_manager = DatabaseManager(sqlite=True)
print("DatabaseManager instance created and initialized.")
db_manager._create_tables()
