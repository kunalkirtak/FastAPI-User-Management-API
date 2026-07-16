"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base
from app.utils.helpers import utcnow


class User(Base):
    """Database representation of an application user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)

    # Never store plain-text passwords -- only the bcrypt hash is persisted.
    # See app/services/user_service.py for hashing/verification logic.
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    # `utcnow` (app/utils/helpers.py) returns a timezone-aware datetime --
    # prefer it over the deprecated `datetime.datetime.utcnow()`.
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"
