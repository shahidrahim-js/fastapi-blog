# Database Configuration file: This file handles the connection string and creates a session factory
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine 
from sqlalchemy.orm import DeclarativeBase

BASE_DIR = Path(__file__).resolve().parent

# SQLite database file path
# database url tells sqlalchemy where to connect.
# ./ is current directory. blog.db is the file name (this file will created automatically)
# Note: When we switch to PostgreSQL this connection string should be one and only chnages. Rest of the code will stay the same.
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR/'blog.db'}"

# Create engine that connection to the database
# check_same_thread=False is required for SQLite to work smoothly with FastAPI's async loops.
engine = create_async_engine( 
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False}
)

# Create a Session factory for handling requests
# This is standard FastAPI pattern.
AsyncSessionLocal = async_sessionmaker(
  engine,
  class_=AsyncSession,
  expire_on_commit=False  # recommend for async. It prevent issues with expired object after a commit. 
)

#Base class for SQLAlchemy models
class Base(DeclarativeBase):
  pass

# Dependency to inject the database session into api route functions (in main.py)
async def get_db():
  async with AsyncSessionLocal() as session:
    yield session