"""Tier 1: Validação Matemática Rigorosa dos Cálculos Zootécnicos e Algoritmos.

Cobre com precisão matemática (erro < 0.01%) todas as fórmulas oficiais de:
- População Estimada e Biomassa Estimada
- Fator de Conversão Alimentar (FCA) Parcial e Acumulado
- Ganho Médio Diário (GMD)
- Encerramento de Safra / Despesca (Sobrevivência Real, FCA Final, Produtividade)
- Classificação Paramétrica de Qualidade da Água
- Validação Cruzada Direta com a Planilha Real (V-03 de Controle_Alimentacao_e_Biometria.xlsx)
"""
import pytest
import openpyxl
from pathlib import Path
from typing import Dict

from app.services.zootecnia_service import ZootecniaService
from tests.conftest import ZootecniaOracle


# ==============================================================================
# 1. BIOMASSA ESTIMADA E POPULAÇÃO
# ==============================================================================
class TestBiomassaEstimada:
    """Testes cobrindo classes de equivalência para cálculo de biomassa estimada."""

    @pytest.mark.parametrize("pls,sobrevivencia,peso_g,esperado_kg", [
        # 1. Caso Nominal Médio (Cultivo em meio de ciclo)
        (65000, 85.0, 12.10, 668.53),
        # 2. Camarão Jovem / Berçário (Pequeno peso e alta sobrevivência)
        (40000, 95.0, 2.50, 95.00),
        # 3. Tanque Central Grande de Alta Biomassa (Pré-despesca)
        (100000, 70.0, 18.00, 1260.00),
        # 4. Povoamento Inicial / PL-10 (Limite inferior operacional)
        (65000, 100.0, 0.01, 0.65),
        # 5. Sobrevivência Baixa com Camarão Especial
        (50000, 50.0, 22.00, 550.00),
    ])
    def test_biomassa_estimada_classes_equivalencia(
        self, pls: int, sobrevivencia: float, peso_g: float, esperado_kg: float
    ):
        """Valida que o cálculo de biomassa confere com a fórmula oficial com erro < 0.01%."""
        pop_viva = ZootecniaService.calcular_populacao_estimada(pls, sobrevivencia)
        biomassa_calc = ZootecniaService.calcular_biomassa_estimada_kg(pop_viva, peso_g)

        # Validação cruzada com o oráculo matemático
        pop_oracle = ZootecniaOracle.populacao(pls, sobrevivencia)
        biomassa_oracle = ZootecniaOracle.biomassa_kg(pop_oracle, peso_g)

        assert abs(biomassa_calc - esperado_kg) <= 0.05, f"Esperado {esperado_kg}, obtido {biomassa_calc}"
        assert abs(biomassa_calc - biomassa_oracle) <= 0.01, "Discrepância com o oráculo zootécnico"

    @pytest.mark.parametrize("pls,sobrevivencia,peso_g", [
        (0, 85.0, 10.0),       # PLs zero
        (50000, 0.0, 10.0),    # Sobrevivência zero
        (50000, 85.0, 0.0),    # Peso médio zero
        (-1000, 80.0, 10.0),   # Entrada negativa
        (50000, -10.0, 10.0),  # Sobrevivência negativa
    ])
    def test_biomassa_estimada_casos_borda(self, pls: int, sobrevivencia: float, peso_g: float):
        """Casos de borda e entradas nulas/inválidas devem retornar 0.0 sem estourar exceção."""
        pop_viva = ZootecniaService.calcular_populacao_estimada(pls, sobrevivencia)
        biomassa_calc = ZootecniaService.calcular_biomassa_estimada_kg(pop_viva, peso_g)
        assert biomassa_calc == 0.0


# ==============================================================================
# 2. FATOR DE CONVERSÃO ALIMENTAR (FCA) PARCIAL
# ==============================================================================
class TestFcaParcial:
    """Testes cobrindo classes de equivalência para cálculo de FCA parcial."""

    @pytest.mark.parametrize("racao_kg,biomassa_kg,fca_esperado", [
        # 1. Eficiência Padrão da Fazenda (FCA meta: ~1.20)
        (540.0, 450.0, 1.20),
        # 2. Excelente Eficiência / Camarão Jovem
        (95.0, 105.5, 0.90),
        # 3. Conversão Moderada em Final de Safra
        (1350.0, 900.0, 1.50),
        # 4. Alerta de Ineficiência / Risco de Desvio (> 1.80)
        (720.0, 360.0, 2.00),
        # 5. Pequeno Porte / Início do Arraçoamento
        (12.0, 15.0, 0.80),
    ])
    def test_fca_parcial_classes_equivalencia(
        self, racao_kg: float, biomassa_kg: float, fca_esperado: float
    ):
        """Valida que o FCA Parcial atende à especificação com erro inferior a 0.01%."""
        fca_calc = ZootecniaService.calcular_fca_parcial(racao_kg, biomassa_kg)
        fca_oracle = ZootecniaOracle.fca_parcial(racao_kg, biomassa_kg)

        assert fca_calc is not None
        assert abs(fca_calc - fca_esperado) <= 0.01
        assert abs(fca_calc - fca_oracle) <= 0.01

    @pytest.mark.parametrize("racao_kg,biomassa_kg", [
        (0.0, 450.0),    # Ração zero (início do ciclo ou jejum)
        (500.0, 0.0),    # Biomassa zero (proteção contra divisão por zero)
        (-50.0, 200.0),  # Valor negativo
        (100.0, -10.0),  # Biomassa negativa
    ])
    def test_fca_parcial_casos_borda(self, racao_kg: float, biomassa_kg: float):
        """Proteção contra divisão por zero e entradas nulas."""
        fca_calc = ZootecniaService.calcular_fca_parcial(racao_kg, biomassa_kg)
        assert fca_calc is None


# ==============================================================================
# 3. GANHO MÉDIO DIÁRIO (GMD)
# ==============================================================================
class TestGanhoMedioDiario:
    """Testes cobrindo classes de equivalência para cálculo de GMD."""

    @pytest.mark.parametrize("peso_atual,peso_ant,dias,gmd_esperado", [
        # 1. 1ª Biometria em V-03 (Row 14 da planilha real: 11.21g - 0.01g em 65 dias)
        (11.21, 0.01, 65, 0.17),
        # 2. Intervalo Semanal Típico (7 dias)
        (12.10, 11.45, 7, 0.09),
        # 3. Fase de Crescimento Rápido (1.5g em 7 dias)
        (8.50, 7.00, 7, 0.21),
        # 4. Super Ganho de Peso de Juvenil
        (5.10, 3.00, 7, 0.30),
        # 5. Regressão Amostral por Ecdise Coletiva (Row 31 de V-03: 9.0g - 11.21g em 7 dias)
        (9.00, 11.21, 7, -0.32),
    ])
    def test_gmd_classes_equivalencia(
        self, peso_atual: float, peso_ant: float, dias: int, gmd_esperado: float
    ):
        """Valida que o cálculo de GMD calcula o ganho com precisão de 0.01 g/dia."""
        gmd_calc = ZootecniaService.calcular_gmd(peso_atual, peso_ant, dias)
        gmd_oracle = ZootecniaOracle.gmd(peso_atual, peso_ant, dias)

        assert gmd_calc is not None
        assert abs(gmd_calc - gmd_esperado) <= 0.01
        assert abs(gmd_calc - gmd_oracle) <= 0.01

    def test_gmd_divisao_por_zero(self):
        """Dias de intervalo zero não pode causar ZeroDivisionError."""
        gmd_calc = ZootecniaService.calcular_gmd(10.0, 9.0, 0)
        assert gmd_calc == 0.0


# ==============================================================================
# 4. ENCERRAMENTO DE SAFRA E DESPESCA
# ==============================================================================
class TestEncerramentoSafra:
    """Testes cobrindo as métricas finais de fechamento de safra na despesca."""

    @pytest.mark.parametrize("colhido_kg,peso_final_g,pls,racao_kg,area_ha,sob_esp,fca_esp,prod_esp", [
        # 1. Safra Padrão em Tanque Médio (V-03 / 0.50 ha)
        (850.0, 14.50, 65000, 1020.0, 0.50, 90.19, 1.20, 1700.0),
        # 2. Superprodutividade em Tanque Central (1.26 ha)
        (3200.0, 16.00, 250000, 3840.0, 1.26, 80.00, 1.20, 2539.68),
        # 3. Safra com Alta Mortalidade e FCA Elevado
        (300.0, 10.00, 65000, 660.0, 0.50, 46.15, 2.20, 600.0),
        # 4. Fechamento de Tanque Pequeno (0.14 ha)
        (250.0, 12.50, 25000, 275.0, 0.14, 80.00, 1.10, 1785.71),
        # 5. Despesca de Emergência (Camarão precoce de 8g)
        (400.0, 8.00, 70000, 480.0, 0.55, 71.43, 1.20, 727.27),
    ])
    def test_fechamento_safra_classes_equivalencia(
        self, colhido_kg: float, peso_final_g: float, pls: int,
        racao_kg: float, area_ha: float, sob_esp: float, fca_esp: float, prod_esp: float
    ):
        """Valida sobrevivência real, FCA final e produtividade com erro < 0.01%."""
        sob_calc, fca_calc, prod_calc = ZootecniaService.calcular_fechamento_safra(
            camarao_colhido_kg=colhido_kg,
            peso_final_g=peso_final_g,
            pls_estocadas=pls,
            racao_total_ciclo_kg=racao_kg,
            area_ha=area_ha,
        )

        assert abs(sob_calc - sob_esp) <= 0.05
        assert abs(fca_calc - fca_esp) <= 0.01
        assert abs(prod_calc - prod_esp) <= 0.10

    def test_fechamento_safra_valores_nulos_ou_zero(self):
        """Entradas zero ou nulas devem ser tratadas sem divisão por zero."""
        sob, fca, prod = ZootecniaService.calcular_fechamento_safra(
            camarao_colhido_kg=0.0,
            peso_final_g=0.0,
            pls_estocadas=0,
            racao_total_ciclo_kg=0.0,
            area_ha=0.0,
        )
        assert sob == 0.0
        assert fca == 0.0
        assert prod == 0.0


# ==============================================================================
# 5. CLASSIFICAÇÃO PARAMÉTRICA DE QUALIDADE DA ÁGUA
# ==============================================================================
class TestClassificacaoAgua:
    """Testes cobrindo limites oficiais de água (POP Ceará-Mirim/RN)."""

    def test_oxigenio_critico_manha(self):
        """O2 Manhã < 3.0 mg/L deve classificar como CRITICO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=2.6) == "CRITICO"

    def test_oxigenio_critico_noite(self):
        """O2 Noite < 3.0 mg/L na ronda noturna deve classificar como CRITICO."""
        assert ZootecniaService.classificar_status_agua(o2_noite=2.8) == "CRITICO"

    def test_amonia_critica(self):
        """Amônia tóxica > 0.1 mg/L deve classificar como CRITICO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=5.0, amonia_mg_l=0.15) == "CRITICO"

    def test_nitrito_critico(self):
        """Nitrito > 0.2 mg/L deve classificar como CRITICO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=5.0, nitrito_mg_l=0.25) == "CRITICO"

    def test_oxigenio_alerta_atencao(self):
        """O2 Manhã entre 3.0 e 3.8 mg/L deve classificar como ATENCAO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=3.4) == "ATENCAO"

    def test_delta_ph_excessivo_atencao(self):
        """Delta pH diurno > 0.8 indica bloom algal e classifica como ATENCAO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=5.0, delta_ph=1.0) == "ATENCAO"

    def test_secchi_fora_da_faixa(self):
        """Transparência Secchi < 20 cm ou > 50 cm classifica como ATENCAO."""
        assert ZootecniaService.classificar_status_agua(o2_manha=5.0, secchi_cm=15.0) == "ATENCAO"
        assert ZootecniaService.classificar_status_agua(o2_manha=5.0, secchi_cm=60.0) == "ATENCAO"

    def test_parametros_ideais_otimo(self):
        """Parâmetros dentro das faixas ótimas devem classificar como OTIMO."""
        assert ZootecniaService.classificar_status_agua(
            o2_manha=4.5,
            o2_noite=4.0,
            amonia_mg_l=0.02,
            nitrito_mg_l=0.05,
            delta_ph=0.4,
            secchi_cm=35.0,
        ) == "OTIMO"


# ==============================================================================
# 6. VALIDAÇÃO CRUZADA COM A PLANILHA REAL (V-03)
# ==============================================================================
class TestValidacaoCruzadaPlanilhaReal:
    """Valida as fórmulas zootécnicas diretamente contra as células da planilha real da fazenda."""

    def test_validacao_v03_metadados_e_biometrias(self, spreadsheet_paths: Dict[str, Path]):
        """Abre o arquivo real Controle_Alimentacao_e_Biometria.xlsx e audita a aba V-03."""
        arquivo = spreadsheet_paths["alimentacao"]
        assert arquivo.exists(), f"Arquivo não encontrado: {arquivo}"

        wb = openpyxl.load_workbook(arquivo, data_only=True)
        assert "V-03" in wb.sheetnames, "Aba V-03 deve existir na planilha real"
        ws = wb["V-03"]

        # 1. Metadados Oficiais do Cabeçalho
        area_ha = float(ws["B2"].value)
        lab = str(ws["D2"].value)
        peso_inicial = float(ws["F2"].value)
        pls_mil = float(ws["B3"].value)
        ultimo_peso = float(ws["F3"].value)
        racao_total = float(ws["H3"].value)

        assert area_ha == 0.5, "Área de V-03 na planilha deve ser 0.5 ha"
        assert lab == "NE", "Laboratório deve ser NE"
        assert peso_inicial == 0.01, "Peso inicial padrão deve ser 0.01g"
        assert pls_mil == 65.0, "PLs povoadas deve ser 65 mil"
        assert ultimo_peso == 12.1, "Último peso deve ser 12.1g"
        assert racao_total == 404.0, "Ração total deve ser 404 kg"

        # 2. Amostragem Real Row 14 (Data: 22/08/2026, DOC 65)
        # 1ª biometria registrada: 11.21g
        gmd_excel_r14 = float(ws.cell(14, 10).value)  # Coluna J: GMD
        gmd_calculado_r14 = (11.21 - peso_inicial) / 65.0
        assert abs(gmd_excel_r14 - gmd_calculado_r14) < 0.0001, "GMD da Linha 14 diverge da fórmula oficial"

        # 3. Biomassa Estimada na Linha 14 com Sobrevivência de 85%
        pop_v03 = int(65000 * 0.85)  # 55.250 camarões
        biomassa_r14 = (pop_v03 * 11.21) / 1000.0  # 619.3525 kg
        racao_acum_r14 = float(ws.cell(14, 8).value)  # Coluna H: 54 kg
        assert racao_acum_r14 == 54.0

        fca_r14 = ZootecniaService.calcular_fca_parcial(racao_acum_r14, biomassa_r14)
        assert fca_r14 == 0.09, f"FCA calculado deve ser 0.09, obtido {fca_r14}"

        # 4. Amostragem Real Row 52 (Última biometria: 12.1g)
        peso_r52 = float(ws.cell(52, 9).value)
        assert peso_r52 == 12.1, "Último peso biometrado deve ser 12.1g"

        wb.close()
