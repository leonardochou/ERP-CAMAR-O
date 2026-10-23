"""Testes automatizados para o Hub Contábil: Ingestão Excel, Bloqueio Estrito Anti-Redundância, Alocação por Viveiro, DRE, Fluxo de Caixa e Backups."""
from pathlib import Path
from fastapi.testclient import TestClient

PLANILHA_CONTABIL = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\MODELOS DE CONTROLE\Registro de custos e contas\Registro_de_Custos_e_Contas.xlsx")


def test_ingestao_planilha_contabil_e_bloqueio_estrito_redundancia(client: TestClient):
    """
    Valida que:
    1. A 1ª sincronização da planilha Registro_de_Custos_e_Contas.xlsx importa todos os lançamentos e gera backup diário.
    2. A 2ª sincronização consecutiva bloqueia automaticamente 100% das duplicatas (novos_lancamentos == 0).
    """
    assert PLANILHA_CONTABIL.exists(), "Planilha Registro_de_Custos_e_Contas.xlsx deve existir."

    # 1ª Sincronização
    r1 = client.post("/api/v1/contabilidade/sincronizar-planilha")
    assert r1.status_code == 200
    dados1 = r1.json()["resultado"]
    assert dados1["novos_lancamentos"] == 25
    assert dados1["duplicatas_bloqueadas"] == 0
    assert dados1["backup_diario"] is not None

    # 2ª Sincronização consecutiva (Mesma planilha jogada duas vezes no sistema)
    r2 = client.post("/api/v1/contabilidade/sincronizar-planilha")
    assert r2.status_code == 200
    dados2 = r2.json()["resultado"]
    assert dados2["novos_lancamentos"] == 0
    assert dados2["duplicatas_bloqueadas"] == 25


def test_resumo_contabil_dre_fluxo_e_alocacao_manual_viveiro(client: TestClient):
    """
    Valida as visões de Plano de Contas, DRE (Competência vs Caixa), Fluxo de Caixa
    e o direcionamento manual de um custo 'Geral da Fazenda' para um viveiro específico.
    """
    client.post("/api/v1/contabilidade/sincronizar-planilha")

    res = client.get("/api/v1/contabilidade/resumo-completo?regime=COMPETENCIA&centro_custo=TODOS")
    assert res.status_code == 200
    body = res.json()

    assert body["dre"]["receita_bruta"] > 0
    assert body["dre"]["custos_variaveis"] > 0
    assert body["dre"]["lucro_liquido"] != 0
    assert body["fluxo_caixa"]["entradas_realizadas"] > 0
    assert body["fluxo_caixa"]["saidas_pagas"] > 0
    assert len(body["plano_de_contas"]) >= 8
    assert len(body["livro_diario"]) == 24  # 24 na Fazenda Arrendada (e 1 na Fazenda Hakka)

    # Encontra um lançamento que veio como 'Geral da Fazenda' e direciona manualmente para 'V-05'
    lanc_geral = next(l for l in body["livro_diario"] if l["centro_custo_viveiro"] == "Geral da Fazenda")
    r_aloc = client.patch(
        f"/api/v1/contabilidade/lancamentos/{lanc_geral['id']}/alocar-viveiro",
        json={"centro_custo_viveiro": "V-05"}
    )
    assert r_aloc.status_code == 200
    assert r_aloc.json()["centro_custo_viveiro"] == "V-05"

    # Filtra o resumo contábil apenas para o V-05
    res_v05 = client.get("/api/v1/contabilidade/resumo-completo?regime=COMPETENCIA&centro_custo=V-05")
    assert res_v05.status_code == 200
    assert len(res_v05.json()["livro_diario"]) == 1
    assert res_v05.json()["livro_diario"][0]["id"] == lanc_geral["id"]


def test_bloqueio_estrito_lancamento_manual_duplicado(client: TestClient):
    """
    Valida que tentar criar dois lançamentos manuais com mesmo Valor + Fornecedor + Data de Vencimento
    descarta automaticamente a duplicata sem somar duas vezes.
    """
    payload = {
        "data_competencia": "2026-10-22",
        "data_vencimento": "2026-10-30",
        "tipo_movimento": "SAIDA",
        "nome_conta": "3.1.01 - Ração e Nutrição",
        "descricao": "Compra Teste 20 sacos ração",
        "fornecedor_cliente": "Fornecedor Teste Anti-Redundancia",
        "valor_rs": 3200.00,
        "status_pagamento": "PENDENTE",
        "forma_pagamento": "Pix"
        # Sem centro_custo_viveiro explícito -> deve cair em 'Geral da Fazenda'
    }

    r1 = client.post("/api/v1/contabilidade/lancamentos", json=payload)
    assert r1.status_code == 200
    assert r1.json()["duplicata_descartada"] is False
    assert r1.json()["centro_custo_viveiro"] == "Geral da Fazenda"

    # Segunda tentativa idêntica (mesmo Valor + Fornecedor + Vencimento)
    r2 = client.post("/api/v1/contabilidade/lancamentos", json=payload)
    assert r2.status_code == 200
    assert r2.json()["duplicata_descartada"] is True
    assert r2.json()["status"] == "bloqueado_redundancia"
