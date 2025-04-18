from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

# Optional: Define naming conventions for constraints
# Helps keep constraint names consistent across different DBs
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    metadata = metadata

    # Optional: Automatically generate __tablename__
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Converts class name like 'UserAccount' to table name 'user_accounts'
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Ensure plural form for table names (simple 's' suffix)
        if not name.endswith('s'):
             name += 's'
        # Handle specific cases like 'currency' -> 'currencies'
        if name == 'currencys':
            name = 'currencies'
        if name == 'categorys':
            name = 'categories'
        return name