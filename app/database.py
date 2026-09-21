from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# WHY: SQLite stores data locally in a file. 'sqlite:///./sql_app.db' creates this file in your project root.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# WHY: The engine is the starting point for any SQLAlchemy application; it manages the connection pool.
# (check_same_thread=False is specifically required for SQLite in FastAPI to allow multi-threaded requests)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# WHY: SessionLocal will be our actual database session factory. Each request gets its own independent session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# WHY: We use this Base class to create our database models (Python classes that map to SQL tables).
Base = declarative_base()

from app.models.product import ProductModel


# Dependency to get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensures connection leaks never happen!

