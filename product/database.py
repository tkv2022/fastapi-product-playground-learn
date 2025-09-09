from sqlalchemy import create_engine,engine  # create_engine: factory to produce a DB engine; `engine` is a submodule (not needed here)
from sqlalchemy.ext.declarative import declarative_base  # helper to create a base class for model classes
from sqlalchemy.orm import sessionmaker  # factory for creating Session classes bound to an engine

# Database URL for SQLAlchemy. Using SQLite stored in the project file `product.db`.
# The format "sqlite:///./product.db" means a relative path in the current working directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./product.db"

# Create the SQLAlchemy Engine which manages connections to the DB.
# connect_args={'check_same_thread': False} is required for SQLite when using the same
# connection across multiple threads (typical for web apps using threaded servers).
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# sessionmaker produces a Session class bound to our engine. Use SessionLocal() to get
# a new session instance. autocommit and autoflush are disabled for explicit control.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base is the declarative base class that our ORM models should inherit from.
# It keeps a catalog of classes and tables for SQLAlchemy's ORM mappings.
Base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()