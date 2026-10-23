"""Serviço de Ingestão de Planilhas e Sincronização Contínua do ERP CAMARÃO.

Processa as planilhas oficiais de campo:
- Controle_Alimentacao_e_Biometria.xlsx
- Controle_Qualidade_Agua.xlsx
Garante:
- Salto rigoroso das linhas institucionais 1 a 9
- Ingestão contínua a partir da Linha 10
- Deduplicação idempotente estrita via Hash SHA-256
- Interceptação de anomalias e envio para a Central de Auditoria
- Cálculo automatizado de indicadores zootécnicos (Biomassa, FCA, GMD)
"""
import hashlib
import io
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, BinaryIO

import openpyxl
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.despesca import DespescaVenda
from app.models.auditoria import AuditoriaPendencia
from app.models.contabilidade import LancamentoContabil, LogBackupContabil
from app.services.zootecnia_service import ZootecniaService
from app.core.tenant import FAZENDA_PADRAO_ID, FAZENDA_HAKKA_ID


def calcular_chave_contabil_estrita(
    fazenda_id: str,
    fornecedor: str,
    data_vencimento: date,
    valor_rs: float
) -> str:
    """Gera hash SHA-256 determinístico para bloqueio automático estrito de redundância contábil."""
    forn_limpo = re.sub(r"\s+", " ", str(fornecedor or "").strip().upper())
    dt_str = data_vencimento.strftime("%Y-%m-%d")
    val_str = f"{float(valor_rs):.2f}"
    payload = f"{fazenda_id.strip()}|{forn_limpo}|{dt_str}|{val_str}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def mapear_grupo_contabil(codigo_conta: str) -> str:
    """Classifica o código do Plano de Contas no respectivo grupo estrutural da DRE e Fluxo."""
    cod = str(codigo_conta or "").strip()
    if cod.startswith("1.2"):
        return "RESULTADO_FINANCEIRO"
    if cod.startswith("1."):
        return "RECEITA_BRUTA"
    if cod.startswith("2."):
        return "DEDUCOES"
    if cod.startswith("3."):
        return "CUSTO_VARIAVEL"
    if cod.startswith("4.2"):
        return "RESULTADO_FINANCEIRO"
    if cod.startswith("4."):
        return "DESPESA_FIXA"
    if cod.startswith("5."):
        return "CAPEX"
    return "CUSTO_VARIAVEL"


def calcular_hash_alimentacao(
    fazenda_codigo: str,
    viveiro_codigo: str,
    data_val: date,
    racao_manha: float,
    racao_tarde: float,
    sobra_manha: int = 0,
    sobra_tarde: int = 0,
) -> str:
    """Gera hash determinístico SHA-256 para linha de alimentação."""
    payload = (
        f"{fazenda_codigo.strip().upper()}|"
        f"{viveiro_codigo.strip().upper()}|"
        f"{data_val.strftime('%Y-%m-%d')}|"
        f"{racao_manha:.2f}|{sobra_manha}|"
        f"{racao_tarde:.2f}|{sobra_tarde}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def calcular_hash_agua(
    fazenda_codigo: str,
    viveiro_codigo: str,
    data_val: date,
    o2_manha: Optional[float] = None,
    o2_noite: Optional[float] = None,
    salinidade: Optional[float] = None,
    ph_manha: Optional[float] = None,
) -> str:
    """Gera hash determinístico SHA-256 para qualidade da água."""
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


def converter_para_data(valor: Any) -> Optional[date]:
    """Converte valores variados de células openpyxl em objeto date nativo."""
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        valor_limpo = valor.strip()
        for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%y-%m-%d"):
            try:
                return datetime.strptime(valor_limpo, formato).date()
            except ValueError:
                continue
    return None


class IngestorService:
    """Serviço executivo de ingestão, sanitização e auditoria de planilhas."""

    @classmethod
    def processar_planilha_alimentacao(
        cls,
        db: Session,
        arquivo_ou_caminho: Union[str, Path, BinaryIO, bytes],
        fazenda_id: str,
        fazenda_codigo: str = "FAZ_ARRENDADA"
    ) -> Dict[str, Any]:
        """Lê e ingere a planilha Controle_Alimentacao_e_Biometria.xlsx."""
        if isinstance(arquivo_ou_caminho, bytes):
            arquivo_ou_caminho = io.BytesIO(arquivo_ou_caminho)

        wb = openpyxl.load_workbook(arquivo_ou_caminho, data_only=True)
        resumo = {
            "tipo": "ALIMENTACAO_E_BIOMETRIA",
            "fazenda_id": fazenda_id,
            "fazenda_codigo": fazenda_codigo,
            "abas_processadas": [],
            "linhas_lidas": 0,
            "novos_lancamentos": 0,
            "atualizacoes_incremental": 0,
            "duplicatas_ignoradas": 0,
            "biometrias_registradas": 0,
            "pendencias_auditoria": 0,
            "novidades_por_viveiro": {},
        }

        # Abas que representam viveiros (ex: V-01, V-1, v-1, v4, V-10, etc.)
        padrao_viveiro = re.compile(r"^V-?(\d{1,2})$", re.IGNORECASE)

        for sheet_name in wb.sheetnames:
            m_viv = padrao_viveiro.match(sheet_name.strip())
            if not m_viv:
                continue

            num_viv = int(m_viv.group(1))
            cod_viveiro = f"V-{num_viv:02d}"
            ws = wb[sheet_name]

            # Inicializa relatório do viveiro
            relatorio_viv = {
                "dias_novos": [],
                "novas_biometrias": [],
                "atualizados": [],
                "duplicatas_ignoradas": 0,
                "laboratorio": "",
                "pls_estocadas": 0,
                "data_povoamento": None,
                "despesca": None,
                "bercario": None
            }

            # Localiza ou cadastra o viveiro
            viveiro = db.query(Viveiro).filter(
                Viveiro.fazenda_id == fazenda_id,
                Viveiro.codigo == cod_viveiro
            ).first()

            # Extração de Área (Linhas 1 a 3)
            area_ha = 0.5
            try:
                for r_a in range(1, 4):
                    val_area = ws.cell(r_a, 2).value
                    if val_area and isinstance(val_area, (int, float)) and 0.1 <= float(val_area) <= 20.0:
                        area_ha = float(val_area)
                        break
            except Exception:
                pass

            if not viveiro:
                area_m2 = round(area_ha * 10000.0, 2)
                viveiro = Viveiro(
                    fazenda_id=fazenda_id,
                    codigo=cod_viveiro,
                    nome_operacional=f"Tanque {num_viv}",
                    nome_pai=f"Viveiro {num_viv}",
                    numero_pai=num_viv,
                    setor="Central",
                    area_m2=area_m2,
                    area_ha=area_ha,
                    volume_m3=round(area_m2 * 1.2, 2),
                    tipo_uso="Engorda",
                    ativo=True
                )
                db.add(viveiro)
                db.flush()

            # Extração Dinâmica de Metadados do Ciclo (Linhas 1 a 6)
            lab = "AQUATEC"
            pls_mil = 65.0
            peso_ini = 0.01
            dt_povoamento = None
            bercario_info = None

            for r in range(1, 7):
                for c in range(1, 12):
                    val_c = ws.cell(r, c).value
                    if not val_c:
                        continue
                    s_c = str(val_c).strip()
                    up_c = s_c.upper()

                    if "LAB" in up_c:
                        next_v = ws.cell(r, c + 1).value
                        if next_v and str(next_v).strip() not in ["0", "None", ""]:
                            lab = str(next_v).strip().upper()

                    if any(k in up_c for k in ["QUANTID", "PLS"]):
                        next_v = ws.cell(r, c + 1).value
                        try:
                            if next_v is not None and str(next_v).strip() != "":
                                pls_mil = float(next_v)
                        except Exception:
                            pass

                    if any(k in up_c for k in ["DIA CULTIVO", "POVOAMENTO", "BERCARIO", "BERÇÁRIO"]):
                        next_v = ws.cell(r, c + 1).value
                        txt_c = s_c + " " + (str(next_v) if next_v else "")
                        dates_f = re.findall(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", txt_c)
                        if dates_f and not dt_povoamento:
                            dt_povoamento = converter_para_data(dates_f[0])
                        if len(dates_f) >= 2 or "c/" in txt_c.lower() or "gr" in txt_c.lower():
                            bercario_info = txt_c.strip()

            pls_qtd = int(pls_mil * 1000) if pls_mil > 0 else 50000
            if not dt_povoamento:
                dt_povoamento = date(2026, 6, 19)

            relatorio_viv["laboratorio"] = lab
            relatorio_viv["pls_estocadas"] = pls_qtd
            relatorio_viv["data_povoamento"] = dt_povoamento.strftime("%d/%m/%Y")
            if bercario_info:
                relatorio_viv["bercario"] = bercario_info

            # Detectar layout operacional (padrão com sobra vs direto de campo)
            layout_com_sobra = False
            start_row = 4
            for r_chk in range(1, min(12, ws.max_row + 1)):
                row_txt = " ".join(str(ws.cell(r_chk, c_chk).value or "").upper() for c_chk in range(1, 12))
                if "SOBRA BANDEJA" in row_txt or "SOBRA" in row_txt:
                    layout_com_sobra = True
                    start_row = r_chk + 1
                    break

            # Localiza ciclo ativo existente ou correspondente
            ciclo = db.query(CicloCultivo).filter(
                CicloCultivo.fazenda_id == fazenda_id,
                CicloCultivo.viveiro_id == viveiro.id,
                CicloCultivo.status.in_(["EM CULTIVO ATIVO", "DESPESCA_PARCIAL", "ATIVO"])
            ).first()

            if not ciclo:
                ciclo = db.query(CicloCultivo).filter(
                    CicloCultivo.fazenda_id == fazenda_id,
                    CicloCultivo.viveiro_id == viveiro.id,
                    CicloCultivo.data_povoamento == dt_povoamento
                ).first()

            ano_safra_val = dt_povoamento.year

            if not ciclo:
                maior_seq = db.query(func.max(CicloCultivo.numero_sequencial)).filter(
                    CicloCultivo.fazenda_id == fazenda_id,
                    CicloCultivo.viveiro_id == viveiro.id,
                    CicloCultivo.ano_safra == ano_safra_val
                ).scalar() or 0
                prox_seq = int(maior_seq) + 1
                codigo_oficial = f"{cod_viveiro} • Ciclo {ano_safra_val}.{prox_seq}"
                num_lote = f"LOTE-{ano_safra_val}-{cod_viveiro}.{prox_seq}"
                densidade = round(pls_qtd / (viveiro.area_ha * 10000), 2) if viveiro.area_ha else 13.0

                ciclo = CicloCultivo(
                    fazenda_id=fazenda_id,
                    viveiro_id=viveiro.id,
                    numero_lote=num_lote,
                    codigo_ciclo=codigo_oficial,
                    ano_safra=ano_safra_val,
                    numero_sequencial=prox_seq,
                    data_povoamento=dt_povoamento,
                    pls_estocadas=pls_qtd,
                    densidade_pl_m2=densidade,
                    laboratorio=lab,
                    peso_inicial_g=peso_ini,
                    status="EM CULTIVO ATIVO",
                    observacoes=f"Berçário: {bercario_info}" if bercario_info else None
                )
                db.add(ciclo)
                db.flush()
            else:
                if lab and lab != "0":
                    ciclo.laboratorio = lab
                if pls_qtd > 0:
                    ciclo.pls_estocadas = pls_qtd
                if dt_povoamento:
                    ciclo.data_povoamento = dt_povoamento
                if not ciclo.codigo_ciclo:
                    ciclo.codigo_ciclo = f"{cod_viveiro} • Ciclo {ano_safra_val}.{ciclo.numero_sequencial or 1}"
                if not ciclo.ano_safra:
                    ciclo.ano_safra = ano_safra_val
                if bercario_info and "Berçário" not in (ciclo.observacoes or ""):
                    ciclo.observacoes = (ciclo.observacoes or "") + f" | Berçário: {bercario_info}"

            # Extração de Despesca Prévia (Linha 5 padrão da planilha)
            despesca_detectada = None
            val_dt_desp = converter_para_data(ws.cell(5, 2).value)
            val_colhido = ws.cell(5, 4).value
            val_peso_final = ws.cell(5, 6).value

            if val_dt_desp and val_colhido and isinstance(val_colhido, (int, float)) and val_colhido > 0:
                colhido_kg = float(val_colhido)
                peso_fim_g = float(val_peso_final) if val_peso_final and isinstance(val_peso_final, (int, float)) else 12.0
                despesca_detectada = {
                    "data": val_dt_desp,
                    "colhido_kg": colhido_kg,
                    "peso_final_g": peso_fim_g,
                    "obs": "Despesca importada da linha 5 da planilha oficial."
                }

            # Ignora abas que estejam explicitamente em preparação sem dados
            if ciclo.status == "EM PREPARACAO":
                resumo["abas_processadas"].append({"aba": sheet_name, "status": "EM PREPARACAO", "linhas": 0})
                continue

            linhas_aba = 0
            # Leitura de Linhas Operacionais a partir da linha identificada
            for r in range(start_row, ws.max_row + 1):
                val_data = converter_para_data(ws.cell(r, 1).value)
                if not val_data:
                    continue

                if layout_com_sobra:
                    c_racao_m = ws.cell(r, 3).value
                    sobra_m_raw = ws.cell(r, 4).value
                    c_racao_t = ws.cell(r, 5).value
                    sobra_t_raw = ws.cell(r, 6).value
                    c_tot = ws.cell(r, 7).value
                    c_acum = ws.cell(r, 8).value
                    c_biometria = ws.cell(r, 9).value
                    gmd_val = ws.cell(r, 10).value
                    c_obs = ws.cell(r, 11).value
                else:
                    c_racao_m = ws.cell(r, 3).value
                    sobra_m_raw = None
                    c_racao_t = ws.cell(r, 4).value
                    sobra_t_raw = None
                    c_tot = ws.cell(r, 5).value
                    c_acum = ws.cell(r, 6).value
                    c_biometria = ws.cell(r, 7).value
                    gmd_val = None
                    c_obs = ws.cell(r, 8).value

                tem_racao_m = c_racao_m is not None and str(c_racao_m).strip() not in ["", "None"]
                tem_racao_t = c_racao_t is not None and str(c_racao_t).strip() not in ["", "None"]
                tem_bio = c_biometria is not None and str(c_biometria).strip() not in ["", "None"]
                tem_observacao = c_obs is not None and str(c_obs).strip() not in ["", "None"]

                # Ignora linhas futuras sem dados
                if not (tem_racao_m or tem_racao_t or tem_bio or tem_observacao):
                    continue

                obs_str = str(c_obs).strip() if tem_observacao else None

                # Reconhecimento inteligente de despesca anotada no campo de observações
                if obs_str and "despesca" in obs_str.lower() and not despesca_detectada:
                    m_kg = re.search(r'(\d+(?:[,\.]\d+)?)\s*kg', obs_str, re.I)
                    m_gr = re.search(r'(\d+(?:[,\.]\d+)?)\s*gr?', obs_str, re.I)
                    kg_d = float(m_kg.group(1).replace(",", ".")) if m_kg else 350.0
                    gr_d = float(m_gr.group(1).replace(",", ".")) if m_gr else (float(c_biometria) if tem_bio and isinstance(c_biometria, (int, float)) else 14.0)
                    despesca_detectada = {
                        "data": val_data,
                        "colhido_kg": kg_d,
                        "peso_final_g": gr_d,
                        "obs": obs_str
                    }

                linhas_aba += 1
                resumo["linhas_lidas"] += 1

                doc_raw = ws.cell(r, 2).value
                doc_val = int(doc_raw) if doc_raw is not None and str(doc_raw).isdigit() else 1

                try:
                    racao_m = float(c_racao_m) if tem_racao_m else 0.0
                except (ValueError, TypeError):
                    racao_m = 0.0

                sobra_m = int(sobra_m_raw) if sobra_m_raw is not None and str(sobra_m_raw).isdigit() else 0

                try:
                    racao_t = float(c_racao_t) if tem_racao_t else 0.0
                except (ValueError, TypeError):
                    racao_t = 0.0

                sobra_t = int(sobra_t_raw) if sobra_t_raw is not None and str(sobra_t_raw).isdigit() else 0

                try:
                    total_dia = float(c_tot) if c_tot is not None else (racao_m + racao_t)
                except (ValueError, TypeError):
                    total_dia = racao_m + racao_t

                try:
                    acumulado = float(c_acum) if c_acum is not None else total_dia
                except (ValueError, TypeError):
                    acumulado = total_dia

                try:
                    biometria_peso = float(c_biometria) if tem_bio and float(c_biometria) > 0 else None
                except (ValueError, TypeError):
                    biometria_peso = None

                h_linha = calcular_hash_alimentacao(
                    fazenda_codigo, cod_viveiro, val_data, racao_m, racao_t, sobra_m, sobra_t
                )

                # Deduplicação idempotente por SHA-256
                existente_hash = db.query(LancamentoAlimentacao).filter(
                    LancamentoAlimentacao.hash_linha == h_linha
                ).first()

                # Verifica se já existe lançamento registrado para a mesma data no ciclo
                existente_data = db.query(LancamentoAlimentacao).filter(
                    LancamentoAlimentacao.ciclo_id == ciclo.id,
                    LancamentoAlimentacao.data == val_data
                ).first()

                data_fmt = val_data.strftime("%d/%m/%Y")

                if existente_hash:
                    resumo["duplicatas_ignoradas"] += 1
                    relatorio_viv["duplicatas_ignoradas"] += 1

                    if biometria_peso and biometria_peso > 0:
                        bio_exist = db.query(Biometria).filter(
                            Biometria.ciclo_id == ciclo.id,
                            Biometria.data == val_data
                        ).first()
                        if not bio_exist:
                            pop_est = ZootecniaService.calcular_populacao_estimada(ciclo.pls_estocadas, 85.0)
                            bio_kg = ZootecniaService.calcular_biomassa_estimada_kg(pop_est, biometria_peso)
                            fca_p = ZootecniaService.calcular_fca_parcial(acumulado, bio_kg) if bio_kg > 0 else 0.0
                            nova_bio = Biometria(
                                fazenda_id=fazenda_id,
                                ciclo_id=ciclo.id,
                                data=val_data,
                                doc=doc_val,
                                peso_medio_g=biometria_peso,
                                gmd_g_dia=float(gmd_val) if gmd_val and isinstance(gmd_val, (int, float)) else None,
                                sobrevivencia_estimada_pct=85.0,
                                populacao_estimada=pop_est,
                                biomassa_estimada_kg=bio_kg,
                                racao_acumulada_ate_data_kg=acumulado,
                                fca_parcial=fca_p,
                                observacoes=obs_str
                            )
                            db.add(nova_bio)
                            resumo["biometrias_registradas"] += 1
                            relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")
                    continue

                if existente_data:
                    existente_data.racao_manha_kg = racao_m
                    existente_data.sobra_manha = sobra_m
                    existente_data.racao_tarde_kg = racao_t
                    existente_data.sobra_tarde = sobra_t
                    existente_data.total_dia_kg = total_dia
                    existente_data.consumo_acumulado_kg = acumulado
                    existente_data.hash_linha = h_linha
                    if obs_str:
                        existente_data.observacoes = obs_str

                    resumo["atualizacoes_incremental"] += 1
                    relatorio_viv["atualizados"].append(f"{data_fmt}: Ração atualizada ({total_dia:.1f}kg)")

                    if biometria_peso and biometria_peso > 0:
                        bio_exist = db.query(Biometria).filter(
                            Biometria.ciclo_id == ciclo.id,
                            Biometria.data == val_data
                        ).first()
                        if not bio_exist:
                            pop_est = ZootecniaService.calcular_populacao_estimada(ciclo.pls_estocadas, 85.0)
                            bio_kg = ZootecniaService.calcular_biomassa_estimada_kg(pop_est, biometria_peso)
                            fca_p = ZootecniaService.calcular_fca_parcial(acumulado, bio_kg) if bio_kg > 0 else 0.0
                            nova_bio = Biometria(
                                fazenda_id=fazenda_id,
                                ciclo_id=ciclo.id,
                                data=val_data,
                                doc=doc_val,
                                peso_medio_g=biometria_peso,
                                gmd_g_dia=float(gmd_val) if gmd_val and isinstance(gmd_val, (int, float)) else None,
                                sobrevivencia_estimada_pct=85.0,
                                populacao_estimada=pop_est,
                                biomassa_estimada_kg=bio_kg,
                                racao_acumulada_ate_data_kg=acumulado,
                                fca_parcial=fca_p,
                                observacoes=obs_str
                            )
                            db.add(nova_bio)
                            resumo["biometrias_registradas"] += 1
                            relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")
                        else:
                            bio_exist.peso_medio_g = biometria_peso
                            if gmd_val and isinstance(gmd_val, (int, float)):
                                bio_exist.gmd_g_dia = float(gmd_val)
                    continue

                novo_trato = LancamentoAlimentacao(
                    fazenda_id=fazenda_id,
                    ciclo_id=ciclo.id,
                    data=val_data,
                    doc=doc_val,
                    racao_manha_kg=racao_m,
                    sobra_manha=sobra_m,
                    racao_tarde_kg=racao_t,
                    sobra_tarde=sobra_t,
                    total_dia_kg=total_dia,
                    consumo_acumulado_kg=acumulado,
                    hash_linha=h_linha,
                    observacoes=obs_str
                )
                db.add(novo_trato)
                resumo["novos_lancamentos"] += 1
                relatorio_viv["dias_novos"].append(f"{data_fmt}: {total_dia:.1f}kg (DOC {doc_val})")

                if biometria_peso and biometria_peso > 0:
                    pop_est = ZootecniaService.calcular_populacao_estimada(ciclo.pls_estocadas, 85.0)
                    bio_kg = ZootecniaService.calcular_biomassa_estimada_kg(pop_est, biometria_peso)
                    fca_p = ZootecniaService.calcular_fca_parcial(acumulado, bio_kg) if bio_kg > 0 else 0.0

                    nova_bio = Biometria(
                        fazenda_id=fazenda_id,
                        ciclo_id=ciclo.id,
                        data=val_data,
                        doc=doc_val,
                        peso_medio_g=biometria_peso,
                        gmd_g_dia=float(gmd_val) if gmd_val and isinstance(gmd_val, (int, float)) else None,
                        sobrevivencia_estimada_pct=85.0,
                        populacao_estimada=pop_est,
                        biomassa_estimada_kg=bio_kg,
                        racao_acumulada_ate_data_kg=acumulado,
                        fca_parcial=fca_p,
                        observacoes=obs_str
                    )
                    db.add(nova_bio)
                    resumo["biometrias_registradas"] += 1
                    relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")

            # Atualiza consumo total de ração do ciclo
            tot_racao = db.query(func.sum(LancamentoAlimentacao.total_dia_kg)).filter(
                LancamentoAlimentacao.ciclo_id == ciclo.id
            ).scalar() or 0.0
            ciclo.racao_total_kg = round(tot_racao, 2)

            # Se houver despesca identificada, consolida e encerra o ciclo
            if despesca_detectada:
                d_data = despesca_detectada["data"]
                d_kg = despesca_detectada["colhido_kg"]
                d_peso = despesca_detectada["peso_final_g"]
                d_obs = despesca_detectada["obs"]

                ciclo.status = "ENCERRADO"
                ciclo.data_despesca = d_data
                ciclo.camarao_colhido_kg = d_kg
                ciclo.peso_final_g = d_peso
                sob_real = round(((d_kg * 1000 / d_peso) / ciclo.pls_estocadas) * 100, 1) if ciclo.pls_estocadas > 0 else 0.0
                ciclo.sobrevivencia_real_pct = sob_real
                ciclo.fca_real_final = round(tot_racao / d_kg, 2) if d_kg > 0 else 1.25
                ciclo.produtividade_kg_ha = round(d_kg / (viveiro.area_ha or 1.0), 2)
                ciclo.faturamento_total_rs = round(d_kg * 22.0, 2)

                desp_existente = db.query(DespescaVenda).filter(
                    DespescaVenda.fazenda_id == fazenda_id,
                    DespescaVenda.ciclo_id == ciclo.id
                ).first()
                if not desp_existente:
                    nova_desp = DespescaVenda(
                        fazenda_id=fazenda_id,
                        ciclo_id=ciclo.id,
                        data=d_data,
                        tipo_despesca="TOTAL",
                        gramatura_media_g=d_peso,
                        camarao_colhido_kg=d_kg,
                        comprador="Mercado Local / ABCC",
                        preco_kg_rs=22.0,
                        faturamento_bruto_rs=round(d_kg * 22.0, 2),
                        observacoes=d_obs
                    )
                    db.add(nova_desp)
                else:
                    desp_existente.data = d_data
                    desp_existente.gramatura_media_g = d_peso
                    desp_existente.camarao_colhido_kg = d_kg
                    desp_existente.faturamento_bruto_rs = round(d_kg * (desp_existente.preco_kg_rs or 22.0), 2)

                relatorio_viv["despesca"] = {
                    "data": d_data.strftime("%d/%m/%Y"),
                    "colhido_kg": d_kg,
                    "peso_final_g": d_peso,
                    "sobrevivencia_pct": sob_real
                }

            resumo["abas_processadas"].append({"aba": sheet_name, "status": "PROCESSADO", "linhas": linhas_aba})
            resumo["novidades_por_viveiro"][cod_viveiro] = relatorio_viv

        db.commit()
        wb.close()
        return resumo

    @classmethod
    def processar_planilha_agua(
        cls,
        db: Session,
        arquivo_ou_caminho: Union[str, Path, BinaryIO, bytes],
        fazenda_id: str,
        fazenda_codigo: str = "FAZ_ARRENDADA"
    ) -> Dict[str, Any]:
        """Lê e ingere a planilha Controle_Qualidade_Agua.xlsx."""
        if isinstance(arquivo_ou_caminho, bytes):
            arquivo_ou_caminho = io.BytesIO(arquivo_ou_caminho)

        wb = openpyxl.load_workbook(arquivo_ou_caminho, data_only=True)
        resumo = {
            "tipo": "QUALIDADE_AGUA",
            "fazenda_id": fazenda_id,
            "fazenda_codigo": fazenda_codigo,
            "abas_processadas": [],
            "linhas_lidas": 0,
            "novas_medicoes": 0,
            "duplicatas_ignoradas": 0,
            "alertas_criticos": 0,
        }

        padrao_viveiro = re.compile(r"^V-\d{2}$", re.IGNORECASE)

        for sheet_name in wb.sheetnames:
            if not padrao_viveiro.match(sheet_name.strip()):
                continue

            ws = wb[sheet_name]
            cod_viveiro = sheet_name.strip().upper()

            viveiro = db.query(Viveiro).filter(
                Viveiro.fazenda_id == fazenda_id,
                Viveiro.codigo == cod_viveiro
            ).first()

            if not viveiro:
                viveiro = Viveiro(
                    fazenda_id=fazenda_id,
                    codigo=cod_viveiro,
                    nome=f"Viveiro {cod_viveiro.replace('V-', '')}",
                    area_ha=0.5,
                    tipo="ENGORDA",
                    status="ATIVO"
                )
                db.add(viveiro)
                db.flush()

            ciclo = db.query(CicloCultivo).filter(
                CicloCultivo.fazenda_id == fazenda_id,
                CicloCultivo.viveiro_id == viveiro.id,
                CicloCultivo.status == "EM CULTIVO ATIVO"
            ).first()

            linhas_aba = 0
            # Salto mandatório L1 a L9: dados iniciam na Linha 10
            for r in range(10, ws.max_row + 1):
                val_data = converter_para_data(ws.cell(r, 2).value)
                if not val_data:
                    continue

                linhas_aba += 1
                resumo["linhas_lidas"] += 1

                dia_ciclo = int(ws.cell(r, 1).value or 1)
                o2_m = float(ws.cell(r, 3).value) if ws.cell(r, 3).value is not None else None
                o2_n = float(ws.cell(r, 4).value) if ws.cell(r, 4).value is not None else None
                sal = float(ws.cell(r, 5).value) if ws.cell(r, 5).value is not None else None
                ph_m = float(ws.cell(r, 6).value) if ws.cell(r, 6).value is not None else None
                ph_t = float(ws.cell(r, 7).value) if ws.cell(r, 7).value is not None else None
                delta_ph = float(ws.cell(r, 8).value) if ws.cell(r, 8).value is not None else (
                    round(ph_t - ph_m, 2) if (ph_t is not None and ph_m is not None) else None
                )
                secchi = float(ws.cell(r, 9).value) if ws.cell(r, 9).value is not None else None
                amonia = float(ws.cell(r, 10).value) if ws.cell(r, 10).value is not None else None
                nitrito = float(ws.cell(r, 11).value) if ws.cell(r, 11).value is not None else None
                status_tanque = str(ws.cell(r, 12).value or "").strip().upper()
                acoes = str(ws.cell(r, 13).value or "").strip() or None

                # Classificação automática zootécnica se status vier em branco
                if not status_tanque or status_tanque not in ["OTIMO", "ATENCAO", "CRITICO"]:
                    status_tanque = ZootecniaService.classificar_status_agua(
                        o2_manha=o2_m,
                        o2_noite=o2_n,
                        amonia_mg_l=amonia,
                        nitrito_mg_l=nitrito,
                        delta_ph=delta_ph,
                        secchi_cm=secchi
                    )

                h_linha = calcular_hash_agua(fazenda_codigo, cod_viveiro, val_data, o2_m, o2_n, sal, ph_m)

                existente = db.query(MonitoramentoAgua).filter(
                    MonitoramentoAgua.hash_linha == h_linha
                ).first()

                if existente:
                    resumo["duplicatas_ignoradas"] += 1
                    continue

                existente_data = db.query(MonitoramentoAgua).filter(
                    MonitoramentoAgua.viveiro_id == viveiro.id,
                    MonitoramentoAgua.data == val_data
                ).first()

                if existente_data:
                    # Conflito de medição na mesma data
                    pend = AuditoriaPendencia(
                        fazenda_id=fazenda_id,
                        origem="INGESTAO_EXCEL",
                        entidade="AGUA",
                        viveiro_codigo=cod_viveiro,
                        data_evento=val_data,
                        tipo_anomalia="CONFLITO_DADOS",
                        severidade="INFO",
                        mensagem=f"Medição de água duplicada no {cod_viveiro} para {val_data}."
                    )
                    db.add(pend)
                    continue

                medicao = MonitoramentoAgua(
                    fazenda_id=fazenda_id,
                    viveiro_id=viveiro.id,
                    ciclo_id=ciclo.id if ciclo else None,
                    data=val_data,
                    dia_ciclo=dia_ciclo,
                    o2_manha=o2_m,
                    o2_noite=o2_n,
                    salinidade_ppt=sal,
                    ph_manha=ph_m,
                    ph_tarde=ph_t,
                    delta_ph=delta_ph,
                    transparencia_secchi_cm=secchi,
                    amonia_mg_l=amonia,
                    nitrito_mg_l=nitrito,
                    status_tanque=status_tanque,
                    acoes_adotadas=acoes,
                    hash_linha=h_linha
                )
                db.add(medicao)
                resumo["novas_medicoes"] += 1

                # Disparo de Alerta Crítico para anóxia ou amônia tóxica
                if (o2_m is not None and o2_m < 3.0) or (o2_n is not None and o2_n < 3.0):
                    menor_o2 = min([x for x in [o2_m, o2_n] if x is not None])
                    pend = AuditoriaPendencia(
                        fazenda_id=fazenda_id,
                        origem="INGESTAO_EXCEL",
                        entidade="AGUA",
                        viveiro_codigo=cod_viveiro,
                        data_evento=val_data,
                        tipo_anomalia="O2_CRITICO",
                        severidade="CRITICA",
                        mensagem=f"ALERTA CRÍTICO: O2 aferido em {menor_o2:.1f} mg/L no viveiro {cod_viveiro} em {val_data} (Risco iminente de mortalidade por asfixia)!"
                    )
                    db.add(pend)
                    resumo["alertas_criticos"] += 1

                elif amonia is not None and amonia > 0.1:
                    pend = AuditoriaPendencia(
                        fazenda_id=fazenda_id,
                        origem="INGESTAO_EXCEL",
                        entidade="AGUA",
                        viveiro_codigo=cod_viveiro,
                        data_evento=val_data,
                        tipo_anomalia="AMONIA_TOXICA",
                        severidade="CRITICA",
                        mensagem=f"ALERTA CRÍTICO: Amônia tóxica em {amonia:.2f} mg/L no {cod_viveiro} em {val_data}!"
                    )
                    db.add(pend)
                    resumo["alertas_criticos"] += 1

            resumo["abas_processadas"].append({"aba": sheet_name, "status": "PROCESSADO", "linhas": linhas_aba})

        db.commit()
        wb.close()
        return resumo

    @classmethod
    def processar_planilha_contabil(
        cls,
        db: Session,
        arquivo_ou_caminho: Union[str, Path, BinaryIO, bytes],
        fazenda_id: str,
        fazenda_codigo: str = "FAZ_ARRENDADA"
    ) -> Dict[str, Any]:
        """
        Lê e ingere de forma gradativa a planilha oficial Registro_de_Custos_e_Contas.xlsx:
        1. Realiza backup diário automático em '03_BACKUPS_DIARIOS' caso seja caminho em disco.
        2. Pula as linhas institucionais 1 a 9 e lê a aba 'Lancamento_Contas' a partir da Linha 10.
        3. Aplica Bloqueio Automático Estrito de Redundância (Fazenda + Fornecedor + Vencimento + Valor).
        4. Atualiza o status (PENDENTE -> PAGO) ou o Centro de Custo/Viveiro caso a mesma conta tenha sido editada.
        """
        import shutil as _shutil

        nome_backup_gerado = None
        if isinstance(arquivo_ou_caminho, (str, Path)):
            caminho_p = Path(arquivo_ou_caminho)
            if caminho_p.exists():
                dir_bkp = caminho_p.parent / "03_BACKUPS_DIARIOS"
                dir_bkp.mkdir(parents=True, exist_ok=True)
                hoje_str = datetime.now().strftime("%Y-%m-%d")
                nome_backup_gerado = f"Registro_de_Custos_e_Contas_BACKUP_{hoje_str}.xlsx"
                _shutil.copy2(caminho_p, dir_bkp / nome_backup_gerado)

        if isinstance(arquivo_ou_caminho, bytes):
            arquivo_ou_caminho = io.BytesIO(arquivo_ou_caminho)

        wb = openpyxl.load_workbook(arquivo_ou_caminho, data_only=True)
        aba_alvo = "Lancamento_Contas" if "Lancamento_Contas" in wb.sheetnames else wb.sheetnames[0]
        ws = wb[aba_alvo]

        resumo = {
            "tipo": "CONTABILIDADE_CUSTOS_E_CONTAS",
            "fazenda_id": fazenda_id,
            "fazenda_codigo": fazenda_codigo,
            "aba_processada": aba_alvo,
            "backup_diario": nome_backup_gerado,
            "linhas_lidas": 0,
            "novos_lancamentos": 0,
            "atualizacoes_incremental": 0,
            "duplicatas_bloqueadas": 0,
            "itens_bloqueados": [],
            "itens_inseridos": [],
            "itens_atualizados": [],
        }

        chaves_vistas_neste_lote = set()

        # Leitura estrita a partir da Linha 10
        for r in range(10, ws.max_row + 1):
            c_valor = ws.cell(r, 8).value
            c_desc = ws.cell(r, 6).value

            # Se linha estiver em branco (sem valor ou descrição), ignora
            if c_valor is None or str(c_valor).strip() == "" or not c_desc:
                continue

            try:
                valor_rs = float(c_valor)
            except (ValueError, TypeError):
                continue

            if valor_rs <= 0:
                continue

            resumo["linhas_lidas"] += 1

            dt_comp = converter_para_data(ws.cell(r, 2).value)
            dt_venc = converter_para_data(ws.cell(r, 3).value) or dt_comp or date.today()
            if not dt_comp:
                dt_comp = dt_venc

            tipo_raw = str(ws.cell(r, 4).value or "SAÍDA").strip().upper()
            tipo_mov = "ENTRADA" if "ENTRADA" in tipo_raw else "SAIDA"

            conta_raw = str(ws.cell(r, 5).value or "3.1.01 - Ração e Nutrição").strip()
            partes_conta = conta_raw.split(" - ", 1)
            codigo_conta = partes_conta[0].strip() if len(partes_conta) > 1 else "3.1.01"
            grupo_contabil = mapear_grupo_contabil(codigo_conta)

            descricao = str(c_desc).strip()
            fornecedor = str(ws.cell(r, 7).value or "Fornecedor Geral").strip()
            status_raw = str(ws.cell(r, 9).value or "PENDENTE").strip().upper()
            status_pgto = "PAGO" if status_raw in ["PAGO", "RECEBIDO", "LIQUIDADO"] else "PENDENTE"
            dt_liq = converter_para_data(ws.cell(r, 11).value)
            if status_pgto == "PAGO" and not dt_liq:
                dt_liq = dt_venc

            forma_pgto = str(ws.cell(r, 12).value or "Boleto Bancário").strip()

            # Regra de Alocação por Viveiro sob Controle do Usuário:
            # Se não especificado no documento/planilha, fica como 'Geral da Fazenda'
            viv_raw = str(ws.cell(r, 13).value or "").strip()
            centro_custo = viv_raw if viv_raw else "Geral da Fazenda"

            faz_raw = str(ws.cell(r, 14).value or "Fazenda Arrendada").strip().upper()
            target_faz_id = FAZENDA_HAKKA_ID if "HAKKA" in faz_raw else FAZENDA_PADRAO_ID

            arq_nota = str(ws.cell(r, 15).value or "").strip() or None

            chave_dedup = calcular_chave_contabil_estrita(
                target_faz_id, fornecedor, dt_venc, valor_rs
            )

            # 1. Bloqueio se a mesma linha apareceu duplicada dentro da própria planilha
            if chave_dedup in chaves_vistas_neste_lote:
                resumo["duplicatas_bloqueadas"] += 1
                resumo["itens_bloqueados"].append(
                    f"Linha {r}: {fornecedor} (R$ {valor_rs:.2f} venc. {dt_venc.strftime('%d/%m/%Y')}) — duplicata na planilha"
                )
                continue

            chaves_vistas_neste_lote.add(chave_dedup)

            # 2. Verifica se já existe no banco de dados pela chave estrita
            existente = db.query(LancamentoContabil).filter(
                LancamentoContabil.chave_dedup == chave_dedup
            ).first()

            if existente:
                # Verifica se o usuário atualizou o status (PENDENTE -> PAGO) ou mudou o Viveiro alocado
                mudou_status = existente.status_pagamento != status_pgto
                mudou_viveiro = existente.centro_custo_viveiro != centro_custo
                mudou_conta = existente.nome_conta != conta_raw

                if mudou_status or mudou_viveiro or mudou_conta:
                    existente.status_pagamento = status_pgto
                    existente.data_liquidacao = dt_liq
                    existente.centro_custo_viveiro = centro_custo
                    existente.codigo_conta = codigo_conta
                    existente.nome_conta = conta_raw
                    existente.grupo_contabil = grupo_contabil
                    existente.descricao = descricao
                    if arq_nota:
                        existente.arquivo_nota = arq_nota
                    resumo["atualizacoes_incremental"] += 1
                    resumo["itens_atualizados"].append(
                        f"{fornecedor} (R$ {valor_rs:.2f}): atualizado ({status_pgto} • {centro_custo})"
                    )
                else:
                    # Redundância 100% idêntica bloqueada automaticamente
                    resumo["duplicatas_bloqueadas"] += 1
                    resumo["itens_bloqueados"].append(
                        f"{fornecedor} - R$ {valor_rs:.2f} ({dt_venc.strftime('%d/%m/%Y')})"
                    )
                continue

            # 3. Registro inédito: insere no Livro Diário
            novo = LancamentoContabil(
                fazenda_id=target_faz_id,
                data_competencia=dt_comp,
                data_vencimento=dt_venc,
                data_liquidacao=dt_liq,
                tipo_movimento=tipo_mov,
                codigo_conta=codigo_conta,
                nome_conta=conta_raw,
                grupo_contabil=grupo_contabil,
                descricao=descricao,
                fornecedor_cliente=fornecedor,
                valor_rs=valor_rs,
                status_pagamento=status_pgto,
                forma_pagamento=forma_pgto,
                centro_custo_viveiro=centro_custo,
                arquivo_nota=arq_nota,
                origem="PLANILHA_EXCEL",
                chave_dedup=chave_dedup,
            )
            db.add(novo)
            resumo["novos_lancamentos"] += 1
            resumo["itens_inseridos"].append(
                f"{dt_comp.strftime('%d/%m/%Y')} • {fornecedor}: R$ {valor_rs:.2f} ({centro_custo})"
            )

        # Registra log do backup e da sincronização
        log_bkp = LogBackupContabil(
            fazenda_id=fazenda_id,
            tipo_operacao="SYNC_PLANILHA_CONTABIL",
            arquivo_backup=nome_backup_gerado or "Upload Manual XLSX",
            novos_lancamentos=resumo["novos_lancamentos"],
            atualizacoes_status=resumo["atualizacoes_incremental"],
            duplicatas_bloqueadas=resumo["duplicatas_bloqueadas"],
            detalhes=f"Lidas {resumo['linhas_lidas']} linhas da aba {aba_alvo}."
        )
        db.add(log_bkp)
        db.commit()
        wb.close()
        return resumo
