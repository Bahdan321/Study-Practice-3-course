from sqlalchemy import Integer, String, Column, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin" # Example if you need roles

class User(Base):
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, server_default='user') # Use Enum

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan") # User-specific categories

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"