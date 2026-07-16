"""
Database setup.

Defines the SQLAlchemy engine, session factory, declarative base, and the
`get_db` FastAPI dependency used by routers/services to obtain a scoped
database session.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


def _ensure_sqlite_directory_exists(database_url: str) -> None:
    """
    For a file-based SQLite URL (e.g. `sqlite:///./data/app.db`), make sure
    the parent directory exists before SQLAlchemy tries to open the file --
    sqlite3 raises "unable to open database file" otherwise. This is what
    lets DATABASE_URL point into a subdirectory (like the `data/` folder a
    Docker volume mounts onto) with zero manual setup, in both local dev
    and containers.
    """
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or not url.database:
        return
    if url.database == ":memory:":
        return
    Path(url.database).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory_exists(settings.DATABASE_URL)

# SQLite needs `check_same_thread=False` because FastAPI can use a request
# in a different thread than the one that created the connection. Other
# databases (PostgreSQL, MySQL, ...) don't need this.
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees it is
    closed after the request finishes -- even if an exception is raised.

    Usage:
        @router.get("/users")
        def list_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
