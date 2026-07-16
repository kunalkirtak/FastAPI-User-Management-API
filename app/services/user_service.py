"""
User service.

Business logic for the User resource: password hashing, duplicate
email/username checks, and translating "not found" into the appropriate
HTTP error. Routers stay thin and simply delegate here; this layer is what
makes the routers easy to test and the business rules easy to find.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------------------------------------------------------------------
# Password helpers
# ------------------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kept here for future use, e.g. by a login/auth endpoint (bonus feature)."""
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------------------------------------------------
# Lookups
# ------------------------------------------------------------------------------------
def get_user_or_404(db: Session, user_id: int) -> User:
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return crud.get_users(db, skip=skip, limit=limit)


# ------------------------------------------------------------------------------------
# Create
# ------------------------------------------------------------------------------------
def create_user(db: Session, user_in: schemas.UserCreate) -> User:
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists",
        )

    hashed_password = hash_password(user_in.password)
    return crud.create_user(db, user_in, hashed_password)


# ------------------------------------------------------------------------------------
# Update
# ------------------------------------------------------------------------------------
def update_user(db: Session, user_id: int, user_in: schemas.UserUpdate) -> User:
    db_user = get_user_or_404(db, user_id)

    if user_in.email and user_in.email != db_user.email:
        if crud.get_user_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

    if user_in.username and user_in.username != db_user.username:
        if crud.get_user_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this username already exists",
            )

    hashed_password: Optional[str] = (
        hash_password(user_in.password) if user_in.password else None
    )
    return crud.update_user(db, db_user, user_in, hashed_password=hashed_password)


# ------------------------------------------------------------------------------------
# Delete
# ------------------------------------------------------------------------------------
def delete_user(db: Session, user_id: int) -> None:
    db_user = get_user_or_404(db, user_id)
    crud.delete_user(db, db_user)
