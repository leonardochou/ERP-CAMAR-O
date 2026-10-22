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
from sqlalchemy import desc

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.despesca import DespescaVenda
from app.models.auditoria import AuditoriaPendencia
from app.services.zootecnia_service import ZootecniaService


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
        for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
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

        # Abas que representam viveiros (ex: V-01, V-02, ..., V-15)
        padrao_viveiro = re.compile(r"^V-\d{2}$", re.IGNORECASE)

        for sheet_name in wb.sheetnames:
            if not padrao_viveiro.match(sheet_name.strip()):
                continue

            ws = wb[sheet_name]
            cod_viveiro = sheet_name.strip().upper()

            # Inicializa relatório do viveiro
            relatorio_viv = {
                "dias_novos": [],
                "novas_biometrias": [],
                "atualizados": [],
                "duplicatas_ignoradas": 0,
                "laboratorio": "",
                "pls_estocadas": 0,
                "data_povoamento": None,
                "despesca": None
            }

            # Localiza ou cadastra o viveiro
            viveiro = db.query(Viveiro).filter(
                Viveiro.fazenda_id == fazenda_id,
                Viveiro.codigo == cod_viveiro
            ).first()

            # Extração de Metadados do Ciclo (Linhas 2 e 3)
            area_ha = 0.5
            try:
                val_area = ws.cell(2, 2).value
                if val_area and isinstance(val_area, (int, float)):
                    area_ha = float(val_area)
            except Exception:
                pass

            if not viveiro:
                viveiro = Viveiro(
                    fazenda_id=fazenda_id,
                    codigo=cod_viveiro,
                    nome=f"Viveiro {cod_viveiro.replace('V-', '')}",
                    area_ha=area_ha,
                    tipo="ENGORDA",
                    status="ATIVO"
                )
                db.add(viveiro)
                db.flush()

            # Metadados do Ciclo Cultivo (Linhas 2 e 3)
            lab = str(ws.cell(2, 4).value or "AQUATEC").strip()
            peso_ini = float(ws.cell(2, 6).value or 0.01)
            status_lote = str(ws.cell(2, 8).value or "EM CULTIVO ATIVO").strip().upper()
            pls_mil = float(ws.cell(3, 2).value or 65.0)
            pls_qtd = int(pls_mil * 1000)
            dt_povoamento = converter_para_data(ws.cell(3, 4).value) or date(2026, 6, 19)

            relatorio_viv["laboratorio"] = lab
            relatorio_viv["pls_estocadas"] = pls_qtd
            relatorio_viv["data_povoamento"] = dt_povoamento.strftime("%d/%m/%Y")

            # Localiza ciclo ativo existente ou cria novo
            ciclo = db.query(CicloCultivo).filter(
                CicloCultivo.fazenda_id == fazenda_id,
                CicloCultivo.viveiro_id == viveiro.id,
                CicloCultivo.status.in_(["EM CULTIVO ATIVO", "DESPESCADO"])
            ).first()

            if not ciclo:
                numero_lote = f"LOTE-2026-{cod_viveiro}"
                ciclo = db.query(CicloCultivo).filter(
                    CicloCultivo.fazenda_id == fazenda_id,
                    CicloCultivo.numero_lote == numero_lote
                ).first()

            if not ciclo:
                densidade = round(pls_qtd / (viveiro.area_ha * 10000), 2) if viveiro.area_ha else 13.0
                ciclo = CicloCultivo(
                    fazenda_id=fazenda_id,
                    viveiro_id=viveiro.id,
                    numero_lote=f"LOTE-2026-{cod_viveiro}",
                    data_povoamento=dt_povoamento,
                    pls_estocadas=pls_qtd,
                    densidade_pl_m2=densidade,
                    laboratorio=lab,
                    peso_inicial_g=peso_ini,
                    status=status_lote if status_lote in ["EM CULTIVO ATIVO", "DESPESCADO", "EM PREPARACAO"] else "EM CULTIVO ATIVO"
                )
                db.add(ciclo)
                db.flush()
            else:
                # Atualiza dados de povoamento caso tenham sido refinados na planilha
                if lab and lab != "0":
                    ciclo.laboratorio = lab
                if pls_qtd > 0:
                    ciclo.pls_estocadas = pls_qtd
                if dt_povoamento:
                    ciclo.data_povoamento = dt_povoamento

            # Extração de Encerramento do Lote / Despesca (Linha 5 da aba)
            val_dt_desp = converter_para_data(ws.cell(5, 2).value)
            val_colhido = ws.cell(5, 4).value
            val_peso_final = ws.cell(5, 6).value

            if val_dt_desp and val_colhido and isinstance(val_colhido, (int, float)) and val_colhido > 0:
                colhido_kg = float(val_colhido)
                peso_fim_g = float(val_peso_final) if val_peso_final and isinstance(val_peso_final, (int, float)) else 12.0
                ciclo.status = "DESPESCADO"
                
                # Registra ou atualiza DespescaVenda
                desp_existente = db.query(DespescaVenda).filter(
                    DespescaVenda.fazenda_id == fazenda_id,
                    DespescaVenda.ciclo_id == ciclo.id
                ).first()

                if not desp_existente:
                    nova_desp = DespescaVenda(
                        fazenda_id=fazenda_id,
                        ciclo_id=ciclo.id,
                        data=val_dt_desp,
                        tipo_despesca="TOTAL",
                        gramatura_media_g=peso_fim_g,
                        camarao_colhido_kg=colhido_kg,
                        comprador="Mercado Local / ABCC",
                        preco_kg_rs=22.0,
                        faturamento_bruto_rs=colhido_kg * 22.0,
                        observacoes="Despesca importada da planilha oficial."
                    )
                    db.add(nova_desp)
                else:
                    desp_existente.data = val_dt_desp
                    desp_existente.gramatura_media_g = peso_fim_g
                    desp_existente.camarao_colhido_kg = colhido_kg
                    desp_existente.faturamento_bruto_rs = colhido_kg * desp_existente.preco_kg_rs

                sob_real = round(((colhido_kg * 1000 / peso_fim_g) / ciclo.pls_estocadas) * 100, 1) if ciclo.pls_estocadas > 0 else 0.0
                relatorio_viv["despesca"] = {
                    "data": val_dt_desp.strftime("%d/%m/%Y"),
                    "colhido_kg": colhido_kg,
                    "peso_final_g": peso_fim_g,
                    "sobrevivencia_pct": sob_real
                }

            # Ignora abas que estejam explicitamente em preparação sem dados
            if ciclo.status == "EM PREPARACAO":
                resumo["abas_processadas"].append({"aba": sheet_name, "status": "EM PREPARACAO", "linhas": 0})
                continue

            linhas_aba = 0
            # Salto mandatório L1 a L9: dados operacionais iniciam rigorosamente na Linha 10
            for r in range(10, ws.max_row + 1):
                val_data = converter_para_data(ws.cell(r, 1).value)
                if not val_data:
                    continue

                # Leitura e sanitização dos dados operacionais da linha
                c_racao_m = ws.cell(r, 3).value
                c_racao_t = ws.cell(r, 5).value
                c_biometria = ws.cell(r, 9).value
                c_obs = ws.cell(r, 11).value

                tem_racao_m = c_racao_m is not None and str(c_racao_m).strip() != ""
                tem_racao_t = c_racao_t is not None and str(c_racao_t).strip() != ""
                tem_bio = c_biometria is not None and str(c_biometria).strip() != ""
                tem_observacao = c_obs is not None and str(c_obs).strip() != ""

                # REGRA DE OURO: Se a linha for dia futuro em branco (sem ração, biometria ou obs), IGNORA!
                if not (tem_racao_m or tem_racao_t or tem_bio or tem_observacao):
                    continue

                linhas_aba += 1
                resumo["linhas_lidas"] += 1

                doc_val = int(ws.cell(r, 2).value or 1)
                racao_m = float(c_racao_m or 0.0) if tem_racao_m else 0.0
                sobra_m_raw = ws.cell(r, 4).value
                sobra_m = int(sobra_m_raw) if sobra_m_raw is not None and str(sobra_m_raw).isdigit() else 0

                racao_t = float(c_racao_t or 0.0) if tem_racao_t else 0.0
                sobra_t_raw = ws.cell(r, 6).value
                sobra_t = int(sobra_t_raw) if sobra_t_raw is not None and str(sobra_t_raw).isdigit() else 0

                total_dia = float(ws.cell(r, 7).value or (racao_m + racao_t))
                acumulado = float(ws.cell(r, 8).value or total_dia)
                biometria_peso = float(c_biometria) if tem_bio and isinstance(c_biometria, (int, float)) else None
                gmd_val = ws.cell(r, 10).value
                obs = str(c_obs).strip() if tem_observacao else None

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
                    # Registro de alimentação 100% idêntico já existe
                    resumo["duplicatas_ignoradas"] += 1
                    relatorio_viv["duplicatas_ignoradas"] += 1

                    # Mas confere se este dia ganhou uma biometria nova ou complementar
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
                                observacoes=obs
                            )
                            db.add(nova_bio)
                            resumo["biometrias_registradas"] += 1
                            relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")
                    continue

                if existente_data:
                    # Enriquecimento incremental (Upsert Inteligente): o mesmo dia recebeu novos dados (ex: turno tarde ou biometria)
                    existente_data.racao_manha_kg = racao_m
                    existente_data.sobra_manha = sobra_m
                    existente_data.racao_tarde_kg = racao_t
                    existente_data.sobra_tarde = sobra_t
                    existente_data.total_dia_kg = total_dia
                    existente_data.consumo_acumulado_kg = acumulado
                    existente_data.hash_linha = h_linha
                    if obs:
                        existente_data.observacoes = obs

                    resumo["atualizacoes_incremental"] += 1
                    relatorio_viv["atualizados"].append(f"{data_fmt}: Ração atualizada ({total_dia:.1f}kg)")

                    # Processa ou atualiza biometria
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
                                observacoes=obs
                            )
                            db.add(nova_bio)
                            resumo["biometrias_registradas"] += 1
                            relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")
                        else:
                            bio_exist.peso_medio_g = biometria_peso
                            if gmd_val and isinstance(gmd_val, (int, float)):
                                bio_exist.gmd_g_dia = float(gmd_val)
                    continue

                # Cria novo lançamento para dia inédito
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
                    observacoes=obs
                )
                db.add(novo_trato)
                resumo["novos_lancamentos"] += 1
                relatorio_viv["dias_novos"].append(f"{data_fmt}: {total_dia:.1f}kg (DOC {doc_val})")

                # Processa biometria associada, se informada na coluna 9
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
                        observacoes=obs
                    )
                    db.add(nova_bio)
                    resumo["biometrias_registradas"] += 1
                    relatorio_viv["novas_biometrias"].append(f"{data_fmt}: {biometria_peso}g")

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
