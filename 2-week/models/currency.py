from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from .base import Base

class Currency(Base):
    # Explicit table name needed because auto-generation makes it 'currencys'
    __tablename__ = "currencies"

    currency_id = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False, unique=True) # e.g., USD, EUR
    name = Column(String, nullable=False) # e.g., US Dollar
    symbol = Column(String(5), nullable=False) # e.g., $

    # Relationship (if accounts reference currency)
    accounts = relationship("Account", back_populates="currency")

    def __repr__(self):
        return f"<Currency(currency_id={self.currency_id}, code='{self.code}')>"