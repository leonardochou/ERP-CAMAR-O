"""Testes automatizados para o Módulo de Gestão de Ciclos de Produção e Safras."""
from pathlib import Path
import pytest
from datetime import date
from app.core.tenant import FAZENDA_HAKKA_ID
from app.models.fazenda import Fazenda
from app.services.ingestor_service import IngestorService


def test_iniciar_ciclo_sequencial_auto(client):
    """Garante numeração sequencial automática por viveiro e ano (Ciclo 2026.1 -> Ciclo 2026.2)."""
    # 1. Obter V-01
    v_resp = client.get("/api/v1/viveiros/V-01")
    assert v_resp.status_code == 200
    v01_id = v_resp.json()["id"]

    # 2. Iniciar primeiro ciclo de 2026 via /iniciar
    payload1 = {
        "viveiro_id": v01_id,
        "ano_safra": 2026,
        "data_povoamento": "2026-01-15",
        "pls_estocadas": 60000,
        "laboratorio": "AQUATEC",
        "observacoes": "Povoamento inicial 2026.1"
    }
    resp1 = client.post("/api/v1/ciclos/iniciar", json=payload1)
    assert resp1.status_code == 201
    c1 = resp1.json()
    assert c1["codigo_ciclo"] == "V-01 • Ciclo 2026.1"
    assert c1["numero_sequencial"] == 1
    assert c1["ano_safra"] == 2026
    assert c1["status"] == "EM CULTIVO ATIVO"

    # 3. Encerrar o ciclo 2026.1
    encerrar_payload = {
        "data_despesca": "2026-04-10",
        "camarao_colhido_kg": 600.0,
        "peso_final_g": 13.5,
        "preco_kg_rs": 23.00,
        "observacoes": "Encerramento com despesca total"
    }
    resp_enc = client.post(f"/api/v1/ciclos/{c1['id']}/encerrar", json=encerrar_payload)
    assert resp_enc.status_code == 200
    c1_fechado = resp_enc.json()
    assert c1_fechado["status"] == "ENCERRADO"
    assert c1_fechado["camarao_colhido_kg"] == 600.0

    # 4. Iniciar segundo ciclo no mesmo viveiro em 2026
    payload2 = {
        "viveiro_id": v01_id,
        "ano_safra": 2026,
        "data_povoamento": "2026-05-01",
        "pls_estocadas": 65000,
        "laboratorio": "NE",
        "observacoes": "Novo ciclo pós-preparo de solo"
    }
    resp2 = client.post("/api/v1/ciclos/iniciar", json=payload2)
    assert resp2.status_code == 201
    c2 = resp2.json()
    assert c2["codigo_ciclo"] == "V-01 • Ciclo 2026.2"
    assert c2["numero_sequencial"] == 2
    assert c2["id"] != c1["id"]

    # 5. Garantir que ambos os ciclos coexistem e o ciclo 1 não foi corrompido
    get_c1 = client.get(f"/api/v1/ciclos/{c1['id']}")
    assert get_c1.status_code == 200
    assert get_c1.json()["codigo_ciclo"] == "V-01 • Ciclo 2026.1"
    assert get_c1.json()["status"] == "ENCERRADO"


def test_despesca_parcial_e_recalculo_fechamento(client):
    """Testa o desbaste/despesca parcial, persistência em vendas e consolidação no encerramento final."""
    # 1. Obter V-02
    v_resp = client.get("/api/v1/viveiros/V-02")
    assert v_resp.status_code == 200
    v02_id = v_resp.json()["id"]

    # 2. Iniciar ciclo
    ciclo_resp = client.post("/api/v1/ciclos/iniciar", json={
        "viveiro_id": v02_id,
        "ano_safra": 2026,
        "data_povoamento": "2026-03-01",
        "pls_estocadas": 80000,
        "laboratorio": "AQUATEC"
    })
    assert ciclo_resp.status_code == 201
    ciclo_id = ciclo_resp.json()["id"]

    # 3. Lançar alimentação (100 kg no total)
    t_resp = client.post("/api/v1/alimentacao/", json={
        "ciclo_id": ciclo_id,
        "data": "2026-03-02",
        "doc": 1,
        "racao_manha_kg": 50.0,
        "racao_tarde_kg": 50.0
    })
    assert t_resp.status_code == 201

    # 4. Registrar Despesca Parcial (Desbaste de 250 kg)
    parcial_payload = {
        "data": "2026-05-15",
        "camarao_colhido_kg": 250.0,
        "gramatura_media_g": 11.0,
        "comprador": "Peixaria Regional",
        "preco_kg_rs": 22.00,
        "observacoes": "Desbaste de 30% da biomassa"
    }
    parcial_resp = client.post(f"/api/v1/ciclos/{ciclo_id}/despesca-parcial", json=parcial_payload)
    assert parcial_resp.status_code == 200
    c_parcial = parcial_resp.json()
    assert c_parcial["status"] == "DESPESCA_PARCIAL"
    assert c_parcial["despescas_parciais_kg"] == 250.0

    # 5. Encerrar Ciclo com Despesca Final de 550 kg (Total colhido = 250 + 550 = 800 kg)
    final_payload = {
        "data_despesca": "2026-06-20",
        "camarao_colhido_kg": 550.0,
        "peso_final_g": 14.0,
        "preco_kg_rs": 24.00,
        "observacoes": "Despesca final e drenagem completa"
    }
    encerrar_resp = client.post(f"/api/v1/ciclos/{ciclo_id}/encerrar", json=final_payload)
    assert encerrar_resp.status_code == 200
    c_final = encerrar_resp.json()

    assert c_final["status"] == "ENCERRADO"
    # Total colhido deve somar parcial (250) + final (550) = 800.0 kg
    assert c_final["camarao_colhido_kg"] == 800.0
    # Faturamento total deve somar desbaste (250 * 22 = 5500) + despesca final (550 * 24 = 13200) = 18700
    assert c_final["faturamento_total_rs"] == 18700.0
    # FCA final = 100 kg ração / 800 kg colhido = 0.125 -> 0.12 ou 0.13
    assert c_final["fca_real_final"] == pytest.approx(0.12, abs=0.02)
    # Sobrevivência calculada sobre 800 kg e 14.0g com 80.000 PLs:
    # camaroes = 800 * 1000 / 14 = 57142.86 -> 57142.86 / 80000 * 100 = 71.43%
    assert c_final["sobrevivencia_real_pct"] == 71.43


def test_listar_ciclos_ativos_e_historico(client):
    """Testa a separação estrita entre ciclos ativos na água e histórico permanente."""
    v01 = client.get("/api/v1/viveiros/V-01").json()["id"]
    v02 = client.get("/api/v1/viveiros/V-02").json()["id"]

    # Cria ciclo ativo no V-01
    c1 = client.post("/api/v1/ciclos/iniciar", json={
        "viveiro_id": v01,
        "ano_safra": 2026,
        "data_povoamento": "2026-02-01",
        "pls_estocadas": 50000
    }).json()

    # Cria ciclo no V-02 e encerra
    c2 = client.post("/api/v1/ciclos/iniciar", json={
        "viveiro_id": v02,
        "ano_safra": 2026,
        "data_povoamento": "2026-01-10",
        "pls_estocadas": 50000
    }).json()

    client.post(f"/api/v1/ciclos/{c2['id']}/encerrar", json={
        "data_despesca": "2026-04-01",
        "camarao_colhido_kg": 500.0,
        "peso_final_g": 12.0
    })

    # Verificar /ativos: deve conter apenas c1
    resp_ativos = client.get("/api/v1/ciclos/ativos")
    assert resp_ativos.status_code == 200
    ativos = resp_ativos.json()
    ids_ativos = [c["id"] for c in ativos]
    assert c1["id"] in ids_ativos
    assert c2["id"] not in ids_ativos

    # Verificar /historico: deve conter c2
    resp_hist = client.get("/api/v1/ciclos/historico?ano_safra=2026")
    assert resp_hist.status_code == 200
    historico = resp_hist.json()
    ids_hist = [c["id"] for c in historico]
    assert c2["id"] in ids_hist
    assert c1["id"] not in ids_hist


def test_isolamento_multitenant_ciclos(client):
    """Garante que ciclos da fazenda arrendada não vazem para a fazenda hakka."""
    v01 = client.get("/api/v1/viveiros/V-01").json()["id"]

    # Ciclo na fazenda padrão (Arrendada)
    c_resp = client.post("/api/v1/ciclos/iniciar", json={
        "viveiro_id": v01,
        "ano_safra": 2026,
        "data_povoamento": "2026-03-01",
        "pls_estocadas": 50000
    })
    assert c_resp.status_code == 201
    ciclo_id = c_resp.json()["id"]

    # Faz requisição com header de tenant da Fazenda Hakka
    hakka_headers = {"X-Fazenda-ID": FAZENDA_HAKKA_ID}
    h_resp = client.get("/api/v1/ciclos/ativos", headers=hakka_headers)
    assert h_resp.status_code == 200
    ids_hakka = [c["id"] for c in h_resp.json()]
    assert ciclo_id not in ids_hakka


def test_multiplos_desbastes_sucessivos(client):
    """Testa múltiplos raleios/desbastes sucessivos no mesmo ciclo antes do esgotamento final."""
    v03 = client.get("/api/v1/viveiros/V-03").json()["id"]

    # 1. Iniciar Ciclo
    c = client.post("/api/v1/ciclos/iniciar", json={
        "viveiro_id": v03,
        "ano_safra": 2026,
        "data_povoamento": "2026-02-01",
        "pls_estocadas": 70000
    }).json()
    ciclo_id = c["id"]

    # 2. Desbaste 1: 150 kg @ R$ 20.00 = R$ 3.000,00
    d1 = client.post(f"/api/v1/ciclos/{ciclo_id}/despesca-parcial", json={
        "data": "2026-04-10",
        "camarao_colhido_kg": 150.0,
        "gramatura_media_g": 10.0,
        "preco_kg_rs": 20.0
    }).json()
    assert d1["status"] == "DESPESCA_PARCIAL"
    assert d1["despescas_parciais_kg"] == 150.0

    # 3. Desbaste 2: 200 kg @ R$ 22.00 = R$ 4.400,00 (Total acumulado: 350 kg)
    d2 = client.post(f"/api/v1/ciclos/{ciclo_id}/despesca-parcial", json={
        "data": "2026-04-25",
        "camarao_colhido_kg": 200.0,
        "gramatura_media_g": 12.0,
        "preco_kg_rs": 22.0
    }).json()
    assert d2["status"] == "DESPESCA_PARCIAL"
    assert d2["despescas_parciais_kg"] == 350.0

    # 4. Despesca Final: 450 kg @ R$ 25.00 = R$ 11.250,00 (Total geral: 800 kg)
    c_final = client.post(f"/api/v1/ciclos/{ciclo_id}/encerrar", json={
        "data_despesca": "2026-05-20",
        "camarao_colhido_kg": 450.0,
        "peso_final_g": 15.0,
        "preco_kg_rs": 25.0
    }).json()

    assert c_final["status"] == "ENCERRADO"
    assert c_final["camarao_colhido_kg"] == 800.0
    # Faturamento total = 3.000 + 4.400 + 11.250 = 18.650,00
    assert c_final["faturamento_total_rs"] == 18650.0


def test_ingestao_planilha_campos_oficiais_ciclo(client, db_session):
    """Testa se a ingestão da planilha oficial preenche codigo_ciclo, ano_safra e numero_sequencial."""
    fazenda = db_session.query(Fazenda).first()
    assert fazenda is not None

    caminho = Path(__file__).resolve().parent.parent.parent.parent / "MODELOS DE CONTROLE" / "Controle de alimentação e biometria" / "Controle_Alimentacao_e_Biometria.xlsx"
    if caminho.exists():
        IngestorService.processar_planilha_alimentacao(
            db=db_session,
            arquivo_ou_caminho=caminho,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )

    # Acessa os ciclos ativos e históricos
    resp = client.get("/api/v1/ciclos/")
    assert resp.status_code == 200
    ciclos = resp.json()
    assert len(ciclos) > 0
    # Verifica integridade de formato dos códigos gerados
    for c in ciclos:
        assert c["codigo_ciclo"] is not None
        assert "• Ciclo" in c["codigo_ciclo"]
        assert c["ano_safra"] is not None
        assert c["numero_sequencial"] is not None
