"""Testes automatizados para a Ingestão Incremental Inteligente de Alimentação e Biometria."""
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.fazenda import Fazenda
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.biometria import Biometria
from app.services.ingestor_service import IngestorService

ARQUIVO_ALIMENTACAO_REAL = Path(
    r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\MODELOS DE CONTROLE\Controle de alimentação e biometria\Controle_Alimentacao_e_Biometria.xlsx"
)


def test_ingestao_incremental_alimentacao_e_biometria(db_session: Session):
    """Testa a ingestão inicial e reingestão idempotente com a planilha real da fazenda."""
    # Garante fazenda padrão
    fazenda = db_session.query(Fazenda).first()
    assert fazenda is not None

    if not ARQUIVO_ALIMENTACAO_REAL.exists():
        return  # Pula caso execute em ambiente sem o drive

    # 1. Primeira Ingestão da Planilha Real
    resumo_1 = IngestorService.processar_planilha_alimentacao(
        db=db_session,
        arquivo_ou_caminho=ARQUIVO_ALIMENTACAO_REAL,
        fazenda_id=fazenda.id,
        fazenda_codigo=fazenda.codigo
    )

    assert resumo_1["tipo"] == "ALIMENTACAO_E_BIOMETRIA"
    assert "novidades_por_viveiro" in resumo_1
    assert resumo_1["novos_lancamentos"] > 0
    assert resumo_1["biometrias_registradas"] > 0

    # Verifica se os tanques reais foram populados
    assert "V-03" in resumo_1["novidades_por_viveiro"]
    assert "V-05" in resumo_1["novidades_por_viveiro"]
    v3_info = resumo_1["novidades_por_viveiro"]["V-03"]
    assert v3_info["laboratorio"] == "NE"
    assert v3_info["pls_estocadas"] == 65000

    # 2. Segunda Ingestão Consecutiva da Mesma Planilha (Deduplicação Inteligente)
    resumo_2 = IngestorService.processar_planilha_alimentacao(
        db=db_session,
        arquivo_ou_caminho=ARQUIVO_ALIMENTACAO_REAL,
        fazenda_id=fazenda.id,
        fazenda_codigo=fazenda.codigo
    )

    # NENHUM novo lançamento deve ser inserido (100% idempotente via SHA-256)
    assert resumo_2["novos_lancamentos"] == 0
    assert resumo_2["duplicatas_ignoradas"] > 0
    assert resumo_2["novidades_por_viveiro"]["V-03"]["duplicatas_ignoradas"] > 0
    assert len(resumo_2["novidades_por_viveiro"]["V-03"]["dias_novos"]) == 0
