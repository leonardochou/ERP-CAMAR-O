"""Tier 2: Ingestão de Planilhas e Idempotência Estrita.

Valida a leitura das planilhas reais em CAMARÃO/MODELOS DE CONTROLE/:
- Salto obrigatório das linhas 1 a 9 (metadados e fórmulas superiores)
- Extração de dados diários contínuos a partir da Linha 10
- Extração e mapeamento de metadados de cabeçalho do ciclo
- Hashing determinístico SHA-256 por linha (fazenda + viveiro + data + turno)
- TESTE DE IDEMPOTÊNCIA DUPLA: Ingestão 2 vezes consecutivas com zero duplicatas criadas
- Tolerância graciosa a abas inativas ("EM PREPARACAO")
- Associação multi-tenant com a Fazenda Arrendada (FAZ_ARRENDADA)
"""
import hashlib
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Any

import openpyxl
import pytest
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua


# ==============================================================================
# FUNÇÃO DE HASHING CANÔNICA DETERMINÍSTICA
# ==============================================================================
def calcular_hash_linha_alimentacao(
    fazenda_codigo: str,
    viveiro_codigo: str,
    data_val: date,
    racao_manha: float,
    racao_tarde: float,
    sobra_manha: int = 0,
    sobra_tarde: int = 0,
) -> str:
    """Gera hash SHA-256 determinístico para garantir idempotência estrita."""
    payload = (
        f"{fazenda_codigo.strip().upper()}|"
        f"{viveiro_codigo.strip().upper()}|"
        f"{data_val.strftime('%Y-%m-%d')}|"
        f"{racao_manha:.2f}|{sobra_manha}|"
        f"{racao_tarde:.2f}|{sobra_tarde}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def calcular_hash_linha_agua(
    fazenda_codigo: str,
    viveiro_codigo: str,
    data_val: date,
    o2_manha: float = None,
    o2_noite: float = None,
    salinidade: float = None,
    ph_manha: float = None,
) -> str:
    """Gera hash SHA-256 determinístico para qualidade da água."""
    o2_m = f"{o2_manha:.2f}" if o2_manha is not None else "NULL"
    o2_n = f"{o2_noite:.2f}" if o2_noite is not None else "NULL"
    sal = f"{salinidade:.1f}" if salinidade is not None else "NULL"
    ph_m = f"{ph_manha:.2f}" if ph_manha is not None else "NULL"

    payload = (
        f"{fazenda_codigo.strip().upper()}|"
        f"{viveiro_codigo.strip().upper()}|"
        f"{data_val.strftime('%Y-%m-%d')}|"
        f"{o2_m}|{o2_n}|{sal}|{ph_m}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ==============================================================================
# TESTES DE ESTRUTURA E SALTO DE CABEÇALHO (LINHAS 1 A 9)
# ==============================================================================
class TestEstruturaPlanilhasReais:
    """Valida a conformidade física dos modelos reais de controle."""

    def test_existencia_arquivos_obrigatorios(self, spreadsheet_paths: Dict[str, Path]):
        """Confere que todas as 4 planilhas mestras da fazenda existem no diretório oficial."""
        for chave, caminho in spreadsheet_paths.items():
            assert caminho.exists(), f"Planilha obrigatória '{chave}' não encontrada em {caminho}"
            assert caminho.stat().st_size > 1000, f"Arquivo '{chave}' parece vazio ou corrompido"

    def test_salto_rigoroso_linhas_1_a_9_alimentacao(self, spreadsheet_paths: Dict[str, Path]):
        """Valida que as linhas 1 a 9 são metadados institucionais e a linha 10 é operacional."""
        wb = openpyxl.load_workbook(spreadsheet_paths["alimentacao"], data_only=True)
        ws = wb["V-03"]

        # Linha 1: Título institucional
        assert "VIVEIRO" in str(ws["A1"].value).upper() or "CONTROLE" in str(ws["A1"].value).upper()

        # Linhas 2-3: Metadados do Ciclo
        assert ws["B2"].value == 0.5, "B2 deve conter a Área do viveiro (0.5 ha)"
        assert ws["D2"].value == "NE", "D2 deve conter o Laboratório fornecedor"
        assert ws["F2"].value == 0.01, "F2 deve conter o Peso Inicial das PLs"
        assert ws["B3"].value == 65, "B3 deve conter a quantidade de PLs em milhares (65 mil)"
        assert isinstance(ws["D3"].value, (date, datetime)), "D3 deve conter a Data de Povoamento"

        # Linha 4-5: Painel de Encerramento (Despesca)
        assert "ENCERRAMENTO" in str(ws["A4"].value).upper() or "PAINEL" in str(ws["A4"].value).upper()

        # Linha 9: Cabeçalhos oficiais de colunas de dados
        cabecalhos_l9 = [str(ws.cell(9, c).value) for c in range(1, 12)]
        assert any("DATA" in h.upper() for h in cabecalhos_l9)
        assert any("DOC" in h.upper() for h in cabecalhos_l9)
        assert any("MANHÃ" in h.upper() or "MANHA" in h.upper() or "TRATO A" in h.upper() for h in cabecalhos_l9)
        assert any("TARDE" in h.upper() or "TRATO B" in h.upper() for h in cabecalhos_l9)
        assert any("BIOMETRIA" in h.upper() for h in cabecalhos_l9)

        # Linha 10: Início dos dados operacionais
        data_l10 = ws.cell(10, 1).value
        assert isinstance(data_l10, (date, datetime)), "Linha 10 Coluna 1 deve ser uma Data válida"
        doc_l10 = ws.cell(10, 2).value
        assert isinstance(doc_l10, (int, float)) and doc_l10 > 0, "Linha 10 Coluna 2 deve ser o DOC numérico"

        wb.close()

    def test_salto_rigoroso_linhas_1_a_9_agua(self, spreadsheet_paths: Dict[str, Path]):
        """Valida a separação entre metadados/cards superiores (L1-8) e medições (L10+) em água."""
        wb = openpyxl.load_workbook(spreadsheet_paths["agua"], data_only=True)
        ws = wb["V-03"]

        # Linha 9: Cabeçalho das colunas físico-químicas
        cabecalhos = [str(ws.cell(9, c).value).lower() for c in range(1, 14)]
        assert any("o2" in c or "oxig" in c for c in cabecalhos)
        assert any("ph" in c for c in cabecalhos)
        assert any("salinidade" in c for c in cabecalhos)

        # Linha 10: Linha de dados operacionais
        doc_l10 = ws.cell(10, 1).value
        assert doc_l10 == 1, "Linha 10 deve iniciar no Dia Ciclo 1"
        data_l10 = ws.cell(10, 2).value
        assert isinstance(data_l10, (date, datetime)), "Linha 10 Coluna 2 deve conter uma Data"

        wb.close()


# ==============================================================================
# TESTES DE HASHING DETERMINÍSTICO SHA-256
# ==============================================================================
class TestHashingDeterministico:
    """Valida a geração de assinaturas imutáveis para proteção contra duplicações."""

    def test_hash_sha256_consistente_mesma_entrada(self):
        """A mesma entrada de dados deve gerar rigorosamente o mesmo hash de 64 caracteres."""
        dt = date(2026, 8, 22)
        h1 = calcular_hash_linha_alimentacao("FAZ_ARRENDADA", "V-03", dt, 6.0, 0.0, 0, 0)
        h2 = calcular_hash_linha_alimentacao("FAZ_ARRENDADA", "V-03", dt, 6.0, 0.0, 0, 0)

        assert h1 == h2
        assert len(h1) == 64
        assert isinstance(h1, str)

    def test_hash_sha256_efeito_avalanche_alteracao_minima(self):
        """Qualquer alteração em quantidade, data ou viveiro altera radicalmente o hash."""
        dt = date(2026, 8, 22)
        h_orig = calcular_hash_linha_alimentacao("FAZ_ARRENDADA", "V-03", dt, 6.0, 0.0, 0, 0)

        # Modificação de 0.1 kg no trato
        h_mod_kg = calcular_hash_linha_alimentacao("FAZ_ARRENDADA", "V-03", dt, 6.1, 0.0, 0, 0)
        assert h_orig != h_mod_kg

        # Modificação na fazenda (Multi-Tenant)
        h_mod_faz = calcular_hash_linha_alimentacao("FAZ_HAKKA", "V-03", dt, 6.0, 0.0, 0, 0)
        assert h_orig != h_mod_faz

        # Modificação no tanque
        h_mod_viv = calcular_hash_linha_alimentacao("FAZ_ARRENDADA", "V-04", dt, 6.0, 0.0, 0, 0)
        assert h_orig != h_mod_viv

    def test_hash_sha256_monitoramento_agua(self):
        """Verifica hash determinístico para qualidade da água."""
        dt = date(2026, 10, 1)
        h1 = calcular_hash_linha_agua("FAZ_ARRENDADA", "V-03", dt, 4.2, 3.9, 15.0, 7.8)
        h2 = calcular_hash_linha_agua("FAZ_ARRENDADA", "V-03", dt, 4.2, 3.9, 15.0, 7.8)
        h3 = calcular_hash_linha_agua("FAZ_ARRENDADA", "V-03", dt, 2.6, 3.9, 15.0, 7.8)

        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 64


# ==============================================================================
# TESTE DE DUPLA IDEMPOTÊNCIA ESTRITA (CRITÉRIO DE ACEITAÇÃO MANDATÓRIO)
# ==============================================================================
class TestDuplaIdempotencia:
    """Executa o conector de ingestão duas vezes consecutivas sobre a mesma base.

    Comprova formalmente que COUNT(registros) permanece rigorosamente idêntico
    e ZERO linhas duplicadas são inseridas no banco relacional.
    """

    def _executar_ingestao_v03(
        self, session: Session, planilha_path: Path, fazenda: Fazenda, ciclo: CicloCultivo
    ) -> int:
        """Simula o pipeline de ingestão de V-03 com deduplicação por SHA-256 e chave natural."""
        wb = openpyxl.load_workbook(planilha_path, data_only=True)
        ws = wb["V-03"]

        registros_inseridos = 0

        # Itera da Linha 10 até o fim das linhas preenchidas
        for r in range(10, ws.max_row + 1):
            val_data = ws.cell(r, 1).value
            if not val_data:
                continue

            # Converte para data nativa
            if isinstance(val_data, datetime):
                dt_obj = val_data.date()
            elif isinstance(val_data, date):
                dt_obj = val_data
            else:
                continue

            doc_val = int(ws.cell(r, 2).value or 0)
            racao_a = float(ws.cell(r, 3).value or 0.0)
            sobra_a = ws.cell(r, 4).value
            sobra_a_int = int(sobra_a) if isinstance(sobra_a, (int, float)) else 0

            racao_b = float(ws.cell(r, 5).value or 0.0)
            sobra_b = ws.cell(r, 6).value
            sobra_b_int = int(sobra_b) if isinstance(sobra_b, (int, float)) else 0

            total_dia = float(ws.cell(r, 7).value or (racao_a + racao_b))
            consumo_acum = float(ws.cell(r, 8).value or total_dia)

            # Gera hash determinístico
            hash_linha = calcular_hash_linha_alimentacao(
                fazenda.codigo, "V-03", dt_obj, racao_a, racao_b, sobra_a_int, sobra_b_int
            )

            # Deduplicação Idempotente: Verifica se hash ou chave composta já existem
            existente_hash = session.query(LancamentoAlimentacao).filter(
                LancamentoAlimentacao.hash_linha == hash_linha
            ).first()

            existente_chave = session.query(LancamentoAlimentacao).filter(
                LancamentoAlimentacao.ciclo_id == ciclo.id,
                LancamentoAlimentacao.data == dt_obj
            ).first()

            if existente_hash or existente_chave:
                # Linha já processada anteriormente -> descarta de forma idempotente
                continue

            # Insere novo registro com o tenant da fazenda
            novo_lancamento = LancamentoAlimentacao(
                fazenda_id=fazenda.id,
                ciclo_id=ciclo.id,
                data=dt_obj,
                doc=doc_val,
                racao_manha_kg=racao_a,
                sobra_manha=sobra_a_int,
                racao_tarde_kg=racao_b,
                sobra_tarde=sobra_b_int,
                total_dia_kg=total_dia,
                consumo_acumulado_kg=consumo_acum,
                hash_linha=hash_linha,
            )
            session.add(novo_lancamento)
            registros_inseridos += 1


        session.commit()
        wb.close()
        return registros_inseridos

    def test_dupla_ingestao_zero_duplicatas(
        self, db_session: Session, spreadsheet_paths: Dict[str, Path],
        fazenda_padrao: Fazenda, ciclo_teste: CicloCultivo
    ):
        """Critério Oficial: Rodar a ingestão 2 vezes seguidas sobre o mesmo arquivo não duplica dados."""
        arquivo_alim = spreadsheet_paths["alimentacao"]

        # -------------------------------------------------------------
        # Rodada 1 de Ingestão: Popula o banco com os dados da planilha
        # -------------------------------------------------------------
        inseridos_rodada_1 = self._executar_ingestao_v03(
            db_session, arquivo_alim, fazenda_padrao, ciclo_teste
        )
        total_banco_rodada_1 = db_session.query(LancamentoAlimentacao).filter(
            LancamentoAlimentacao.ciclo_id == ciclo_teste.id
        ).count()

        assert inseridos_rodada_1 > 0, "A rodada 1 deve inserir registros a partir da planilha real"
        assert total_banco_rodada_1 == inseridos_rodada_1

        # -------------------------------------------------------------
        # Rodada 2 de Ingestão: Executa exatamente o mesmo arquivo novamente
        # -------------------------------------------------------------
        inseridos_rodada_2 = self._executar_ingestao_v03(
            db_session, arquivo_alim, fazenda_padrao, ciclo_teste
        )
        total_banco_rodada_2 = db_session.query(LancamentoAlimentacao).filter(
            LancamentoAlimentacao.ciclo_id == ciclo_teste.id
        ).count()

        # ASSERÇÃO MANDATÓRIA: Zero novos registros e contagem inalterada
        assert inseridos_rodada_2 == 0, f"Rodada 2 deveria inserir 0 registros, inseriu {inseridos_rodada_2}"
        assert total_banco_rodada_2 == total_banco_rodada_1, "Contagem de registros diverge após re-ingestão"

    def test_tolerancia_abas_em_preparacao(self, spreadsheet_paths: Dict[str, Path]):
        """Abas V-01, V-02 e V-04 (sem povoamento ativo) devem ser reconhecidas como em preparação."""
        wb = openpyxl.load_workbook(spreadsheet_paths["alimentacao"], data_only=True)

        for aba_nome in ["V-01", "V-02", "V-04"]:
            assert aba_nome in wb.sheetnames
            ws = wb[aba_nome]

            # Status avaliado nas planilhas reais para abas vazias
            status_lote = str(ws["H2"].value).strip()
            pls_val = ws["B3"].value
            racao_total = ws["H3"].value

            assert status_lote == "EM PREPARACAO", f"Aba {aba_nome} deveria ter status EM PREPARACAO"
            assert pls_val is None or pls_val == 0, f"Aba {aba_nome} não deve ter PLs estocadas"
            assert racao_total is None or racao_total == 0, f"Aba {aba_nome} não deve ter consumo total"

            # Linha 10 não deve ter tratos lançados
            trato_a = ws.cell(10, 3).value
            trato_b = ws.cell(10, 5).value
            assert trato_a is None or trato_a == 0, f"Aba {aba_nome} não deve ter ração A em L10"
            assert trato_b is None or trato_b == 0, f"Aba {aba_nome} não deve ter ração B em L10"

        wb.close()

