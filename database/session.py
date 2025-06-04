from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_database_url

engine = create_engine(get_database_url())
SessionLocal = sessionmaker(bind=engine)

# FastAPI dependency for DB session
from typing import Generator

def get_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 