"""
Tests for app/database.py -- the SQLAlchemy engine/session setup itself,
independent of any specific model's business logic.
"""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db


def test_users_table_is_registered_on_metadata():
    """Importing app.models (done in app/main.py) should register `users`."""
    assert "users" in Base.metadata.tables


def test_users_table_exists_after_create_all():
    inspector = inspect(engine)
    assert "users" in inspector.get_table_names()


def test_get_db_yields_a_working_session_and_closes_it():
    gen = get_db()
    db = next(gen)

    assert isinstance(db, Session)
    # A trivial query proves the session actually has a live connection.
    assert db.execute(text("SELECT 1")).scalar() == 1

    # Exhausting the generator runs the `finally: db.close()` branch in
    # get_db(). A closed session raises on next use.
    with pytest.raises(StopIteration):
        next(gen)


def test_sessionlocal_produces_independent_sessions():
    session_a = SessionLocal()
    session_b = SessionLocal()
    try:
        assert session_a is not session_b
    finally:
        session_a.close()
        session_b.close()
