from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from core.config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
SQLAlchemyInstrumentor().instrument(
    engine=engine
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
