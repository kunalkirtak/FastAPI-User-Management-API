"""
User routes.

Thin HTTP layer -- request/response handling only. All business logic lives
in `app/services/user_service.py`.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.dependencies import PaginationParams, get_pagination_params
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    - **username**: 3-50 characters, letters/numbers/underscores only
    - **email**: must be a valid, unique email address
    - **password**: 8+ characters, at least one letter and one digit

    Returns **409 Conflict** if the email or username is already taken.
    """
    return user_service.create_user(db, user_in)


@router.get(
    "",
    response_model=List[schemas.UserResponse],
    summary="List users",
)
def list_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    """
    Return a page of users, ordered by id.

    Basic offset pagination (`skip`/`limit`) is included out of the box.
    Search, sorting, and filtering are tracked as future enhancements.
    """
    return user_service.list_users(db, skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Get a single user",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Return a single user by id. Returns **404** if it doesn't exist."""
    return user_service.get_user_or_404(db, user_id)


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Update a user",
)
def update_user(user_id: int, user_in: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    Update one or more fields of an existing user (partial update -- only
    fields present in the request body are changed).

    Returns **404** if the user doesn't exist, **409** if the new email or
    username is already taken by another user.
    """
    return user_service.update_user(db, user_id, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by id. Returns **404** if it doesn't exist."""
    user_service.delete_user(db, user_id)
    return None
