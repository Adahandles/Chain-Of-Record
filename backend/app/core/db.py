# Database connection and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from typing import Generator
from .config import settings

# SQLAlchemy setup
engine = create_engine(
    str(settings.database_url),
    future=True,
    echo=settings.environment != "prod",  # Log SQL in development
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    future=True
)

Base = declarative_base()


def get_db() -> Generator:
    """
    Database dependency for FastAPI.
    Yields a database session and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    This should only be used in development.
    Production should use Alembic migrations.
    """
    if settings.is_development:
        Base.metadata.create_all(bind=engine)