from typing import Generator
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
from db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
