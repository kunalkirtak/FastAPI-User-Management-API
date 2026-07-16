"""
Shared pytest fixtures.

The DATABASE_URL environment variable is set *before* anything from `app`
is imported, so the application's own engine (app.database.engine) points
at a throwaway SQLite file for the whole test session instead of the
developer's real app.db. No dependency-override plumbing is needed --
tests exercise the exact same `get_db` the app uses in production.
"""

import os
import tempfile

_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "fastapi_user_management_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("LOG_LEVEL", "WARNING")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_database():
    """Give every test a clean schema -- no leftover rows from the previous test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """A TestClient wired up to the full app, including startup/shutdown events."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_payload() -> dict:
    """A valid `UserCreate` payload, reused across tests to cut down on boilerplate."""
    return {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "password": "S3curePass1",
    }


def pytest_sessionfinish(session, exitstatus):
    """Remove the temp SQLite file used for this test run."""
    try:
        os.remove(_TEST_DB_PATH)
    except OSError:
        pass
