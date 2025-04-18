import os
import datetime
import secrets
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, or_, func, update, delete
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession, joinedload
from werkzeug.security import generate_password_hash, check_password_hash

# Import models
from models.base import Base
from models.user import User, UserRole
from models.session import Session
from models.currency import Currency
from models.account import Account
from models.category import Category, TransactionType
from models.transaction import Transaction

# Load environment variables from .env file
load_dotenv()


class DatabaseManager:
    """
    Класс для работы с базой данных PostgreSQL через SQLAlchemy (синхронный).
    """

    def __init__(self):
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("Database connection details missing in .env file")

        # Construct the database URL
        # postgresql+psycopg2://user:password@host:port/database
        db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Create engine
        self.engine = create_engine(
            db_url, echo=False
        )  # Set echo=True for debugging SQL

        # Create session factory
        self.SessionFactory = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        # self._create_tables()
        # Populate default data if necessary
        self._populate_default_currencies()
        self._populate_default_categories()

    def _create_tables(self):
        """Creates tables defined in models using Base metadata."""
        try:
            Base.metadata.create_all(self.engine)
            print("Tables checked/created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            # Depending on the error, you might want to raise it or handle it differently
            raise

    def _get_session(self) -> SQLAlchemySession:
        """Provides a new session."""
        return self.SessionFactory()

    # === Default Data Population ===

    def _populate_default_currencies(self):
        """Adds default currencies if the table is empty."""
        with self._get_session() as session:
            try:
                # Check if currencies already exist
                count = session.execute(
                    select(func.count(Currency.currency_id))
                ).scalar_one_or_none()
                if count is None or count == 0:
                    default_currencies = [
                        Currency(code="RUB", name="Российский рубль", symbol="₽"),
                        Currency(code="USD", name="Доллар США", symbol="$"),
                        Currency(code="EUR", name="Евро", symbol="€"),
                        # Add more currencies as needed
                    ]
                    session.add_all(default_currencies)
                    session.commit()
                    print("Default currencies added.")
                # else:
                #     print("Currencies table already populated.")
            except Exception as e:
                print(f"Error populating default currencies: {e}")
                session.rollback()

    def _populate_default_categories(self):
        """Adds default expense and income categories if none exist."""
        with self._get_session() as session:
            try:
                # Check for existing default categories (user_id IS NULL)
                count = session.execute(
                    select(func.count(Category.category_id)).where(
                        Category.user_id == None
                    )  # noqa E711
                ).scalar_one_or_none()

                if count is None or count == 0:
                    default_categories = [
                        # Expenses
                        Category(
                            user_id=None,
                            name="Продукты",
                            type=TransactionType.expense,
                            icon="shopping_cart",
                        ),
                        Category(
                            user_id=None,
                            name="Транспорт",
                            type=TransactionType.expense,
                            icon="directions_bus",
                        ),
                        Category(
                            user_id=None,
                            name="Жилье",
                            type=TransactionType.expense,
                            icon="home",
                        ),
                        Category(
                            user_id=None,
                            name="Кафе и рестораны",
                            type=TransactionType.expense,
                            icon="restaurant",
                        ),
                        Category(
                            user_id=None,
                            name="Развлечения",
                            type=TransactionType.expense,
                            icon="local_movies",
                        ),
                        Category(
                            user_id=None,
                            name="Одежда",
                            type=TransactionType.expense,
                            icon="checkroom",
                        ),
                        Category(
                            user_id=None,
                            name="Здоровье",
                            type=TransactionType.expense,
                            icon="local_hospital",
                        ),
                        Category(
                            user_id=None,
                            name="Подарки",
                            type=TransactionType.expense,
                            icon="card_giftcard",
                        ),
                        Category(
                            user_id=None,
                            name="Другое (Расходы)",
                            type=TransactionType.expense,
                            icon="category",
                        ),
                        # Income
                        Category(
                            user_id=None,
                            name="Зарплата",
                            type=TransactionType.income,
                            icon="work",
                        ),
                        Category(
                            user_id=None,
                            name="Подарки",
                            type=TransactionType.income,
                            icon="card_giftcard",
                        ),
                        Category(
                            user_id=None,
                            name="Инвестиции",
                            type=TransactionType.income,
                            icon="trending_up",
                        ),
                        Category(
                            user_id=None,
                            name="Другое (Доходы)",
                            type=TransactionType.income,
                            icon="category",
                        ),
                    ]
                    session.add_all(default_categories)
                    session.commit()
                    print("Default categories added.")
                # else:
                #     print("Default categories already exist.")
            except Exception as e:
                print(f"Error populating default categories: {e}")
                session.rollback()

    # === User Management ===

    def add_user(self, username, email, password):
        """Adds a new user to the database."""
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        with self._get_session() as session:
            try:
                session.add(new_user)
                session.commit()
                print(f"User '{username}' added successfully.")
                return True
            except (
                Exception
            ) as e:  # Catch specific exceptions like IntegrityError later
                print(f"Error adding user '{username}': {e}")
                session.rollback()
                return False

    def verify_user(self, identifier, password):
        """Verifies user credentials by username or email."""
        with self._get_session() as session:
            try:
                stmt = select(User).where(
                    or_(User.username == identifier, User.email == identifier)
                )
                user = session.execute(stmt).scalar_one_or_none()

                if user and check_password_hash(user.password_hash, password):
                    # Return user data as a dictionary-like object (Row) or map to dict
                    # Using __dict__ might include SQLAlchemy internal state, be careful
                    # A safer approach is to explicitly create a dict
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,  # Return enum value
                        # Add other fields as needed, but avoid password_hash
                    }
                return None
            except Exception as e:
                print(f"Error verifying user '{identifier}': {e}")
                return None

    # === Session Management ===

    def create_session(self, user_id, duration_days=30):
        """Creates a persistent session token for a user."""
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
        """Retrieves user information based on a valid session token."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Session)
                    .where(
                        Session.token == token,
                        Session.expires_at > datetime.datetime.utcnow(),
                    )
                    .options(joinedload(Session.user))
                )  # Eager load user data

                valid_session = session.execute(stmt).scalar_one_or_none()

                if valid_session and valid_session.user:
                    user = valid_session.user
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,
                    }
                # Optional: Clean up expired sessions here or in a separate task
                # if valid_session is None:
                #     self.delete_session(token) # Delete if found but expired

                return None
            except Exception as e:
                print(f"Error validating session token '{token[:8]}...': {e}")
                return None

    def delete_session(self, token):
        """Deletes a session token (logout)."""
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

    # === Currency Management ===

    def get_currencies(self):
        """Retrieves all available currencies."""
        with self._get_session() as session:
            try:
                stmt = select(Currency).order_by(Currency.code)
                currencies = session.execute(stmt).scalars().all()
                # Convert to list of dictionaries
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

    # === Account Management ===

    def get_accounts_by_user(self, user_id):
        """Retrieves all accounts for a specific user, including currency info."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Account)
                    .where(Account.user_id == user_id)
                    .options(joinedload(Account.currency))
                    .order_by(Account.name)
                )  # Eager load currency

                accounts = session.execute(stmt).scalars().all()
                # Convert to list of dictionaries
                return [
                    {
                        "account_id": acc.account_id,
                        "user_id": acc.user_id,
                        "name": acc.name,
                        "balance": acc.balance,
                        "currency_id": acc.currency_id,
                        "description": acc.description,
                        "icon": acc.icon,
                        "currency_code": acc.currency.code,  # Add currency details
                        "currency_symbol": acc.currency.symbol,
                    }
                    for acc in accounts
                ]
            except Exception as e:
                print(f"Error retrieving accounts for user_id {user_id}: {e}")
                return []

    def get_account_by_id(self, account_id, user_id):
        """Retrieves a specific account by its ID, ensuring it belongs to the user."""
        with self._get_session() as session:
            try:
                stmt = (
                    select(Account)
                    .where(Account.account_id == account_id, Account.user_id == user_id)
                    .options(joinedload(Account.currency))
                )  # Eager load currency

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
                print(
                    f"Error retrieving account ID {account_id} for user_id {user_id}: {e}"
                )
                return None

    def add_account(self, user_id, name, balance, currency_id, description, icon):
        """Adds a new account for the user."""
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
                return (
                    True,
                    "Account added successfully.",
                )  # Return tuple (success, message)
            except Exception as e:
                print(f"Error adding account '{name}' for user_id {user_id}: {e}")
                session.rollback()
                return False, f"Database error: {e}"

    def update_account(
        self, account_id, user_id, name, balance, currency_id, description, icon
    ):
        """Updates an existing account, verifying ownership."""
        with self._get_session() as session:
            try:
                # Find the account first to ensure it exists and belongs to the user
                stmt_select = select(Account).where(
                    Account.account_id == account_id, Account.user_id == user_id
                )
                account_to_update = session.execute(stmt_select).scalar_one_or_none()

                if not account_to_update:
                    print(
                        f"Account ID {account_id} not found or does not belong to user_id {user_id}."
                    )
                    return False, "Account not found or access denied."

                # Update the account fields
                account_to_update.name = name
                account_to_update.balance = balance
                account_to_update.currency_id = currency_id
                account_to_update.description = description
                account_to_update.icon = icon

                # Alternative using update statement (less ORM-like but potentially more efficient)
                # stmt_update = update(Account).where(
                #     Account.account_id == account_id,
                #     Account.user_id == user_id
                # ).values(
                #     name=name,
                #     balance=balance,
                #     currency_id=currency_id,
                #     description=description,
                #     icon=icon
                # )
                # result = session.execute(stmt_update)

                session.commit()
                print(
                    f"Account ID {account_id} updated successfully for user_id {user_id}."
                )
                return True, "Account updated successfully."

                # if result.rowcount == 0: # Check if update statement affected rows
                #     print(f"Account ID {account_id} not found or does not belong to user_id {user_id}. No update performed.")
                #     session.rollback() # Rollback if update didn't happen (though select should prevent this)
                #     return False, "Account not found or access denied."
                # else:
                #     session.commit()
                #     print(f"Account ID {account_id} updated successfully for user_id {user_id}.")
                #     return True, "Account updated successfully."

            except Exception as e:
                print(
                    f"Error updating account ID {account_id} for user_id {user_id}: {e}"
                )
                session.rollback()
                return False, f"Database error: {e}"

    # === Category Management ===

    def get_categories_by_user_and_type(self, user_id, category_type: TransactionType):
        """
        Retrieves categories for a user by type (expense/income),
        including default categories (user_id IS NULL).
        """
        if not isinstance(category_type, TransactionType):
            try:
                category_type = TransactionType(
                    category_type
                )  # Convert string to enum if needed
            except ValueError:
                print(f"Invalid category type provided: {category_type}")
                return []

        with self._get_session() as session:
            try:
                stmt = (
                    select(Category)
                    .where(
                        or_(
                            Category.user_id == user_id, Category.user_id == None
                        ),  # noqa E711
                        Category.type == category_type,
                    )
                    .order_by(Category.user_id.desc().nullslast(), Category.name)
                )  # Show user categories first

                categories = session.execute(stmt).scalars().all()
                return [
                    {
                        "category_id": cat.category_id,
                        "user_id": cat.user_id,
                        "name": cat.name,
                        "type": cat.type.value,  # Return enum value
                        "icon": cat.icon,
                    }
                    for cat in categories
                ]
            except Exception as e:
                print(
                    f"Error retrieving categories for user {user_id}, type {category_type.value}: {e}"
                )
                return []

    # === Transaction Management ===

    def add_transaction(
        self,
        account_id,
        category_id,
        amount,
        transaction_date,
        description,
        transaction_type: TransactionType,
    ):
        """
        Adds a new transaction and updates the corresponding account balance atomically.
        Returns (True, "Success message") or (False, "Error message").
        """
        if not isinstance(transaction_type, TransactionType):
            try:
                transaction_type = TransactionType(
                    transaction_type
                )  # Convert string to enum if needed
            except ValueError:
                return False, "Invalid transaction type."

        if amount <= 0:
            return False, "Amount must be positive."

        # Ensure transaction_date is a datetime object if passed as string
        if isinstance(transaction_date, str):
            try:
                # Adjust format if needed (e.g., '%Y-%m-%d %H:%M:%S')
                # Assuming ISO format from the previous code
                transaction_date = datetime.datetime.fromisoformat(
                    transaction_date.replace(" ", "T")
                )
            except ValueError as e:
                print(
                    f"Error parsing transaction date string '{transaction_date}': {e}"
                )
                return False, "Invalid date format."
        elif not isinstance(transaction_date, datetime.datetime):
            return False, "Invalid transaction date type."

        with self._get_session() as session:
            try:
                # Start a transaction block (though SQLAlchemy sessions often manage this implicitly)
                # Explicit begin() can be used if needed for complex scenarios or specific isolation levels
                # session.begin()

                # 1. Fetch the account to update its balance
                account_to_update = session.get(Account, account_id)
                if not account_to_update:
                    raise ValueError(f"Account with ID {account_id} not found.")

                # 2. Fetch the category to ensure it exists (optional, FK constraint handles this)
                category_exists = session.get(Category, category_id)
                if not category_exists:
                    raise ValueError(f"Category with ID {category_id} not found.")

                # 3. Create the new transaction object
                new_transaction = Transaction(
                    account_id=account_id,
                    category_id=category_id,
                    amount=amount,
                    transaction_date=transaction_date,
                    description=description,
                    type=transaction_type,
                )
                session.add(new_transaction)

                # 4. Update the account balance
                if transaction_type == TransactionType.income:
                    account_to_update.balance += amount
                else:  # expense
                    account_to_update.balance -= amount

                # Flush to send changes to DB and get transaction_id if needed before commit
                # session.flush()
                # transaction_id = new_transaction.transaction_id

                # 5. Commit the session (saves transaction and account update atomically)
                session.commit()

                print(
                    f"Transaction ({transaction_type.value}) of {amount} added for account ID {account_id}. New balance: {account_to_update.balance}"
                )
                return True, "Transaction added successfully."

            except (
                Exception
            ) as e:  # Catch specific errors like IntegrityError, ValueError
                session.rollback()  # Roll back changes on any error
                print(f"Error adding transaction or updating balance: {e}")
                # Provide more specific user feedback if possible
                if "violates foreign key constraint" in str(e):
                    if "fk_transactions_account_id_accounts" in str(e):
                        return (
                            False,
                            f"Error: Account with ID {account_id} does not exist.",
                        )
                    elif "fk_transactions_category_id_categories" in str(e):
                        return (
                            False,
                            f"Error: Category with ID {category_id} does not exist.",
                        )
                elif isinstance(e, ValueError):  # Catch our explicit ValueErrors
                    return False, str(e)
                else:
                    return False, f"Database error: {e}"

    def get_transactions_by_account(self, account_id, user_id, limit=50, offset=0):
        """Gets recent transactions for a specific account owned by the user."""
        with self._get_session() as session:
            try:
                # First, verify the account belongs to the user
                account = session.execute(
                    select(Account.account_id).where(
                        Account.account_id == account_id, Account.user_id == user_id
                    )
                ).scalar_one_or_none()

                if account is None:
                    print(
                        f"Access denied or account {account_id} not found for user {user_id}."
                    )
                    return []

                # Fetch transactions, joining with Category for name/icon
                stmt = (
                    select(Transaction)
                    .where(Transaction.account_id == account_id)
                    .options(joinedload(Transaction.category))
                    .order_by(
                        Transaction.transaction_date.desc(),
                        Transaction.transaction_id.desc(),
                    )
                    .limit(limit)
                    .offset(offset)
                )

                transactions = session.execute(stmt).scalars().all()

                # Convert to list of dictionaries for Flet compatibility
                return [
                    {
                        "transaction_id": t.transaction_id,
                        "account_id": t.account_id,
                        "category_id": t.category_id,
                        "amount": t.amount,
                        "transaction_date": t.transaction_date.isoformat(),  # Format date as string
                        "description": t.description,
                        "type": t.type.value,
                        # Include category details (handle if category was deleted)
                        "category_name": (
                            t.category.name if t.category else "Deleted Category"
                        ),
                        "category_icon": t.category.icon if t.category else None,
                    }
                    for t in transactions
                ]
            except Exception as e:
                print(f"Error retrieving transactions for account {account_id}: {e}")
                return []

    # --- Placeholder methods for Update/Delete Transaction ---
    # These are complex because they require adjusting account balances correctly,
    # potentially involving fetching the *old* transaction amount.

    def update_transaction(self, transaction_id, user_id, **kwargs):
        """
        Placeholder for updating a transaction.
        Requires careful handling of balance adjustments.
        """
        print(
            f"Warning: update_transaction (ID: {transaction_id}) not fully implemented."
        )
        # 1. Verify transaction exists and belongs to user (via account).
        # 2. Get old transaction amount.
        # 3. Update transaction details.
        # 4. Calculate balance difference (new_amount - old_amount, considering type changes).
        # 5. Update account balance.
        # 6. Commit atomically.
        return False, "Update transaction functionality not yet implemented."

    def delete_transaction(self, transaction_id, user_id):
        """
        Placeholder for deleting a transaction.
        Requires careful handling of balance adjustments.
        """
        print(
            f"Warning: delete_transaction (ID: {transaction_id}) not fully implemented."
        )
        # 1. Verify transaction exists and belongs to user (via account).
        # 2. Get transaction amount and type.
        # 3. Delete the transaction.
        # 4. Adjust account balance (add if expense, subtract if income).
        # 5. Commit atomically.
        return False, "Delete transaction functionality not yet implemented."


# --- Instance Creation ---
# Create a single instance of the DatabaseManager for the application to use
db_manager = DatabaseManager()
print("DatabaseManager instance created and initialized.")
