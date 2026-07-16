"""
Tests for app/crud.py and app/services/user_service.py -- exercised
directly (no HTTP), so failures here point straight at the business logic
rather than routing/serialization concerns. See test_api.py for the
end-to-end HTTP tests.
"""

import pytest
from fastapi import HTTPException

from app import crud, schemas
from app.database import SessionLocal
from app.services import user_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ------------------------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------------------------
def test_hash_password_does_not_store_plaintext():
    hashed = user_service.hash_password("S3curePass1")
    assert hashed != "S3curePass1"
    assert hashed.startswith("$2b$")  # bcrypt hash prefix


def test_verify_password_round_trip():
    hashed = user_service.hash_password("S3curePass1")
    assert user_service.verify_password("S3curePass1", hashed) is True
    assert user_service.verify_password("WrongPassword1", hashed) is False


# ------------------------------------------------------------------------------------
# create_user
# ------------------------------------------------------------------------------------
def test_create_user_persists_and_hashes_password(db_session, sample_user_payload):
    user_in = schemas.UserCreate(**sample_user_payload)
    user = user_service.create_user(db_session, user_in)

    assert user.id is not None
    assert user.username == sample_user_payload["username"]
    assert user.email == sample_user_payload["email"]
    assert user.hashed_password != sample_user_payload["password"]
    assert user_service.verify_password(sample_user_payload["password"], user.hashed_password)


def test_create_user_duplicate_email_raises_409(db_session, sample_user_payload):
    user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))

    duplicate = {**sample_user_payload, "username": "someoneelse"}
    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(db_session, schemas.UserCreate(**duplicate))
    assert exc_info.value.status_code == 409


def test_create_user_duplicate_username_raises_409(db_session, sample_user_payload):
    user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))

    duplicate = {**sample_user_payload, "email": "someoneelse@example.com"}
    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(db_session, schemas.UserCreate(**duplicate))
    assert exc_info.value.status_code == 409


# ------------------------------------------------------------------------------------
# get_user_or_404 / list_users
# ------------------------------------------------------------------------------------
def test_get_user_or_404_raises_for_missing_user(db_session):
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_or_404(db_session, 9999)
    assert exc_info.value.status_code == 404


def test_list_users_respects_skip_and_limit(db_session, sample_user_payload):
    for i in range(5):
        payload = {
            **sample_user_payload,
            "username": f"user{i}",
            "email": f"user{i}@example.com",
        }
        user_service.create_user(db_session, schemas.UserCreate(**payload))

    page = user_service.list_users(db_session, skip=0, limit=2)
    assert len(page) == 2

    all_users = user_service.list_users(db_session, skip=0, limit=100)
    assert len(all_users) == 5


# ------------------------------------------------------------------------------------
# update_user
# ------------------------------------------------------------------------------------
def test_update_user_partial_update_only_changes_given_fields(db_session, sample_user_payload):
    user = user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))

    updated = user_service.update_user(
        db_session, user.id, schemas.UserUpdate(full_name="New Name")
    )

    assert updated.full_name == "New Name"
    assert updated.email == sample_user_payload["email"]  # unchanged
    assert updated.username == sample_user_payload["username"]  # unchanged


def test_update_user_password_is_rehashed(db_session, sample_user_payload):
    user = user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))
    old_hash = user.hashed_password

    updated = user_service.update_user(
        db_session, user.id, schemas.UserUpdate(password="NewPassword1")
    )

    assert updated.hashed_password != old_hash
    assert user_service.verify_password("NewPassword1", updated.hashed_password)


def test_update_user_to_taken_email_raises_409(db_session, sample_user_payload):
    user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))
    second_payload = {
        **sample_user_payload,
        "username": "second",
        "email": "second@example.com",
    }
    second_user = user_service.create_user(db_session, schemas.UserCreate(**second_payload))

    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user(
            db_session, second_user.id, schemas.UserUpdate(email=sample_user_payload["email"])
        )
    assert exc_info.value.status_code == 409


def test_update_missing_user_raises_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user(db_session, 9999, schemas.UserUpdate(full_name="Ghost"))
    assert exc_info.value.status_code == 404


# ------------------------------------------------------------------------------------
# delete_user
# ------------------------------------------------------------------------------------
def test_delete_user_removes_the_record(db_session, sample_user_payload):
    user = user_service.create_user(db_session, schemas.UserCreate(**sample_user_payload))

    user_service.delete_user(db_session, user.id)

    assert crud.get_user(db_session, user.id) is None


def test_delete_missing_user_raises_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        user_service.delete_user(db_session, 9999)
    assert exc_info.value.status_code == 404
