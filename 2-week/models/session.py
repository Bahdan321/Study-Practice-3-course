from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class Session(Base):
    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id}, token='{self.token[:8]}...')>"

    @property
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at