"""Database connection and session factory using SQLAlchemy 2.0 and psycopg 3.

Provides engine factory, session makers, and SQL file execution helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from readmission.config import DATABASE_URL

_engine: sa.Engine | None = None


def get_engine(url: str | None = None, echo: bool = False) -> sa.Engine:
    """Return a cached or newly created SQLAlchemy engine."""
    global _engine
    target_url = url or DATABASE_URL
    if _engine is None or url is not None:
        engine = sa.create_engine(
            target_url,
            echo=echo,
            pool_pre_ping=True,
            future=True,
        )
        if url is None:
            _engine = engine
        return engine
    return _engine


def get_session_factory(engine: sa.Engine | None = None) -> sessionmaker[Session]:
    """Return a configured sessionmaker."""
    eng = engine or get_engine()
    return sessionmaker(bind=eng, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session(engine: sa.Engine | None = None) -> Generator[Session, None, None]:
    """Yield a database session for context managers or FastAPI dependency injection."""
    factory = get_session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_connection(engine: sa.Engine | None = None) -> bool:
    """Test whether the database is reachable."""
    eng = engine or get_engine()
    try:
        with eng.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        return True
    except Exception:
        return False


def execute_sql_file(file_path: Path | str, engine: sa.Engine | None = None) -> None:
    """Execute raw SQL statements from a file using a connection."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    sql_text = path.read_text(encoding="utf-8")
    eng = engine or get_engine()
    with eng.begin() as conn:
        conn.execute(sa.text(sql_text))
