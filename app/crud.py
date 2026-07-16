"""
CRUD layer.

Pure database access functions -- no HTTP concerns (no status codes, no
exceptions tied to the API) live here. This layer only knows how to talk
to the database via SQLAlchemy. Business rules (duplicate checks, 404s,
password hashing) live one level up, in `app/services/user_service.py`.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app import schemas
from app.models import User


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Fetch a single user by primary key, or None if it doesn't exist."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Return a page of users ordered by id (basic offset pagination)."""
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str) -> User:
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    db_user: User,
    user_in: schemas.UserUpdate,
    hashed_password: Optional[str] = None,
) -> User:
    """
    Apply only the fields that were actually supplied in `user_in` (partial
    update). `password` is excluded from the generic loop since it must be
    hashed first -- the caller passes the already-hashed value separately.
    """
    update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        setattr(db_user, field, value)

    if hashed_password is not None:
        db_user.hashed_password = hashed_password

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    db.delete(db_user)
    db.commit()
