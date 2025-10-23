import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session

from dotenv import load_dotenv

load_dotenv()

# Replace with your actual credentials and database name
DATABASE_URL = os.getenv("POSTGRES_URL") 

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes (optional, for use in routes)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()