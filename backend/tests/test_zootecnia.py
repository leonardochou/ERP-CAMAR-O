"""Testes unitários para o motor de fórmulas zootécnicas oficiais da fazenda."""
import pytest
from app.services.zootecnia_service import ZootecniaService


def test_populacao_estimada():
    """Valida o cálculo de população viva com base na estocagem e sobrevivência estimada."""
    # 65.000 PLs estocadas com 85% de sobrevivência estimada
    populacao = ZootecniaService.calcular_populacao_estimada(65000, 85.0)
    assert populacao == 55250

    # Casos de borda: valores nulos ou negativos
    assert ZootecniaService.calcular_populacao_estimada(0, 80.0) == 0
    assert ZootecniaService.calcular_populacao_estimada(50000, 0.0) == 0


def test_biomassa_estimada_kg():
    """Valida o cálculo de biomassa viva em kg: (População * Peso Médio em gramas) / 1000."""
    # 55.250 camarões com 12.1g
    # 55250 * 12.1 / 1000 = 668.525 -> 668.52 kg (banker's rounding)
    biomassa = ZootecniaService.calcular_biomassa_estimada_kg(55250, 12.1)
    assert biomassa == 668.52

    # Erro estrito < 0.01%
    esperado = (55250 * 12.1) / 1000.0
    erro_relativo = abs(biomassa - esperado) / esperado
    assert erro_relativo < 0.0001


def test_fca_parcial():
    """Valida o Fator de Conversão Alimentar Parcial: Ração Acumulada / Biomassa Estimada."""
    # 404 kg de ração ofertada para 668.52 kg de biomassa
    # 404 / 668.52 = 0.6043 -> 0.60
    fca = ZootecniaService.calcular_fca_parcial(404.0, 668.52)
    assert fca == 0.60

    # Divisão por zero ou valores nulos protegidos
    assert ZootecniaService.calcular_fca_parcial(0.0, 500.0) is None
    assert ZootecniaService.calcular_fca_parcial(500.0, 0.0) is None


def test_gmd_ganho_medio_diario():
    """Valida o Ganho Médio Diário em gramas por dia."""
    # Crescimento de 10.0g para 12.1g em 7 dias
    # (12.1 - 10.0) / 7 = 2.1 / 7 = 0.30 g/dia
    gmd = ZootecniaService.calcular_gmd(12.1, 10.0, 7)
    assert gmd == 0.30

    # Primeira pesagem: 3.5g a partir de 0.01g em 25 dias
    # (3.5 - 0.01) / 25 = 3.49 / 25 = 0.1396 -> 0.14 g/dia
    gmd_inicial = ZootecniaService.calcular_gmd(3.5, 0.01, 25)
    assert gmd_inicial == 0.14


def test_fechamento_safra_despesca():
    """Valida os cálculos oficiais de encerramento de lote."""
    # Dados reais típicos de viveiro em Ceará-Mirim:
    # 60.000 PLs estocadas em 0.54 ha (V-06)
    # Colheita: 750 kg colhidos, peso médio final 16.0g
    # Ração total consumida: 900 kg
    sobrevivencia, fca_final, produtividade = ZootecniaService.calcular_fechamento_safra(
        camarao_colhido_kg=750.0,
        peso_final_g=16.0,
        pls_estocadas=60000,
        racao_total_ciclo_kg=900.0,
        area_ha=0.54
    )

    # Camaroes colhidos = 750 * 1000 / 16.0 = 46.875
    # Sobrevivência = 46875 / 60000 * 100 = 78.125% -> 78.12%
    assert sobrevivencia == 78.12

    # FCA Final = 900 / 750 = 1.20
    assert fca_final == 1.20

    # Produtividade = 750 / 0.54 = 1388.888... -> 1388.89 kg/ha
    assert produtividade == 1388.89


def test_classificacao_status_agua():
    """Valida as regras de severidade e detecção de anomalias da água."""
    # Ótimo: O2 >= 4.0, amônia e nitrito baixos
    status = ZootecniaService.classificar_status_agua(
        o2_manha=4.8,
        o2_noite=5.2,
        amonia_mg_l=0.02,
        nitrito_mg_l=0.05
    )
    assert status == "OTIMO"

    # Crítico: O2 < 3.0 (risco iminente de mortandade)
    status_o2 = ZootecniaService.classificar_status_agua(o2_manha=2.6)
    assert status_o2 == "CRITICO"

    # Crítico: Amônia > 0.1 mg/L
    status_amonia = ZootecniaService.classificar_status_agua(
        o2_manha=4.5,
        amonia_mg_l=0.15
    )
    assert status_amonia == "CRITICO"

    # Atenção: O2 entre 3.0 e 3.8 mg/L
    status_atencao = ZootecniaService.classificar_status_agua(o2_manha=3.4)
    assert status_atencao == "ATENCAO"

    # Atenção: Delta pH excessivo (> 0.8)
    status_ph = ZootecniaService.classificar_status_agua(
        o2_manha=4.2,
        delta_ph=0.9
    )
    assert status_ph == "ATENCAO"
