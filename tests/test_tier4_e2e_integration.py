"""Tier 4: Fluxo de Integração E2E Completo, Camadas Macro/Micro e Multi-Tenant.

Valida a jornada operacional completa de ponta a ponta:
1. Cadastro Topográfico dos 15 Viveiros na Fazenda Arrendada
2. Abertura de Ciclo de Cultivo e Povoamento de PLs
3. Lançamentos Diários de Arraçoamento e Monitoramento de Água
4. Registro de Biometrias e Recálculo Automático de Biomassa e FCA Parcial
5. Fechamento de Safra (Despesca) com Sobrevivência Real, FCA Final e Faturamento
6. Dashboard Executivo da Camada Macro e Camada Micro do Viveiro
7. Mapa Interativo 2D dos 15 Viveiros com Status por Cor (OTIMO, ATENCAO, CRITICO, VAZIO)
8. Webhook do Assistente WhatsApp (extração, confirmação e alerta de emergência noturno)
9. Chaveamento e Isolamento Multi-Tenant Completo (Fazenda Arrendada vs Fazenda Hakka)
"""
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.despesca import DespescaVenda


# ==============================================================================
# 1. FLUXO COMPLETO DO CICLO DE VIDA (DESDE O POVOAMENTO ATÉ A DESPESCA)
# ==============================================================================
class TestCicloDeVidaCompletoE2E:
    """Testa a sequência transacional completa de uma safra de camarão."""

    def test_jornada_completa_povoamento_ao_fechamento(
        self, client: TestClient, db_session: Session,
        fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Executa a esteira zootécnica completa: Povoamento -> Manejo -> Biometria -> Despesca."""
        # 1. Confere que o Viveiro V-03 existe na Fazenda Arrendada
        resp_viv = client.get("/api/v1/viveiros/V-03", headers=tenant_headers)
        assert resp_viv.status_code == 200
        viv_data = resp_viv.json()
        viveiro_id = viv_data["id"]
        assert viv_data["codigo"] == "V-03"

        # 2. Abre um novo ciclo de cultivo para o V-03
        payload_ciclo = {
            "viveiro_id": viveiro_id,
            "numero_lote": "SAFRA-2026-V03-E2E",
            "data_povoamento": "2026-06-19",
            "pls_estocadas": 65000,
            "laboratorio": "NE",
            "peso_inicial_g": 0.01,
            "observacoes": "Lote E2E para validação completa",
            "fazenda_id": fazenda_padrao.id,
        }
        resp_ciclo = client.post("/api/v1/ciclos/", json=payload_ciclo, headers=tenant_headers)
        assert resp_ciclo.status_code == 201, f"Falha ao abrir ciclo: {resp_ciclo.text}"
        ciclo_id = resp_ciclo.json()["id"]

        # 3. Registra 3 dias consecutivos de arraçoamento
        for i, dt_str in enumerate(["2026-06-20", "2026-06-21", "2026-06-22"], start=1):
            payload_trato = {
                "ciclo_id": ciclo_id,
                "data": dt_str,
                "doc": i,
                "racao_manha_kg": 6.0,
                "sobra_manha": 0,
                "racao_tarde_kg": 6.0,
                "sobra_tarde": 0,
                "fazenda_id": fazenda_padrao.id,
            }
            resp_trato = client.post("/api/v1/alimentacao/", json=payload_trato, headers=tenant_headers)
            assert resp_trato.status_code == 201, f"Falha no trato dia {i}: {resp_trato.text}"
            assert resp_trato.json()["total_dia_kg"] == 12.0
            assert resp_trato.json()["consumo_acumulado_kg"] == round(12.0 * i, 2)

        # 4. Registra medição físico-química da água em condição ótima
        payload_agua = {
            "viveiro_id": viveiro_id,
            "data": "2026-06-22",
            "doc": 3,
            "o2_manha": 4.5,
            "o2_noite": 4.0,
            "salinidade_ppt": 16.0,
            "ph_manha": 7.7,
            "ph_tarde": 8.1,
            "transparencia_secchi_cm": 35,
            "amonia_mg_l": 0.02,
            "nitrito_mg_l": 0.03,
            "fazenda_id": fazenda_padrao.id,
        }
        resp_agua = client.post("/api/v1/agua/", json=payload_agua, headers=tenant_headers)
        assert resp_agua.status_code == 201
        assert resp_agua.json()["status_tanque"] == "OTIMO"

        # 5. Registra 1ª Biometria de amostragem (DOC 65 com peso de 11.21g)
        payload_bio = {
            "ciclo_id": ciclo_id,
            "data": "2026-08-22",
            "doc": 65,
            "peso_medio_g": 11.21,
            "amostras_pesadas_qtd": 150,
            "sobrevivencia_estimada_pct": 85.0,
            "fazenda_id": fazenda_padrao.id,
        }
        resp_bio = client.post("/api/v1/biometrias/", json=payload_bio, headers=tenant_headers)
        assert resp_bio.status_code == 201, f"Falha na biometria: {resp_bio.text}"
        bio_data = resp_bio.json()

        # Validação do cálculo automático
        # População estimada: 65.000 * 0.85 = 55.250
        # Biomassa estimada: (55.250 * 11.21) / 1000 = 619.35 kg
        assert bio_data["populacao_estimada"] == 55250
        assert abs(bio_data["biomassa_estimada_kg"] - 619.35) <= 0.05
        assert bio_data["gmd_g_dia"] is not None

        # 6. Registra a Venda Comercial da Despesca
        payload_venda = {
            "ciclo_id": ciclo_id,
            "data": "2026-09-30",
            "gramatura_media_g": 14.50,
            "camarao_colhido_kg": 850.0,
            "preco_kg_rs": 24.50,
            "tipo_despesca": "TOTAL",
            "comprador": "Frutos do Mar Potiguar Ltda",
            "fazenda_id": fazenda_padrao.id,
        }
        resp_venda = client.post("/api/v1/despescas/", json=payload_venda, headers=tenant_headers)
        assert resp_venda.status_code == 201, f"Falha no registro da venda: {resp_venda.text}"
        venda_data = resp_venda.json()
        assert venda_data["faturamento_bruto_rs"] == round(850.0 * 24.50, 2)

        # 7. Realiza o Fechamento Zootécnico de Safra no Ciclo
        payload_fechamento = {
            "data_despesca": "2026-09-30",
            "camarao_colhido_kg": 850.0,
            "peso_final_g": 14.50,
            "faturamento_total_rs": round(850.0 * 24.50, 2),
            "observacoes": "Fechamento de lote com excelente conversão alimentar",
        }
        resp_fechar = client.post(f"/api/v1/ciclos/{ciclo_id}/fechar", json=payload_fechamento, headers=tenant_headers)
        assert resp_fechar.status_code == 200, f"Falha no fechamento de safra: {resp_fechar.text}"
        ciclo_fechado = resp_fechar.json()

        # Validações zootécnicas oficiais de encerramento
        # Camarões colhidos = (850 * 1000) / 14.5 = 58.620 camarões
        # Sobrevivência real = 58.620 / 65.000 = 90.19%
        assert ciclo_fechado["status"] == "DESPESCADO"
        assert abs(ciclo_fechado["sobrevivencia_real_pct"] - 90.19) <= 0.05
        assert ciclo_fechado["faturamento_total_rs"] == round(850.0 * 24.50, 2)



# ==============================================================================
# 2. MAPA INTERATIVO 2D DOS 15 VIVEIROS (CAMADA MACRO PWA)
# ==============================================================================
class TestMapaInterativoMacro:
    """Valida o endpoint que alimenta a visão aérea dos 15 tanques no frontend PWA."""

    def test_mapa_retorna_todos_os_15_viveiros(
        self, client: TestClient, fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Garante que a rota /api/v1/viveiros/mapa entrega o inventário dos 15 viveiros com status de cor."""
        resp = client.get("/api/v1/viveiros/mapa", headers=tenant_headers)
        assert resp.status_code == 200, f"Falha ao obter mapa: {resp.text}"
        itens_mapa = resp.json()

        assert len(itens_mapa) == 15, f"Esperava 15 tanques no mapa, retornou {len(itens_mapa)}"

        codigos = [item["codigo"] for item in itens_mapa]
        for num in range(1, 16):
            cod_esperado = f"V-{num:02d}"
            assert cod_esperado in codigos, f"Viveiro {cod_esperado} ausente no mapa"

        # Verifica atributos essenciais de cada item do mapa
        for item in itens_mapa:
            assert item["setor"] in ["Norte", "Oeste", "Central", "Leste"]
            assert item["area_ha"] > 0
            assert item["status_cor"] in ["OTIMO", "ATENCAO", "CRITICO", "VAZIO"]


# ==============================================================================
# 3. CAMADAS MACRO E MICRO DE RELATÓRIOS EXECUTIVOS
# ==============================================================================
class TestRelatoriosExecutivosMacroMicro:
    """Testa os serviços de agregação de KPIs para gestores e operadores."""

    def test_resumo_executivo_camada_macro(
        self, client: TestClient, fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Valida os KPIs consolidados: total de tanques, biomassa total, status e fazenda."""
        resp = client.get("/api/v1/relatorios/resumo-executivo", headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_viveiros"] == 15
        assert data["fazenda"]["codigo"] == "FAZ_ARRENDADA"
        assert "biomassa_total_viva_kg" in data
        assert "fca_ponderado_global" in data
        assert "distribuicao_status" in data

    def test_dashboard_camada_micro_viveiro(
        self, client: TestClient, fazenda_padrao: Fazenda,
        ciclo_teste: CicloCultivo, tenant_headers: dict
    ):
        """Valida a entrega dos dados da Camada Micro para o tanque V-03."""
        resp = client.get("/api/v1/relatorios/viveiro/V-03/dashboard", headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["viveiro"]["codigo"] == "V-03"
        assert "serie_agua" in data
        assert "serie_biometria" in data
        assert "serie_alimentacao" in data
        assert "ciclo_ativo" in data


# ==============================================================================
# 4. ASSISTENTE WHATSAPP COM IA (VOZ/TEXTO E ALERTA NOTURNO)
# ==============================================================================
class TestAssistenteWhatsApp:
    """Testa os webhooks do assistente de campo via WhatsApp."""

    def test_webhook_recepcao_mensagem_operador(
        self, client: TestClient, fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Simula mensagem de campo: 'Viveiro 03 trato da manha 15 kg bandejas limpas'."""
        payload = {
            "remetente": "+5584999990001",
            "texto": "Tanque V-03 medição matutina de 15 kg com bandejas limpas",
            "fazenda_id": fazenda_padrao.id,
        }

        resp = client.post("/api/v1/whatsapp/webhook", json=payload, headers=tenant_headers)
        assert resp.status_code == 200, f"Falha no webhook WhatsApp: {resp.text}"
        data = resp.json()

        assert data["status"] == "recebido"
        assert data["fazenda"] == "FAZ_ARRENDADA"
        assert "pendencia_id" in data
        assert "V-03" in data["mensagem_confirmacao"]

    def test_webhook_alerta_emergencia_noturno_vigia(
        self, client: TestClient, fazenda_padrao: Fazenda, tenant_headers: dict
    ):
        """Simula disparo de emergência noturna para vigia se O2 < 3.0 mg/L."""
        payload = {
            "destinatario": "+5584988887777",
            "viveiro_codigo": "V-08",
            "parametro_critico": "Oxigênio Dissolvido < 3.0 mg/L",
            "valor_aferido": 2.4,
            "mensagem": "🚨 EMERGÊNCIA NO VIVEIRO V-08! O2 registrado em 2.4 mg/L às 03:15. Ligar aerador reserva imediatamente!",
            "fazenda_id": fazenda_padrao.id,
        }
        resp = client.post("/api/v1/whatsapp/alerta-emergencia", json=payload, headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "alerta_disparado"
        assert data["severidade"] == "CRITICA"
        assert data["viveiro"] == "V-08"


# ==============================================================================
# 5. CHAVEAMENTO E ISOLAMENTO MULTI-TENANT (ARRENDADA VS HAKKA)
# ==============================================================================
class TestChaveamentoMultiTenantE2E:
    """Valida o chaveamento dinâmico entre Fazenda Arrendada e Fazenda Hakka."""

    def test_listagem_fazendas_ativas_e_configuracao(self, client: TestClient):
        """Endpoint /api/v1/fazendas lista as propriedades cadastradas."""
        resp = client.get("/api/v1/fazendas/")
        assert resp.status_code == 200
        fazendas = resp.json()

        codigos = [f["codigo"] for f in fazendas]
        assert "FAZ_ARRENDADA" in codigos, "Fazenda Arrendada deve estar presente"
        assert "FAZ_HAKKA" in codigos, "Fazenda Hakka deve estar presente"

    def test_isolamento_viveiros_entre_tenants(
        self, client: TestClient, db_session: Session,
        tenant_headers: dict, hakka_headers: dict
    ):
        """Fazenda Arrendada tem 15 tanques; Fazenda Hakka inicia com 0 tanques cadastrados."""
        # Consulta Arrendada
        resp_arr = client.get("/api/v1/viveiros/", headers=tenant_headers)
        assert resp_arr.status_code == 200
        assert len(resp_arr.json()) == 15

        # Consulta Hakka
        resp_hak = client.get("/api/v1/viveiros/", headers=hakka_headers)
        assert resp_hak.status_code == 200
        assert len(resp_hak.json()) == 0, "Fazenda Hakka deve iniciar sem viveiros"

    def test_cadastrar_novo_tanque_na_fazenda_hakka(
        self, client: TestClient, fazenda_hakka: Fazenda,
        tenant_headers: dict, hakka_headers: dict
    ):
        """Cadastrar um novo tanque na Fazenda Hakka não afeta a Fazenda Arrendada."""
        payload_hakka_tanque = {
            "codigo": "H-01",
            "nome_operacional": "Tanque Piloto Hakka 1",
            "setor": "Setor Sul",
            "area_m2": 10000.0,
            "area_ha": 1.0,
            "profundidade_media_m": 1.20,
            "volume_m3": 12000.0,
            "tipo_uso": "Engorda",
            "fazenda_id": fazenda_hakka.id,
        }
        resp = client.post("/api/v1/viveiros/", json=payload_hakka_tanque, headers=hakka_headers)
        assert resp.status_code == 201
        assert resp.json()["codigo"] == "H-01"

        # Confere que a Fazenda Hakka agora tem 1 viveiro
        resp_hak = client.get("/api/v1/viveiros/", headers=hakka_headers)
        assert len(resp_hak.json()) == 1

        # Confere que a Fazenda Arrendada continua com seus 15 viveiros inalterados
        resp_arr = client.get("/api/v1/viveiros/", headers=tenant_headers)
        assert len(resp_arr.json()) == 15
        codigos_arr = [v["codigo"] for v in resp_arr.json()]
        assert "H-01" not in codigos_arr, "Tanque da Hakka vazou para a Fazenda Arrendada!"
