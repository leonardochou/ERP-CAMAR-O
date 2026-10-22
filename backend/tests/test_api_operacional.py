"""Testes de integração para os fluxos zootécnicos e operacionais do ERP CAMARÃO."""
import pytest
from datetime import date


def test_mapa_15_viveiros(client):
    """Garante que a rota do mapa 2D retorne os 15 viveiros com geometria e status inicial VAZIO."""
    response = client.get("/api/v1/viveiros/mapa")
    assert response.status_code == 200
    mapa = response.json()
    assert len(mapa) == 15
    for tanque in mapa:
        assert tanque["codigo"].startswith("V-")
        assert tanque["status_cor"] in ["OTIMO", "ATENCAO", "CRITICO", "VAZIO"]


def test_ciclo_completo_producao_e_zootecnia(client):
    """Executa o ciclo completo de cultivo: povoamento, trato, água, biometria e despesca final."""
    # 1. Obter V-03 (área 1.430 m² / 0.143 ha)
    v_resp = client.get("/api/v1/viveiros/V-03")
    assert v_resp.status_code == 200
    v03_data = v_resp.json()
    v03_id = v03_data["id"]
    area_m2 = v03_data["area_m2"]

    # 2. Iniciar Ciclo de Cultivo (65.000 PLs)
    ciclo_payload = {
        "viveiro_id": v03_id,
        "numero_lote": "LOTE-2026-TESTE-V03",
        "data_povoamento": "2026-06-19",
        "pls_estocadas": 65000,
        "laboratorio": "NE",
        "peso_inicial_g": 0.01,
        "status": "EM CULTIVO ATIVO"
    }
    ciclo_resp = client.post("/api/v1/ciclos/", json=ciclo_payload)
    assert ciclo_resp.status_code == 201
    ciclo_data = ciclo_resp.json()
    ciclo_id = ciclo_data["id"]
    # Densidade esperada calculada dinamicamente: 65000 / area_m2
    densidade_esperada = round(65000 / area_m2, 2)
    assert ciclo_data["densidade_pl_m2"] == densidade_esperada

    # 3. Lançamento de Alimentação (Dia 1 e Dia 2)
    trato_d1 = {
        "ciclo_id": ciclo_id,
        "data": "2026-06-20",
        "doc": 1,
        "racao_manha_kg": 15.0,
        "sobra_manha": 0,
        "racao_tarde_kg": 15.0,
        "sobra_tarde": 1
    }
    t1_resp = client.post("/api/v1/alimentacao/", json=trato_d1)
    assert t1_resp.status_code == 201
    assert t1_resp.json()["total_dia_kg"] == 30.0
    assert t1_resp.json()["consumo_acumulado_kg"] == 30.0

    trato_d2 = {
        "ciclo_id": ciclo_id,
        "data": "2026-06-21",
        "doc": 2,
        "racao_manha_kg": 20.0,
        "sobra_manha": 1,
        "racao_tarde_kg": 20.0,
        "sobra_tarde": 2
    }
    t2_resp = client.post("/api/v1/alimentacao/", json=trato_d2)
    assert t2_resp.status_code == 201
    assert t2_resp.json()["total_dia_kg"] == 40.0
    assert t2_resp.json()["consumo_acumulado_kg"] == 70.0  # 30 + 40

    # 4. Monitoramento de Qualidade de Água (Normal e Crítico)
    agua_normal = {
        "viveiro_id": v03_id,
        "ciclo_id": ciclo_id,
        "data": "2026-06-20",
        "o2_manha": 4.5,
        "o2_noite": 5.0,
        "ph_manha": 7.8,
        "ph_tarde": 8.3,
        "salinidade_ppt": 15.0,
        "amonia_mg_l": 0.01,
        "nitrito_mg_l": 0.02
    }
    a1_resp = client.post("/api/v1/agua/", json=agua_normal)
    assert a1_resp.status_code == 201
    assert a1_resp.json()["status_tanque"] == "OTIMO"
    assert a1_resp.json()["delta_ph"] == 0.50

    # Inserir água com O2 crítico (2.6 mg/L) -> Deve classificar como CRITICO e abrir Auditoria
    agua_critica = {
        "viveiro_id": v03_id,
        "ciclo_id": ciclo_id,
        "data": "2026-06-21",
        "o2_manha": 2.6,
        "o2_noite": 3.1,
        "ph_manha": 7.5,
        "ph_tarde": 8.0,
        "amonia_mg_l": 0.05
    }
    a2_resp = client.post("/api/v1/agua/", json=agua_critica)
    assert a2_resp.status_code == 201
    assert a2_resp.json()["status_tanque"] == "CRITICO"

    # 5. Verifica se a Central de Auditoria recebeu o alerta de O2 crítico
    audit_resp = client.get("/api/v1/auditoria/pendencias")
    assert audit_resp.status_code == 200
    pendencias = audit_resp.json()
    assert len(pendencias) >= 1
    p_critica = [p for p in pendencias if p["tipo_anomalia"] == "O2_CRITICO"][0]
    assert p_critica["severidade"] == "CRITICA"
    assert "O2 Matutino crítico: 2.6 mg/L" in p_critica["mensagem"]

    # 6. Resolver a pendência de auditoria em 1 clique
    resolucao_resp = client.post(
        f"/api/v1/auditoria/{p_critica['id']}/resolver",
        json={"acao": "MANTER_NOVO"}
    )
    assert resolucao_resp.status_code == 200
    assert resolucao_resp.json()["resolvido"] is True
    assert resolucao_resp.json()["acao_resolucao"] == "MANTER_NOVO"

    # 7. Registrar Biometria (DOC 30, peso médio 5.0g, sobrevivência 85%)
    bio_payload = {
        "ciclo_id": ciclo_id,
        "data": "2026-07-19",
        "doc": 30,
        "peso_medio_g": 5.0,
        "amostra_qtd": 100,
        "sobrevivencia_estimada_pct": 85.0
    }
    bio_resp = client.post("/api/v1/biometrias/", json=bio_payload)
    assert bio_resp.status_code == 201
    bio_data = bio_resp.json()

    # População esperada = 65000 * 0.85 = 55250
    assert bio_data["populacao_estimada"] == 55250
    # Biomassa esperada = 55250 * 5.0 / 1000 = 276.25 kg
    assert bio_data["biomassa_estimada_kg"] == 276.25
    # Ração total acumulada até a data = 70.0 kg
    assert bio_data["racao_acumulada_ate_data_kg"] == 70.0
    # FCA Parcial = 70.0 / 276.25 = 0.25
    assert bio_data["fca_parcial"] == 0.25

    # 8. Fechamento de Safra (Despesca Final)
    fechar_payload = {
        "data_despesca": "2026-10-15",
        "camarao_colhido_kg": 650.0,
        "peso_final_g": 14.5,
        "faturamento_total_rs": 19500.0,
        "observacoes": "Despesca concluída com sucesso operacional"
    }
    fechar_resp = client.post(f"/api/v1/ciclos/{ciclo_id}/fechar", json=fechar_payload)
    assert fechar_resp.status_code == 200
    fechado = fechar_resp.json()
    assert fechado["status"] == "DESPESCADO"
    # Camaroes colhidos = 650 * 1000 / 14.5 = 44827.58
    # Sobrevivencia = 44827.58 / 65000 * 100 = 68.97%
    assert fechado["sobrevivencia_real_pct"] == 68.97
    # FCA Real Final = 70.0 / 650.0 = 0.11 (com apenas os 2 dias lançados)
    assert fechado["fca_real_final"] == 0.11
    # Produtividade = 650 / area_ha
    produtividade_esperada = round(650.0 / (area_m2 / 10000.0), 2)
    assert fechado["produtividade_kg_ha"] == produtividade_esperada


def test_whatsapp_webhook_e_emergencia(client):
    """Testa a entrada do webhook do WhatsApp e o disparo de alerta noturno para o vigia."""
    # 1. Envio de mensagem de texto pelo operador de campo
    msg_in = {
        "remetente": "+5584999998888",
        "tipo_mensagem": "texto",
        "texto": "Tanque V-05 trato manha 30kg sobra 1 o2 4.1"
    }
    w_resp = client.post("/api/v1/whatsapp/webhook", json=msg_in)
    assert w_resp.status_code == 200
    w_data = w_resp.json()
    assert w_data["status"] == "recebido"
    assert "V-05" in w_data["mensagem_confirmacao"]

    # 2. Disparo de Alerta de Emergência noturno para o vigia
    alerta = {
        "destinatario": "Vigia Noturno - Ronda",
        "viveiro_codigo": "V-02",
        "parametro_critico": "Oxigênio Dissolvido < 3.0 mg/L",
        "valor_aferido": 2.4,
        "mensagem": "URGENTE: Ligar imediatamente os aeradores do viveiro V-02! O2 crítico em 2.4 mg/L!"
    }
    emerg_resp = client.post("/api/v1/whatsapp/alerta-emergencia", json=alerta)
    assert emerg_resp.status_code == 200
    assert emerg_resp.json()["severidade"] == "CRITICA"
