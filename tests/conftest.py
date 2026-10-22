"""Configuração e fixtures centrais da suíte de testes E2E do ERP CAMARÃO.

Fornece suporte Multi-Tenant (Fazenda Arrendada e Fazenda Hakka), banco SQLite isolado em memória
com StaticPool (compartilhado de forma thread-safe entre TestClient e fixtures),
sessões SQLAlchemy, caminhos autoritativos para os arquivos .xlsx reais e geradores de dados.
"""
import os
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Generator, Dict, Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Garante que o pacote backend/app seja importável
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.database import Base, get_db
import app.models
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.auditoria import AuditoriaPendencia
from app.models.despesca import DespescaVenda
from app.core.init_db import VIVEIROS_SEED
from app.core.tenant import FAZENDA_PADRAO_ID, FAZENDA_HAKKA_ID


# ==============================================================================
# CAMINHOS AUTORITATIVOS PARA AS PLANILHAS REAIS
# ==============================================================================
BASE_PROJETO = Path(__file__).resolve().parent.parent
MODELOS_DIR = BASE_PROJETO.parent / "MODELOS DE CONTROLE"

SPREADSHEET_PATHS = {
    "alimentacao": MODELOS_DIR / "Controle de alimentação e biometria" / "Controle_Alimentacao_e_Biometria.xlsx",
    "agua": MODELOS_DIR / "Controle de qualidade de agua" / "Controle_Qualidade_Agua.xlsx",
    "mapeamento": MODELOS_DIR / "Mapeamento dos viveiros" / "Mapeamento_e_Cadastro_dos_Viveiros.xlsx",
    "despesca": MODELOS_DIR / "Controle de despesca e vendas" / "Controle_de_Despesca_e_Vendas.xlsx",
}


@pytest.fixture(scope="session")
def spreadsheet_paths() -> Dict[str, Path]:
    """Retorna os caminhos dos modelos oficiais .xlsx da fazenda."""
    return SPREADSHEET_PATHS


# ==============================================================================
# FIXTURES DE BANCO DE DADOS ISOLADO (SQLite in-memory com StaticPool)
# ==============================================================================
@pytest.fixture(scope="function")
def db_engine():
    """Engine SQLite em memória thread-safe (StaticPool) isolado por teste."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session_factory(db_engine):
    """Fábrica de sessões conectada ao engine de teste em memória."""
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture(scope="function")
def db_session(session_factory) -> Generator[Session, None, None]:
    """Sessão SQLAlchemy limpa e isolada para cada função de teste com multi-tenant inicializado."""
    session = session_factory()
    try:
        # 1. Cria a Fazenda Padrão (Fazenda Arrendada - Ceará-Mirim/RN)
        fazenda_arrendada = Fazenda(
            id=FAZENDA_PADRAO_ID,
            codigo="FAZ_ARRENDADA",
            nome="Fazenda Arrendada",
            tipo_propriedade="arrendada",
            municipio_uf="Ceará-Mirim/RN",
            status="ativa",
        )
        session.add(fazenda_arrendada)

        # 2. Cria a Fazenda Futura Própria (Fazenda Hakka)
        fazenda_hakka = Fazenda(
            id=FAZENDA_HAKKA_ID,
            codigo="FAZ_HAKKA",
            nome="Fazenda Hakka",
            tipo_propriedade="propria",
            municipio_uf="Ceará-Mirim/RN",
            status="configuracao",
        )
        session.add(fazenda_hakka)
        session.flush()

        # 3. Semeia automaticamente os 15 viveiros reais da Fazenda Arrendada
        for v_data in VIVEIROS_SEED:
            dados = dict(v_data)
            dados["fazenda_id"] = fazenda_arrendada.id
            viveiro = Viveiro(**dados)
            session.add(viveiro)

        session.commit()
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def fazenda_padrao(db_session: Session) -> Fazenda:
    """Fixture que retorna a Fazenda Arrendada ativa."""
    fazenda = db_session.query(Fazenda).filter(Fazenda.codigo == "FAZ_ARRENDADA").first()
    assert fazenda is not None
    return fazenda


@pytest.fixture
def fazenda_hakka(db_session: Session) -> Fazenda:
    """Fixture que retorna a Fazenda Hakka própria em configuração."""
    fazenda = db_session.query(Fazenda).filter(Fazenda.codigo == "FAZ_HAKKA").first()
    assert fazenda is not None
    return fazenda


@pytest.fixture
def tenant_headers(fazenda_padrao: Fazenda) -> Dict[str, str]:
    """Headers HTTP padrão contendo o tenant da Fazenda Arrendada."""
    return {
        "X-Fazenda-Id": fazenda_padrao.id,
        "X-Fazenda-Codigo": fazenda_padrao.codigo,
    }


@pytest.fixture
def hakka_headers(fazenda_hakka: Fazenda) -> Dict[str, str]:
    """Headers HTTP direcionados à Fazenda Hakka."""
    return {
        "X-Fazenda-Id": fazenda_hakka.id,
        "X-Fazenda-Codigo": fazenda_hakka.codigo,
    }


# ==============================================================================
# FIXTURE DO CLIENTE HTTP DE TESTES (FASTAPI TESTCLIENT)
# ==============================================================================
@pytest.fixture
def client(session_factory, db_session: Session):
    """Cliente HTTP de teste conectado ao mesmo banco SQLite in-memory com StaticPool."""
    from fastapi.testclient import TestClient
    from app.main import app

    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==============================================================================
# ORÁCULO MATEMÁTICO ZOOTÉCNICO (Ground Truth Independente)
# ==============================================================================
class ZootecniaOracle:
    """Implementação canônica independente das fórmulas zootécnicas oficiais.

    Utilizada pelos testes como padrão-ouro (oráculo) para verificação
    de conformidade zootécnica sem viés de implementação.
    """

    @staticmethod
    def populacao(pls: int, sobrevivencia_pct: float) -> int:
        """População = PLs * (Sobrevivência / 100)"""
        if pls <= 0 or sobrevivencia_pct <= 0:
            return 0
        return int(round(pls * (sobrevivencia_pct / 100.0)))

    @staticmethod
    def biomassa_kg(populacao_viva: int, peso_medio_g: float) -> float:
        """Biomassa (kg) = (População * Peso Médio em gramas) / 1000"""
        if populacao_viva <= 0 or peso_medio_g <= 0:
            return 0.0
        return round((populacao_viva * peso_medio_g) / 1000.0, 2)

    @staticmethod
    def fca_parcial(racao_acumulada_kg: float, biomassa_kg: float) -> float:
        """FCA Parcial = Ração Acumulada / Biomassa Atual"""
        if biomassa_kg <= 0 or racao_acumulada_kg <= 0:
            return 0.0
        return round(racao_acumulada_kg / biomassa_kg, 2)

    @staticmethod
    def gmd(peso_atual: float, peso_ant: float, dias: int) -> float:
        """GMD (g/dia) = (Peso Atual - Peso Anterior) / Dias"""
        if dias <= 0:
            return 0.0
        return round((peso_atual - peso_ant) / dias, 2)

    @staticmethod
    def sobrevivencia_real(colhido_kg: float, peso_final_g: float, pls: int) -> float:
        """Sobrevivência Real (%) = ((Colhido * 1000 / Peso Final) / PLs) * 100"""
        if pls <= 0 or peso_final_g <= 0 or colhido_kg <= 0:
            return 0.0
        camaroes = (colhido_kg * 1000.0) / peso_final_g
        return round((camaroes / pls) * 100.0, 2)

    @staticmethod
    def fca_final(racao_total_kg: float, colhido_kg: float) -> float:
        """FCA Final = Ração Total Consumida / Total Colhido"""
        if colhido_kg <= 0 or racao_total_kg <= 0:
            return 0.0
        return round(racao_total_kg / colhido_kg, 2)

    @staticmethod
    def produtividade(colhido_kg: float, area_ha: float) -> float:
        """Produtividade (kg/ha) = Total Colhido / Área em hectares"""
        if area_ha <= 0 or colhido_kg <= 0:
            return 0.0
        return round(colhido_kg / area_ha, 2)


@pytest.fixture(scope="session")
def oracle() -> ZootecniaOracle:
    """Fixture que provê o oráculo matemático zootécnico."""
    return ZootecniaOracle()


# ==============================================================================
# FÁBRICA DE DADOS DE TESTE (FIXTURES AUXILIARES)
# ==============================================================================
@pytest.fixture
def ciclo_teste(db_session: Session, fazenda_padrao: Fazenda) -> CicloCultivo:
    """Cria um ciclo de teste ativo no Viveiro V-03 (Berçário O0) da Fazenda Arrendada."""
    v03 = db_session.query(Viveiro).filter(
        Viveiro.codigo == "V-03",
        Viveiro.fazenda_id == fazenda_padrao.id
    ).first()
    assert v03 is not None, "Viveiro V-03 deve existir na carga inicial da fazenda arrendada"

    ciclo = CicloCultivo(
        fazenda_id=fazenda_padrao.id,
        viveiro_id=v03.id,
        numero_lote="LOTE-V03-2026-1",
        data_povoamento=date(2026, 6, 19),
        pls_estocadas=65000,
        peso_inicial_g=0.01,
        laboratorio="NE",
        densidade_pl_m2=round(65000 / v03.area_m2, 2),
        status="EM CULTIVO ATIVO",
        observacoes="Lote de teste padrão V-03",
    )
    db_session.add(ciclo)
    db_session.commit()
    db_session.refresh(ciclo)
    return ciclo
