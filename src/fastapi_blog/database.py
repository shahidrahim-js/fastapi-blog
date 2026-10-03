# Database Configuration file: This file handles the connection string and creates a session factory
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite database file path
# database url tells sqlalchemy where to connect.
# ./ is current directory. blog.db is the file name (this file will created automatically)
# Note: When we switch to PostgreSQL this connection string should be one and only chnages. Rest of the code will stay the same.
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# Create engine that connection to the database
# check_same_thread=False is required for SQLite to work smoothly with FastAPI's async loops.
engine = create_engine( 
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False}
)

# Create a session factory for handling requests
# Setting autocommit and autoflush to False because we want to control when chnages are committed
# This is standard FastAPI pattern.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base class for SQLAlchemy models
class Base(DeclarativeBase):
  pass

# Dependency function to inject the database session into route functions
def get_db():
  with SessionLocal() as db:
    yield db