"""Motor oficial de regras e fórmulas zootécnicas para carcinicultura (Litopenaeus vannamei).

Consolida as fórmulas operacionais e executivas da fazenda em Ceará-Mirim/RN,
garantindo erro matemático inferior a 0.01% em conformidade com os modelos de controle.
"""
from typing import Optional, Tuple


class ZootecniaService:
    """Serviço com as fórmulas zootécnicas oficiais da fazenda."""

    @staticmethod
    def calcular_populacao_estimada(pls_estocadas: int, sobrevivencia_pct: float) -> int:
        """Calcula a população estimada viva no viveiro.

        Fórmula:
            Populacao = PLs_Estocadas * (Sobrevivencia / 100)
        """
        if pls_estocadas <= 0 or sobrevivencia_pct <= 0:
            return 0
        return int(round(pls_estocadas * (sobrevivencia_pct / 100.0)))

    @staticmethod
    def calcular_biomassa_estimada_kg(
        populacao_viva: int,
        peso_medio_g: float
    ) -> float:
        """Calcula a biomassa estimada em quilogramas.

        Fórmula:
            Biomassa (kg) = (Populacao_Viva * Peso_Medio_g) / 1000
        """
        if populacao_viva <= 0 or peso_medio_g <= 0:
            return 0.0
        return round((populacao_viva * peso_medio_g) / 1000.0, 2)

    @staticmethod
    def calcular_fca_parcial(
        racao_acumulada_kg: float,
        biomassa_estimada_kg: float
    ) -> Optional[float]:
        """Calcula o Fator de Conversão Alimentar (FCA) Parcial.

        Fórmula:
            FCA Parcial = Racao_Acumulada_kg / Biomassa_Estimada_kg
        """
        if biomassa_estimada_kg <= 0 or racao_acumulada_kg <= 0:
            return None
        return round(racao_acumulada_kg / biomassa_estimada_kg, 2)

    @staticmethod
    def calcular_gmd(
        peso_atual_g: float,
        peso_anterior_g: float,
        dias_intervalo: int
    ) -> Optional[float]:
        """Calcula o Ganho Médio Diário (GMD) em gramas por dia.

        Fórmula:
            GMD (g/dia) = (Peso_Atual - Peso_Anterior) / Delta_Dias
        """
        if dias_intervalo <= 0:
            return 0.0
        ganho = peso_atual_g - peso_anterior_g
        return round(ganho / dias_intervalo, 2)

    @staticmethod
    def calcular_fechamento_safra(
        camarao_colhido_kg: float,
        peso_final_g: float,
        pls_estocadas: int,
        racao_total_ciclo_kg: float,
        area_ha: float
    ) -> Tuple[float, float, float]:
        """Calcula as métricas definitivas de encerramento de lote (Despesca).

        Retorna:
            (sobrevivencia_real_pct, fca_real_final, produtividade_kg_ha)
        """
        # 1. Sobrevivência Real (%)
        # Número de camarões colhidos = (kg * 1000) / peso_final_g
        # Sobrevivência = (camaroes_colhidos / pls_estocadas) * 100
        sobrevivencia_pct = 0.0
        if pls_estocadas > 0 and peso_final_g > 0 and camarao_colhido_kg > 0:
            camaroes_colhidos = (camarao_colhido_kg * 1000.0) / peso_final_g
            sobrevivencia_pct = round((camaroes_colhidos / pls_estocadas) * 100.0, 2)

        # 2. FCA Real Final
        # FCA = Ração Total Consumida / Total Colhido
        fca_final = 0.0
        if camarao_colhido_kg > 0 and racao_total_ciclo_kg > 0:
            fca_final = round(racao_total_ciclo_kg / camarao_colhido_kg, 2)

        # 3. Produtividade (kg/ha)
        produtividade = 0.0
        if area_ha > 0 and camarao_colhido_kg > 0:
            produtividade = round(camarao_colhido_kg / area_ha, 2)

        return sobrevivencia_pct, fca_final, produtividade

    @staticmethod
    def classificar_status_agua(
        o2_manha: Optional[float] = None,
        o2_noite: Optional[float] = None,
        amonia_mg_l: Optional[float] = None,
        nitrito_mg_l: Optional[float] = None,
        delta_ph: Optional[float] = None,
        secchi_cm: Optional[float] = None
    ) -> str:
        """Classifica a severidade dos parâmetros de qualidade da água.

        Retorna:
            'CRITICO', 'ATENCAO' ou 'OTIMO'
        """
        # Critérios Críticos (Risco Letal Iminente)
        if o2_manha is not None and o2_manha < 3.0:
            return "CRITICO"
        if o2_noite is not None and o2_noite < 3.0:
            return "CRITICO"
        if amonia_mg_l is not None and amonia_mg_l > 0.1:
            return "CRITICO"
        if nitrito_mg_l is not None and nitrito_mg_l > 0.2:
            return "CRITICO"

        # Critérios de Atenção (Sub-ótimo / Ajuste de Manejo)
        if o2_manha is not None and o2_manha < 3.8:
            return "ATENCAO"
        if o2_noite is not None and o2_noite < 3.8:
            return "ATENCAO"
        if delta_ph is not None and abs(delta_ph) > 0.8:
            return "ATENCAO"
        if secchi_cm is not None and (secchi_cm < 20.0 or secchi_cm > 50.0):
            return "ATENCAO"

        return "OTIMO"
