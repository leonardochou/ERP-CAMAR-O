"""Configuração da sessão de banco de dados e engine SQLAlchemy."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Normalização da URL para suportar PostgreSQL nativo e pooling de nuvem
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Ajuste para SQLite vs PostgreSQL
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
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
