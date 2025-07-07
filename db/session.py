from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


# Criando um engine assíncrono com asyncpg
engine_psql = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI_PG),
    pool_pre_ping=True,
    future=True  # Habilita a API 2.0 do SQLAlchemy
)

# SQLAlchemyInstrumentor().instrument(engine=engine_psql)

# Criando a fábrica de sessões assíncronas
SessionLocal_psql = sessionmaker(
    bind=engine_psql,
    class_=AsyncSession,
    expire_on_commit=False
)


engine_212 = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI_212), pool_pre_ping=True)
SQLAlchemyInstrumentor().instrument(
    engine=engine_212
)
SessionLocal_212 = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_212)


engine_211 = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI_211), pool_pre_ping=True)
SQLAlchemyInstrumentor().instrument(
    engine=engine_211
)
SessionLocal_211 = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_211)
