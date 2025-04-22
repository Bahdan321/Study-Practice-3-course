from sqlalchemy import Integer, String, Column, ForeignKey, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from .base import Base
from .category import TransactionType # Import the enum

class Transaction(Base):
    transaction_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="RESTRICT"), nullable=False) # Prevent category deletion if used
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TransactionType), nullable=False) # Matches category type

    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, type='{self.type}', amount={self.amount}, account_id={self.account_id})>"