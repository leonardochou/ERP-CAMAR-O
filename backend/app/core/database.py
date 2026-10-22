"""Configuração da sessão de banco de dados e engine SQLAlchemy."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Ajuste para SQLite vs PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM."""
    pass


def get_db() -> Generator:
    """Gerador de sessão de banco de dados para injeção de dependência nas rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
