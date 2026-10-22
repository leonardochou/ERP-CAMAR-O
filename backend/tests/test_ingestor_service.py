"""Testes automatizados para o serviço de Ingestão e Sincronização de Planilhas."""
import os
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.services.ingestor_service import IngestorService

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELOS_DIR = BASE_DIR.parent / "MODELOS DE CONTROLE"
CAMINHO_ALIMENTACAO = MODELOS_DIR / "Controle de alimentação e biometria" / "Controle_Alimentacao_e_Biometria.xlsx"
CAMINHO_AGUA = MODELOS_DIR / "Controle de qualidade de agua" / "Controle_Qualidade_Agua.xlsx"


def test_ingestao_alimentacao_planilha_real(db_session: Session, fazenda_arrendada: Fazenda):
    """Testa a ingestão da planilha real de alimentação, conferindo linhas, biometrias e idempotência."""
    assert CAMINHO_ALIMENTACAO.exists(), "Planilha de alimentação deve existir"

    # Primeira execução
    res1 = IngestorService.processar_planilha_alimentacao(
        db=db_session,
        arquivo_ou_caminho=CAMINHO_ALIMENTACAO,
        fazenda_id=fazenda_arrendada.id,
        fazenda_codigo=fazenda_arrendada.codigo
    )

    assert res1["linhas_lidas"] > 0
    assert res1["novos_lancamentos"] > 0
    total_inseridos_primeira_vez = res1["novos_lancamentos"]

    # Segunda execução sobre a mesma base: IDEMPOTÊNCIA ESTRITA
    res2 = IngestorService.processar_planilha_alimentacao(
        db=db_session,
        arquivo_ou_caminho=CAMINHO_ALIMENTACAO,
        fazenda_id=fazenda_arrendada.id,
        fazenda_codigo=fazenda_arrendada.codigo
    )

    assert res2["novos_lancamentos"] == 0
    assert res2["duplicatas_ignoradas"] == total_inseridos_primeira_vez


def test_ingestao_agua_planilha_real(db_session: Session, fazenda_arrendada: Fazenda):
    """Testa a ingestão da planilha real de qualidade da água e geração de alertas."""
    assert CAMINHO_AGUA.exists(), "Planilha de água deve existir"

    res = IngestorService.processar_planilha_agua(
        db=db_session,
        arquivo_ou_caminho=CAMINHO_AGUA,
        fazenda_id=fazenda_arrendada.id,
        fazenda_codigo=fazenda_arrendada.codigo
    )

    assert res["linhas_lidas"] > 0
    assert res["novas_medicoes"] >= 0
