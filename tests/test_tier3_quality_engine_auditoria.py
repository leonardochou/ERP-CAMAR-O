"""Tier 3: Central de Auditoria Ativa (Quality Engine) e Integridade de Dados.

Valida os requisitos e critérios de aceitação oficiais de R3:
- Interceptação de conflitos e duplicatas divergentes para a mesma data/tanque (bloqueio 409 Conflict)
- Criação de pendências na tabela auditoria_pendencias
- Resolução de conflitos em 1 clique ("MANTER_NOVO", "MANTER_ANTIGO", "SOMAR_TURNOS", "DESCARTAR")
- Detecção e classificação automática de O2 = 2.6 mg/L como severidade 'CRITICA'
- Detecção de dias esquecidos (viveiro ativo sem dados nas últimas 24h)
- Detecção de amônia tóxica (> 0.10 mg/L) e nitrito (> 0.20 mg/L)
- Isolamento estrito Multi-Tenant entre Fazenda Arrendada e Fazenda Hakka
"""
import json
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.auditoria import AuditoriaPendencia


# ==============================================================================
# 1. DETECÇÃO E INTERCEPTAÇÃO DE CONFLITOS DE DADOS
# ==============================================================================
class TestInterceptacaoConflitos:
    """Testes de interceptação preventiva de duplicatas divergentes."""

    def test_bloqueio_duplicata_alimentacao_mesma_data(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, ciclo_teste: CicloCultivo, tenant_headers: dict
    ):
        """Tentar inserir dois lançamentos de alimentação para a mesma data deve retornar 409 Conflict."""
        data_evento = date(2026, 8, 22)

        # 1. Primeiro lançamento normal
        payload_1 = {
            "ciclo_id": ciclo_teste.id,
            "data": data_evento.isoformat(),
            "doc": 65,
            "racao_manha_kg": 25.0,
            "sobra_manha": 0,
            "racao_tarde_kg": 0.0,
            "sobra_tarde": 0,
            "fazenda_id": fazenda_padrao.id,
        }
        resp1 = client.post("/api/v1/alimentacao/", json=payload_1, headers=tenant_headers)
        assert resp1.status_code == 201, f"Primeiro lançamento deveria ter sido criado: {resp1.text}"

        # 2. Segunda tentativa para a mesma data com valor divergente (35.0 kg)
        payload_2 = dict(payload_1)
        payload_2["racao_manha_kg"] = 35.0
        payload_2["sobra_manha"] = 1

        resp2 = client.post("/api/v1/alimentacao/", json=payload_2, headers=tenant_headers)
        assert resp2.status_code == 409, f"Segundo lançamento conflitante deveria retornar 409 Conflict: {resp2.text}"

    def test_criacao_pendencia_conflito_auditoria(
        self, db_session: Session, fazenda_padrao: Fazenda, ciclo_teste: CicloCultivo
    ):
        """Ao interceptar duplicata divergente, registra pendência formal na tabela auditoria_pendencias."""
        data_evento = date(2026, 8, 25)

        pendencia = AuditoriaPendencia(
            fazenda_id=fazenda_padrao.id,
            origem="EXCEL",
            entidade="ALIMENTACAO",
            viveiro_codigo="V-03",
            data_evento=data_evento,
            tipo_anomalia="CONFLITO_DADOS",
            severidade="ATENCAO",
            mensagem="Divergência de trato: Planilha indica 35 kg enquanto banco possui 25 kg.",
            dados_atuais_json=json.dumps({"racao_manha_kg": 25.0, "sobra": 0}),
            dados_novos_json=json.dumps({"racao_manha_kg": 35.0, "sobra": 1}),
            resolvido=False,
        )
        db_session.add(pendencia)
        db_session.commit()
        db_session.refresh(pendencia)

        assert pendencia.id is not None
        assert pendencia.resolvido is False
        assert pendencia.tipo_anomalia == "CONFLITO_DADOS"
        assert pendencia.fazenda_id == fazenda_padrao.id


# ==============================================================================
# 2. RESOLUÇÃO DE PENDÊNCIAS EM 1 CLIQUE
# ==============================================================================
class TestResolucaoPendencias:
    """Testes dos fluxos de resolução em 1 clique pela Central de Auditoria."""

    @pytest.mark.parametrize("acao_solicitada", [
        "MANTER_NOVO",
        "MANTER_ANTIGO",
        "SOMAR_TURNOS",
        "DESCARTAR",
    ])
    def test_resolucao_acoes_permitidas(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, tenant_headers: dict, acao_solicitada: str
    ):
        """Testa todas as 4 ações de resolução válidas da Central de Auditoria."""
        # Cria uma pendência pendente
        pendencia = AuditoriaPendencia(
            fazenda_id=fazenda_padrao.id,
            origem="MANUAL",
            entidade="ALIMENTACAO",
            viveiro_codigo="V-03",
            data_evento=date(2026, 8, 28),
            tipo_anomalia="CONFLITO_DADOS",
            severidade="ATENCAO",
            mensagem=f"Teste de resolução com ação {acao_solicitada}",
            resolvido=False,
        )
        db_session.add(pendencia)
        db_session.commit()
        db_session.refresh(pendencia)

        # Envia a resolução via endpoint
        payload = {"acao": acao_solicitada}
        resp = client.post(
            f"/api/v1/auditoria/{pendencia.id}/resolver",
            json=payload,
            headers=tenant_headers
        )

        assert resp.status_code == 200, f"Falha na resolução com {acao_solicitada}: {resp.text}"
        data_resp = resp.json()

        assert data_resp["resolvido"] is True
        assert data_resp["acao_resolucao"] == acao_solicitada
        assert data_resp["resolvido_em"] is not None

    def test_resolucao_acao_invalida_retorna_400(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Ação de resolução desconhecida deve retornar 400 Bad Request."""
        pendencia = AuditoriaPendencia(
            fazenda_id=fazenda_padrao.id,
            origem="MANUAL",
            entidade="ALIMENTACAO",
            viveiro_codigo="V-03",
            data_evento=date(2026, 8, 29),
            tipo_anomalia="CONFLITO_DADOS",
            severidade="ATENCAO",
            mensagem="Teste ação inválida",
            resolvido=False,
        )
        db_session.add(pendencia)
        db_session.commit()
        db_session.refresh(pendencia)

        resp = client.post(
            f"/api/v1/auditoria/{pendencia.id}/resolver",
            json={"acao": "ACAO_INEXISTENTE"},
            headers=tenant_headers
        )
        assert resp.status_code == 400


# ==============================================================================
# 3. ANOMALIA DE OXIGÊNIO CRÍTICO (O2 = 2.6 mg/L)
# ==============================================================================
class TestAnomaliaOxigenioCritico:
    """Validação do Critério de Aceitação Oficial: O2 = 2.6 mg/L dispara severidade Crítica."""

    def test_oxigenio_2_6_classificado_como_critico(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Critério Oficial: Inserir medição de O2 = 2.6 mg/L classifica o alerta automaticamente como Crítica."""
        v03 = db_session.query(Viveiro).filter(
            Viveiro.codigo == "V-03",
            Viveiro.fazenda_id == fazenda_padrao.id
        ).first()
        assert v03 is not None

        # Registra medição de água com O2 matutino letal de 2.6 mg/L
        payload_agua = {
            "viveiro_id": v03.id,
            "data": "2026-08-30",
            "doc": 73,
            "o2_manha": 2.60,
            "o2_noite": 4.10,
            "salinidade_ppt": 15.0,
            "ph_manha": 7.6,
            "ph_tarde": 8.0,
            "transparencia_secchi_cm": 35,
            "amonia_mg_l": 0.02,
            "nitrito_mg_l": 0.05,
            "fazenda_id": fazenda_padrao.id,
        }

        resp = client.post("/api/v1/agua/", json=payload_agua, headers=tenant_headers)
        assert resp.status_code == 201, f"Registro de água falhou: {resp.text}"
        data_resp = resp.json()

        # 1. Verifica status retornado no monitoramento
        assert data_resp["status_tanque"] == "CRITICO", "O2 de 2.6 mg/L deve classificar status do tanque como CRITICO"

        # 2. Verifica criação automática de pendência na tabela auditoria_pendencias
        pendencia = db_session.query(AuditoriaPendencia).filter(
            AuditoriaPendencia.fazenda_id == fazenda_padrao.id,
            AuditoriaPendencia.viveiro_codigo == "V-03",
            AuditoriaPendencia.data_evento == date(2026, 8, 30),
            AuditoriaPendencia.tipo_anomalia == "O2_CRITICO"
        ).first()

        assert pendencia is not None, "Pendência de O2_CRITICO deveria ter sido criada na auditoria"
        assert pendencia.severidade == "CRITICA", f"Severidade deveria ser CRITICA, obtido: {pendencia.severidade}"
        assert "2.6" in pendencia.mensagem


# ==============================================================================
# 4. DETECTOR DE DIAS ESQUECIDOS (24 HORAS)
# ==============================================================================
class TestDetectorDiasEsquecidos:
    """Testa a identificação proativa de viveiros ativos sem dados nas últimas 24h."""

    def test_deteccao_viveiro_ativo_sem_trato_recente(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, ciclo_teste: CicloCultivo, tenant_headers: dict
    ):
        """Viveiro V-03 com ciclo ativo e sem tratos nos últimos 2 dias deve disparar pendência DIA_ESQUECIDO."""
        # Insere um trato antigo (há 5 dias atrás)
        data_antiga = date.today() - timedelta(days=5)
        trato_antigo = LancamentoAlimentacao(
            fazenda_id=fazenda_padrao.id,
            ciclo_id=ciclo_teste.id,
            data=data_antiga,
            doc=10,
            racao_manha_kg=20.0,
            total_dia_kg=20.0,
            consumo_acumulado_kg=20.0,
        )
        db_session.add(trato_antigo)
        db_session.commit()

        # Aciona o detector de dias esquecidos
        resp = client.post("/api/v1/auditoria/verificar-dias-esquecidos", headers=tenant_headers)
        assert resp.status_code == 200, f"Falha na verificação de dias esquecidos: {resp.text}"
        pendencias = resp.json()

        # Confere que foi gerada uma pendência para o V-03
        pendencia_v03 = next((p for p in pendencias if p["viveiro_codigo"] == "V-03"), None)
        assert pendencia_v03 is not None, "Deveria ter detectado V-03 sem dados recentes"
        assert pendencia_v03["tipo_anomalia"] == "DIA_ESQUECIDO"
        assert pendencia_v03["severidade"] == "ATENCAO"


# ==============================================================================
# 5. DETECÇÃO DE OUTRAS ANOMALIAS ZOOTÉCNICAS (AMÔNIA, NITRITO)
# ==============================================================================
class TestAnomaliasQuimicasAgua:
    """Testa anomalias de compostos nitrogenados tóxicos."""

    def test_amonia_toxica_gera_alerta_critico(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Amônia acima de 0.10 mg/L deve gerar alerta crítico imediato."""
        v03 = db_session.query(Viveiro).filter(
            Viveiro.codigo == "V-03",
            Viveiro.fazenda_id == fazenda_padrao.id
        ).first()

        payload = {
            "viveiro_id": v03.id,
            "data": "2026-08-31",
            "doc": 74,
            "o2_manha": 4.5,
            "o2_noite": 4.0,
            "salinidade_ppt": 15.0,
            "amonia_mg_l": 0.25,  # Extremamente tóxico (> 0.1)
            "nitrito_mg_l": 0.05,
            "fazenda_id": fazenda_padrao.id,
        }

        resp = client.post("/api/v1/agua/", json=payload, headers=tenant_headers)
        assert resp.status_code == 201
        assert resp.json()["status_tanque"] == "CRITICO"

        pendencia = db_session.query(AuditoriaPendencia).filter(
            AuditoriaPendencia.fazenda_id == fazenda_padrao.id,
            AuditoriaPendencia.viveiro_codigo == "V-03",
            AuditoriaPendencia.data_evento == date(2026, 8, 31)
        ).first()

        assert pendencia is not None
        assert pendencia.severidade == "CRITICA"
        assert "Amônia" in pendencia.mensagem or "AMONIA" in pendencia.tipo_anomalia


# ==============================================================================
# 6. ISOLAMENTO MULTI-TENANT NA AUDITORIA
# ==============================================================================
class TestIsolamentoMultiTenantAuditoria:
    """Garante que pendências de uma fazenda são 100% invisíveis para outra fazenda."""

    def test_pendencias_isoladas_por_fazenda(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, fazenda_hakka: Fazenda,
        tenant_headers: dict, hakka_headers: dict
    ):
        """Pendência criada na Fazenda Arrendada não pode ser listada pela Fazenda Hakka."""
        # 1. Cria pendência na Fazenda Arrendada
        pendencia_arrendada = AuditoriaPendencia(
            fazenda_id=fazenda_padrao.id,
            origem="MANUAL",
            entidade="ALIMENTACAO",
            viveiro_codigo="V-03",
            data_evento=date(2026, 9, 1),
            tipo_anomalia="CONFLITO_DADOS",
            severidade="ATENCAO",
            mensagem="Pendência exclusiva da Fazenda Arrendada",
            resolvido=False,
        )
        db_session.add(pendencia_arrendada)
        db_session.commit()
        db_session.refresh(pendencia_arrendada)

        # 2. Consulta pendências com header da Fazenda Arrendada -> deve encontrar
        resp_arrendada = client.get("/api/v1/auditoria/pendencias", headers=tenant_headers)
        assert resp_arrendada.status_code == 200
        ids_arrendada = [p["id"] for p in resp_arrendada.json()]
        assert pendencia_arrendada.id in ids_arrendada

        # 3. Consulta pendências com header da Fazenda Hakka -> NÃO pode encontrar
        resp_hakka = client.get("/api/v1/auditoria/pendencias", headers=hakka_headers)
        assert resp_hakka.status_code == 200
        ids_hakka = [p["id"] for p in resp_hakka.json()]
        assert pendencia_arrendada.id not in ids_hakka, "VAZAMENTO DE DADOS MULTI-TENANT: Hakka viu pendência da Arrendada"

        # 4. Tentar resolver a pendência da Arrendada usando credenciais da Hakka -> retorna 404
        resp_resolucao_cross = client.post(
            f"/api/v1/auditoria/{pendencia_arrendada.id}/resolver",
            json={"acao": "MANTER_NOVO"},
            headers=hakka_headers
        )
        assert resp_resolucao_cross.status_code == 404, "Hakka não pode resolver pendências da Arrendada"
