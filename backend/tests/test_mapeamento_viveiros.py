"""Testes automatizados para o módulo Mapa dos Viveiros e Calibração de Metragem."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro


def test_seed_mapeamento_numeracao_pai(client: TestClient, db_session: Session, fazenda_arrendada: Fazenda):
    """Valida que todos os 10 viveiros principais do pai e berçários estão cadastrados."""
    resp = client.get("/api/v1/viveiros/mapa")
    assert resp.status_code == 200
    tanques = resp.json()
    assert len(tanques) == 15

    # Confere a numeração do pai de 1 a 10
    numeros_pai = [t["numero_pai"] for t in tanques if t["numero_pai"] is not None]
    assert sorted(numeros_pai) == list(range(1, 11))

    # Confere Viveiro 1 (C1)
    v1 = next(t for t in tanques if t["numero_pai"] == 1)
    assert v1["nome_pai"] == "Viveiro 1"
    assert v1["area_satelite_m2"] == 12600.0
    assert v1["setor"] == "Central"

    # Confere Berçários
    bercarios = [t for t in tanques if t["tipo_uso"] == "Berçário"]
    assert len(bercarios) >= 2


def test_calibracao_metragem_sucesso(client: TestClient, db_session: Session):
    """Testa a rota PATCH para ajustar a metragem de campo de um tanque com recálculo automático."""
    v1 = db_session.query(Viveiro).filter(Viveiro.codigo == "V-01").first()
    assert v1 is not None

    nova_area = 12450.0  # Nova medição precisa de campo
    nova_profundidade = 1.30

    resp = client.patch(
        f"/api/v1/viveiros/{v1.codigo}/metragem",
        json={
            "area_ajustada_m2": nova_area,
            "profundidade_media_m": nova_profundidade,
            "observacoes": "Medição por drone e trena a laser"
        }
    )
    assert resp.status_code == 200
    dados = resp.json()

    assert dados["area_ajustada_m2"] == nova_area
    assert dados["area_m2"] == nova_area
    assert dados["area_ha"] == 1.245
    assert dados["profundidade_media_m"] == nova_profundidade
    assert dados["volume_m3"] == round(nova_area * nova_profundidade, 2)
    assert dados["origem_metragem"] == "MEDICAO_CAMPO"
    assert dados["area_satelite_m2"] == 12600.0  # A metragem de satélite original permanece intacta


def test_calibracao_metragem_invalida_retorna_400(client: TestClient):
    """Testa rejeição de metragem zero ou negativa."""
    resp = client.patch(
        "/api/v1/viveiros/V-01/metragem",
        json={"area_ajustada_m2": -50.0}
    )
    assert resp.status_code in (400, 422)


def test_calibracao_viveiro_inexistente_retorna_404(client: TestClient):
    """Testa tentativa de calibração em viveiro inexistente."""
    resp = client.patch(
        "/api/v1/viveiros/V-99/metragem",
        json={"area_ajustada_m2": 10000.0}
    )
    assert resp.status_code == 404
