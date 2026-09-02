from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"

# SQLite engine configured for multi-threaded FastAPI / NiceGUI context
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

def init_db():
    """Initialize database tables."""
    import src.models  # Register SQLAlchemy ORM models with Base.metadata
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Provide a database session context, ensuring tables exist."""
    init_db()
    return SessionLocal()
