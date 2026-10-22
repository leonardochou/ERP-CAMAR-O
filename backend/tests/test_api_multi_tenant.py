"""Testes de integração para a camada Multi-Tenant do ERP CAMARÃO."""
import pytest
from app.core.tenant import FAZENDA_PADRAO_CODIGO, FAZENDA_HAKKA_CODIGO


def test_listar_fazendas_seed(client):
    """Verifica se as fazendas padrão (Arrendada e Hakka) são inicializadas automaticamente."""
    response = client.get("/api/v1/fazendas/")
    assert response.status_code == 200
    fazendas = response.json()

    assert len(fazendas) >= 2
    codigos = [f["codigo"] for f in fazendas]
    assert FAZENDA_PADRAO_CODIGO in codigos
    assert FAZENDA_HAKKA_CODIGO in codigos


def test_obter_fazenda_por_codigo(client):
    """Testa a recuperação individual de fazenda por código identificador."""
    response = client.get(f"/api/v1/fazendas/{FAZENDA_PADRAO_CODIGO}")
    assert response.status_code == 200
    dados = response.json()
    assert dados["codigo"] == FAZENDA_PADRAO_CODIGO
    assert dados["tipo_propriedade"] == "arrendada"
    assert "Ceará-Mirim" in dados["municipio_uf"]


def test_fallback_automatico_fazenda_arrendada(client):
    """Garante que requisições sem header X-Fazenda-Id operem por padrão na Fazenda Arrendada."""
    # Listar viveiros sem header -> deve retornar os 15 viveiros da Fazenda Arrendada
    response = client.get("/api/v1/viveiros/")
    assert response.status_code == 200
    viveiros = response.json()
    assert len(viveiros) == 15
    codigos = [v["codigo"] for v in viveiros]
    assert "V-01" in codigos
    assert "V-15" in codigos


def test_chaveamento_fazenda_hakka(client):
    """Testa o isolamento de dados com chaveamento de tenant via header X-Fazenda-Id."""
    # Na Fazenda Hakka, inicialmente não há nenhum viveiro cadastrado
    response = client.get("/api/v1/viveiros/", headers={"X-Fazenda-Id": FAZENDA_HAKKA_CODIGO})
    assert response.status_code == 200
    viveiros_hakka = response.json()
    assert len(viveiros_hakka) == 0

    # Cadastra um novo viveiro na Fazenda Hakka
    novo_tanque = {
        "codigo": "H-01",
        "nome_operacional": "Hakka Tanque 1",
        "setor": "Norte",
        "area_m2": 10000.0,
        "area_ha": 1.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 12000.0,
        "tipo_uso": "Engorda",
        "ativo": True
    }
    post_resp = client.post("/api/v1/viveiros/", json=novo_tanque, headers={"X-Fazenda-Id": FAZENDA_HAKKA_CODIGO})
    assert post_resp.status_code == 201
    assert post_resp.json()["codigo"] == "H-01"

    # Confirma que H-01 aparece apenas na Fazenda Hakka
    list_hakka = client.get("/api/v1/viveiros/", headers={"X-Fazenda-Id": FAZENDA_HAKKA_CODIGO})
    assert len(list_hakka.json()) == 1

    # Confirma que a Fazenda Arrendada continua com seus 15 viveiros intactos
    list_arrendada = client.get("/api/v1/viveiros/", headers={"X-Fazenda-Id": FAZENDA_PADRAO_CODIGO})
    assert len(list_arrendada.json()) == 15
    assert "H-01" not in [v["codigo"] for v in list_arrendada.json()]


def test_cadastrar_nova_fazenda(client):
    """Cadastra uma terceira propriedade rural e valida persistência."""
    nova = {
        "codigo": "FAZ_NOVA_EXTENSAO",
        "nome": "Fazenda Nova Extensão",
        "tipo_propriedade": "propria",
        "municipio_uf": "Ceará-Mirim/RN",
        "status": "ativa"
    }
    response = client.post("/api/v1/fazendas/", json=nova)
    assert response.status_code == 201
    assert response.json()["codigo"] == "FAZ_NOVA_EXTENSAO"
