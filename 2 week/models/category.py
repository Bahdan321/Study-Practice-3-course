from sqlalchemy import Integer, String, Column, ForeignKey, Enum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
import enum

class TransactionType(str, enum.Enum):
    expense = "expense"
    income = "income"

class Category(Base):
    # Explicit table name needed because auto-generation makes it 'categorys'
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    # user_id is nullable for default categories
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    type = Column(Enum(TransactionType), nullable=False) # 'expense' or 'income'
    icon = Column(String, nullable=True) # Optional icon name

    # Relationships
    user = relationship("User", back_populates="categories") # Link to user for custom categories
    transactions = relationship("Transaction", back_populates="category") # Don't cascade delete from here

    # Constraint: Prevent duplicate categories per user/type (including NULL user_id for defaults)
    # Note: Handling NULLs in UNIQUE constraints varies by DB. PostgreSQL treats NULLs as distinct.
    # If you need NULLs to be treated as equal for uniqueness, consider alternative approaches or triggers.
    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'type', name='uq_user_category_name_type'),
    )

    def __repr__(self):
        return f"<Category(category_id={self.category_id}, name='{self.name}', type='{self.type}', user_id={self.user_id})>"