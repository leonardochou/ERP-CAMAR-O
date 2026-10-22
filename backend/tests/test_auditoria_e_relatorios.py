"""Testes para relatórios executivos, dias esquecidos e alertas automáticos de FCA."""
import pytest
from datetime import date, timedelta


def test_detector_dias_esquecidos(client):
    """Valida o alerta da Central de Auditoria para viveiros ativos sem dados nas últimas 24h."""
    # 1. Obter V-01 e iniciar ciclo ativo
    v_resp = client.get("/api/v1/viveiros/V-01")
    assert v_resp.status_code == 200
    v01_id = v_resp.json()["id"]

    ciclo_payload = {
        "viveiro_id": v01_id,
        "numero_lote": "LOTE-ESQUECIDO-V01",
        "data_povoamento": "2026-06-01",
        "pls_estocadas": 50000,
        "status": "EM CULTIVO ATIVO"
    }
    client.post("/api/v1/ciclos/", json=ciclo_payload)

    # 2. Executa a rotina de detecção de dias esquecidos
    verif_resp = client.post("/api/v1/auditoria/verificar-dias-esquecidos")
    assert verif_resp.status_code == 200
    alertas = verif_resp.json()
    assert len(alertas) >= 1
    alerta_v01 = [a for a in alertas if a["viveiro_codigo"] == "V-01"][0]
    assert alerta_v01["tipo_anomalia"] == "DIA_ESQUECIDO"
    assert alerta_v01["severidade"] == "ATENCAO"


def test_alerta_fca_anomalo_camarao_jovem(client):
    """Garante que a biometria com FCA > 1.8 em camarão < 10g dispare alerta de desvio na auditoria."""
    # 1. Obter V-04 e iniciar ciclo
    v_resp = client.get("/api/v1/viveiros/V-04")
    v04_id = v_resp.json()["id"]

    ciclo_resp = client.post("/api/v1/ciclos/", json={
        "viveiro_id": v04_id,
        "numero_lote": "LOTE-FCA-ALERTA-V04",
        "data_povoamento": "2026-08-01",
        "pls_estocadas": 40000,
        "peso_inicial_g": 0.01,
        "status": "EM CULTIVO ATIVO"
    })
    ciclo_id = ciclo_resp.json()["id"]

    # 2. Lançar quantidade anormal de ração (ex: 800 kg em poucos dias)
    client.post("/api/v1/alimentacao/", json={
        "ciclo_id": ciclo_id,
        "data": "2026-08-15",
        "doc": 15,
        "racao_manha_kg": 400.0,
        "racao_tarde_kg": 400.0
    })

    # 3. Lançar biometria com peso jovem de 6.0g e 80% sobrevivência
    # População: 32000, Biomassa: 32000 * 6.0 / 1000 = 192 kg
    # FCA Parcial: 800 / 192 = 4.17 (> 1.8 e peso < 10g)
    bio_resp = client.post("/api/v1/biometrias/", json={
        "ciclo_id": ciclo_id,
        "data": "2026-08-15",
        "doc": 15,
        "peso_medio_g": 6.0,
        "sobrevivencia_estimada_pct": 80.0
    })
    assert bio_resp.status_code == 201
    assert bio_resp.json()["fca_parcial"] == 4.17

    # 4. Verifica se a Auditoria gerou a pendência de FCA_DESVIO
    audit_resp = client.get("/api/v1/auditoria/pendencias")
    pendencias = audit_resp.json()
    fca_alertas = [p for p in pendencias if p["tipo_anomalia"] == "FCA_DESVIO" and p["viveiro_codigo"] == "V-04"]
    assert len(fca_alertas) >= 1
    assert "FCA Parcial crítico de 4.17" in fca_alertas[0]["mensagem"]


def test_relatorios_resumo_executivo_e_micro_dashboard(client):
    """Testa os endpoints dos dashboards das Camadas Macro e Micro."""
    # Resumo Executivo Macro
    macro_resp = client.get("/api/v1/relatorios/resumo-executivo")
    assert macro_resp.status_code == 200
    macro_data = macro_resp.json()
    assert macro_data["total_viveiros"] == 15
    assert "biomassa_total_viva_kg" in macro_data
    assert "distribuicao_status" in macro_data

    # Dashboard Micro do Viveiro V-01
    micro_resp = client.get("/api/v1/relatorios/viveiro/V-01/dashboard")
    assert micro_resp.status_code == 200
    micro_data = micro_resp.json()
    assert micro_data["viveiro"]["codigo"] == "V-01"
    assert "serie_agua" in micro_data
    assert "serie_biometria" in micro_data
    assert "serie_alimentacao" in micro_data


def test_vendas_e_despescas(client):
    """Testa o registro de comercialização com cálculo de faturamento bruto."""
    # Obter um ciclo ativo existente
    v_resp = client.get("/api/v1/viveiros/V-05")
    v05_id = v_resp.json()["id"]

    ciclo_resp = client.post("/api/v1/ciclos/", json={
        "viveiro_id": v05_id,
        "numero_lote": "LOTE-VENDA-V05",
        "data_povoamento": "2026-07-01",
        "pls_estocadas": 41000,
        "status": "EM CULTIVO ATIVO"
    })
    ciclo_id = ciclo_resp.json()["id"]

    venda_payload = {
        "ciclo_id": ciclo_id,
        "data": "2026-10-20",
        "tipo_despesca": "TOTAL",
        "gramatura_media_g": 17.2,
        "camarao_colhido_kg": 580.0,
        "comprador": "Pescados Potiguar Ltda",
        "preco_kg_rs": 24.50,
        "status_pagamento": "A RECEBER"
    }
    venda_resp = client.post("/api/v1/despescas/", json=venda_payload)
    assert venda_resp.status_code == 201
    venda_data = venda_resp.json()
    # 580 * 24.50 = 14210.00
    assert venda_data["faturamento_bruto_rs"] == 14210.00
    venda_id = venda_data["id"]

    # Atualiza pagamento para RECEBIDO
    put_resp = client.put(f"/api/v1/despescas/{venda_id}", json={
        "status_pagamento": "RECEBIDO",
        "forma_pagamento": "Pix",
        "data_pagamento": "2026-10-21"
    })
    assert put_resp.status_code == 200
    assert put_resp.json()["status_pagamento"] == "RECEBIDO"
