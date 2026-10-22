"""Configurações globais e fixtures para a suíte de testes do backend."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importa todos os modelos para garantir registro completo no Base.metadata
import app.models
from app.core.database import Base, get_db
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.core.tenant import (
    FAZENDA_PADRAO_ID,
    FAZENDA_HAKKA_ID,
)
from app.core.init_db import FAZENDAS_SEED, VIVEIROS_SEED
from app.main import app

# Banco de dados de teste isolado em memória com StaticPool para compartilhar a mesma instância em memória entre threads
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria uma base de dados limpa em memória com seed completo para cada teste."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    # Semeia as fazendas padrão no banco de teste
    for f_data in FAZENDAS_SEED:
        fazenda = Fazenda(**f_data)
        session.add(fazenda)
    session.commit()

    # Semeia os 15 viveiros na Fazenda Arrendada
    for v_data in VIVEIROS_SEED:
        item = dict(v_data)
        item["fazenda_id"] = FAZENDA_PADRAO_ID
        viveiro = Viveiro(**item)
        session.add(viveiro)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def fazenda_arrendada(db_session):
    """Retorna a instância da Fazenda Arrendada ativa."""
    return db_session.query(Fazenda).filter(Fazenda.id == FAZENDA_PADRAO_ID).first()


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente HTTP do FastAPI configurado com o banco de testes em memória."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
