"""Testes automatizados para o Módulo de Equipe, Vigia Noturno, Escalas e Ocorrências."""
import pytest
from datetime import date, timedelta


def test_criar_e_listar_funcionarios(client):
    """Testa cadastro completo de colaborador com remuneração mista e listagem por fazenda."""
    payload = {
        "nome": "Raimundo Nonato",
        "apelido": "Mundinho",
        "cargo": "Arraçoador de Apoio",
        "telefone": "(84) 99876-2001",
        "whatsapp": "(84) 99876-2001",
        "chave_pix": "mundinho@pix.com",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1600.0,
        "valor_diaria_extra": 75.0,
        "encargos_estimados_pct": 8.0,
        "ativo": True,
        "observacoes": "Contratado para apoio nos viveiros do setor Leste."
    }

    # Criar colaborador
    res = client.post("/api/v1/equipe/funcionarios", json=payload, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res.status_code == 201
    data = res.json()
    assert data["nome"] == "Raimundo Nonato"
    assert data["apelido"] == "Mundinho"
    assert data["salario_base_mensal"] == 1600.0
    assert data["valor_diaria_extra"] == 75.0
    func_id = data["id"]

    # Listar colaboradores
    res_list = client.get("/api/v1/equipe/funcionarios", headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_list.status_code == 200
    funcs = res_list.json()
    assert any(f["id"] == func_id for f in funcs)


def test_apontamento_dia_ocorrencia_e_diaria_extra(client):
    """Testa o registro pontual de ocorrência, falta e diária extra cumprida com valor financeiro."""
    # 1. Cadastrar vigia
    res_func = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Carlos Vigia Teste",
        "apelido": "Carlão",
        "cargo": "Vigia Noturno",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1800.0,
        "valor_diaria_extra": 85.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    func_id = res_func.json()["id"]

    hoje = date.today()

    # 2. Registrar apontamento com diária extra cumprida e observação
    payload_apontamento = {
        "funcionario_id": func_id,
        "data": hoje.isoformat(),
        "turno": "NOTURNO_VIGIA",
        "eh_extra": True,
        "valor_diaria_aplicado": 85.0,
        "status_presenca": "CONFIRMADO",
        "categoria_ocorrencia": "COBERTURA_TURNO",
        "observacoes": "Cobriu plantão noturno emergencial após chuva intensa."
    }
    res_apont = client.post("/api/v1/equipe/escalas/apontamento", json=payload_apontamento, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_apont.status_code == 200
    data_apont = res_apont.json()
    assert data_apont["eh_extra"] is True
    assert data_apont["valor_diaria_aplicado"] == 85.0
    assert data_apont["categoria_ocorrencia"] == "COBERTURA_TURNO"
    assert "emergencial" in data_apont["observacoes"]


def test_template_12x36_vigias(client):
    """Testa a geração de escala 12x36 alternada para 2 vigias noturnos sem sobreposição."""
    # Cadastrar 2 vigias
    res_v1 = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Vigia Um", "cargo": "Vigia Noturno", "tipo_contrato": "MENSALISTA", "salario_base_mensal": 1800.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    v1_id = res_v1.json()["id"]

    res_v2 = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Vigia Dois", "cargo": "Vigia Noturno", "tipo_contrato": "DIARISTA", "salario_base_mensal": 0.0, "valor_diaria_extra": 90.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    v2_id = res_v2.json()["id"]

    ini = date(2026, 11, 1)
    fim = date(2026, 11, 6) # 6 dias

    payload = {
        "tipo_template": "12x36_VIGIAS",
        "data_inicio": ini.isoformat(),
        "data_fim": fim.isoformat(),
        "funcionario_ids": [v1_id, v2_id]
    }
    res_tpl = client.post("/api/v1/equipe/escalas/template-12x36", json=payload, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_tpl.status_code == 200

    # Consultar escala
    res_esc = client.get(f"/api/v1/equipe/escalas?data_inicio={ini.isoformat()}&data_fim={fim.isoformat()}", headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_esc.status_code == 200
    escalas = res_esc.json()

    # Em cada dia deve haver exatamente 1 vigia no turno NOTURNO_VIGIA e o outro em FOLGA
    for d in range(6):
        dt_str = (ini + timedelta(days=d)).isoformat()
        escalas_dia = [e for e in escalas if e["data"] == dt_str and e["funcionario_id"] in (v1_id, v2_id)]
        assert len(escalas_dia) == 2
        turnos = [e["turno"] for e in escalas_dia]
        assert "NOTURNO_VIGIA" in turnos
        assert "FOLGA" in turnos


def test_template_6x1_arracoador(client):
    """Testa a geração de escala 6x1 com folga semanal fixa."""
    res_func = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Tratador 6x1", "cargo": "Arraçoador", "tipo_contrato": "MENSALISTA", "salario_base_mensal": 1500.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    func_id = res_func.json()["id"]

    ini = date(2026, 11, 2)  # Segunda-feira
    fim = date(2026, 11, 8)  # Domingo

    payload = {
        "tipo_template": "6x1_ARRACOADORES",
        "data_inicio": ini.isoformat(),
        "data_fim": fim.isoformat(),
        "funcionario_ids": [func_id],
        "dia_folga_semanal": 6  # Domingo
    }
    res_tpl = client.post("/api/v1/equipe/escalas/template-6x1", json=payload, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_tpl.status_code == 200

    res_esc = client.get(f"/api/v1/equipe/escalas?data_inicio={ini.isoformat()}&data_fim={fim.isoformat()}&funcionario_id={func_id}", headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    escalas = res_esc.json()
    assert len(escalas) == 7

    dias_trabalho = [e for e in escalas if e["turno"] == "DIURNO"]
    dias_folga = [e for e in escalas if e["turno"] == "FOLGA"]
    assert len(dias_trabalho) == 6
    assert len(dias_folga) == 1
    assert dias_folga[0]["data"] == fim.isoformat()


def test_checkin_vigia_noturno(client):
    """Testa registro de check-in e check-out com status de presença."""
    res_func = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Vigia Checkin", "cargo": "Vigia Noturno", "tipo_contrato": "MENSALISTA", "salario_base_mensal": 1800.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    func_id = res_func.json()["id"]

    hoje = date.today()
    res_apont = client.post("/api/v1/equipe/escalas/apontamento", json={
        "funcionario_id": func_id,
        "data": hoje.isoformat(),
        "turno": "NOTURNO_VIGIA",
        "status_presenca": "AGENDADO"
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    escala_id = res_apont.json()["id"]

    # Fazer check-in
    res_check = client.post(f"/api/v1/equipe/escalas/{escala_id}/check-in", json={
        "check_in_hora": "20:55",
        "status_presenca": "CONFIRMADO",
        "observacoes": "Chegou pontual, motores e oxigênio ok."
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_check.status_code == 200
    data = res_check.json()
    assert data["check_in_hora"] == "20:55"
    assert data["status_presenca"] == "CONFIRMADO"


def test_resumo_financeiro_equipe(client):
    """Testa consolidação dos custos da equipe (salários fixos + diárias extras acumuladas)."""
    # 1. Cadastrar 1 mensalista (R$ 2.000) e 1 diarista (R$ 0 fixo + R$ 100 diária)
    f1 = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Mensalista Fixo", "cargo": "Encarregado", "tipo_contrato": "MENSALISTA", "salario_base_mensal": 2000.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"}).json()["id"]

    f2 = client.post("/api/v1/equipe/funcionarios", json={
        "nome": "Diarista Extra", "cargo": "Apoio", "tipo_contrato": "DIARISTA", "salario_base_mensal": 0.0, "valor_diaria_extra": 100.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"}).json()["id"]

    hoje = date.today()

    # Lançar 2 diárias extras para o diarista no mês atual
    client.post("/api/v1/equipe/escalas/apontamento", json={
        "funcionario_id": f2,
        "data": hoje.isoformat(),
        "turno": "DIURNO",
        "eh_extra": True,
        "valor_diaria_aplicado": 100.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})

    d2 = hoje - timedelta(days=2) if hoje.day > 2 else hoje + timedelta(days=2)
    client.post("/api/v1/equipe/escalas/apontamento", json={
        "funcionario_id": f2,
        "data": d2.isoformat(),
        "turno": "DIURNO",
        "eh_extra": True,
        "valor_diaria_aplicado": 100.0
    }, headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})

    # Obter resumo de custos do mês
    res_custos = client.get(f"/api/v1/equipe/resumo-custos?mes={hoje.month}&ano={hoje.year}", headers={"X-Fazenda-Id": "FAZ_ARRENDADA"})
    assert res_custos.status_code == 200
    dados = res_custos.json()

    # Salário fixo >= 2000.0 e diárias extras >= 200.0
    assert dados["total_salarios_fixos"] >= 2000.0
    assert dados["total_diarias_extras"] >= 200.0
    assert dados["custo_total_folha"] == round(dados["total_salarios_fixos"] + dados["total_diarias_extras"], 2)
    assert dados["custo_estimado_por_ha"] > 0
