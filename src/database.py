import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database URL from environment variable or SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Configure SQLite-specific args if using SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass

def init_db():
    """Initialize database tables."""
    import src.models  # Register ORM models before create_all
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Provide a database session context, ensuring tables exist."""
    init_db()
    return SessionLocal()
