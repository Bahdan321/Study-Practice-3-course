from sqlalchemy import Integer, String, Column, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from .base import Base

class Account(Base):
    account_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0, server_default='0.0')
    currency_id = Column(Integer, ForeignKey("currencies.currency_id", ondelete="NO ACTION"), nullable=False) # Protect currency deletion
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True) # Store icon name

    # Relationships
    user = relationship("User", back_populates="accounts")
    currency = relationship("Currency", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account(account_id={self.account_id}, name='{self.name}', user_id={self.user_id})>"