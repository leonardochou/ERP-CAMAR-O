"""Endpoints REST para o Hub Contábil: Plano de Contas, DRE, Fluxo de Caixa, Anti-Redundância, GED e Backups."""
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.contabilidade import LancamentoContabil, LogBackupContabil
from app.services.ingestor_service import (
    IngestorService,
    calcular_chave_contabil_estrita,
    mapear_grupo_contabil,
)

router = APIRouter()

DIRETORIO_CONTABIL = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\MODELOS DE CONTROLE\Registro de custos e contas")
PLANILHA_CONTABIL_PATH = DIRETORIO_CONTABIL / "Registro_de_Custos_e_Contas.xlsx"


class NovoLancamentoContabilInput(BaseModel):
    data_competencia: date
    data_vencimento: date
    data_liquidacao: Optional[date] = None
    tipo_movimento: str = "SAIDA"
    nome_conta: str = "3.1.01 - Ração e Nutrição"
    descricao: str
    fornecedor_cliente: str
    valor_rs: float
    status_pagamento: str = "PENDENTE"
    forma_pagamento: str = "Boleto Bancário"
    centro_custo_viveiro: Optional[str] = "Geral da Fazenda"
    arquivo_nota: Optional[str] = None


class AtualizarViveiroInput(BaseModel):
    centro_custo_viveiro: str


class AtualizarStatusInput(BaseModel):
    status_pagamento: str
    data_liquidacao: Optional[date] = None


@router.get("/resumo-completo", summary="Retorna Plano de Contas, DRE, Fluxo de Caixa, Livro Diário, GED e Backups")
def obter_resumo_contabil_completo(
    regime: str = Query("COMPETENCIA", description="COMPETENCIA ou CAIXA"),
    centro_custo: str = Query("TODOS", description="TODOS, Geral da Fazenda, ou V-01..V-15"),
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Consolida em tempo real as 4 visões contábeis do ERP:
    1. Plano de Contas & Livro Diário
    2. DRE (Demonstração do Resultado do Exercício)
    3. Fluxo de Caixa (Realizado e Projetado)
    4. Importação Excel, GED (Pasta do Drive) e Backups Diários
    """
    # Se o banco ainda estiver vazio de lançamentos contábeis e a planilha existir, sincroniza automaticamente!
    total_no_banco = db.query(LancamentoContabil).count()
    if total_no_banco == 0 and PLANILHA_CONTABIL_PATH.exists():
        IngestorService.processar_planilha_contabil(
            db=db,
            arquivo_ou_caminho=PLANILHA_CONTABIL_PATH,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )

    query = db.query(LancamentoContabil).filter(LancamentoContabil.fazenda_id == fazenda.id)
    if centro_custo and centro_custo.upper() != "TODOS":
        query = query.filter(LancamentoContabil.centro_custo_viveiro == centro_custo)

    lancamentos = query.order_by(desc(LancamentoContabil.data_competencia), desc(LancamentoContabil.id)).all()

    # 1. Consolidação da DRE (por Regime de Competência ou Caixa)
    dre = {
        "receita_bruta": 0.0,
        "deducoes_impostos": 0.0,
        "receita_liquida": 0.0,
        "custos_variaveis": 0.0,
        "margem_contribuicao": 0.0,
        "despesas_fixas": 0.0,
        "ebitda": 0.0,
        "resultado_financeiro": 0.0,
        "lucro_liquido": 0.0,
        "detalhe_contas": {}
    }

    # 2. Consolidação do Fluxo de Caixa
    fluxo = {
        "entradas_realizadas": 0.0,
        "saidas_pagas": 0.0,
        "saldo_caixa_realizado": 0.0,
        "entradas_a_receber": 0.0,
        "saidas_a_pagar": 0.0,
        "saldo_projetado_final": 0.0,
        "mensal": {m: {"entradas_pagas": 0.0, "saidas_pagas": 0.0, "pendentes": 0.0} for m in range(1, 13)}
    }

    # 3. Plano de Contas Acumulado
    mapa_plano_contas: Dict[str, Dict[str, Any]] = {}

    livro_diario = []
    hoje = date.today()

    for l in lancamentos:
        eh_pago = l.status_pagamento == "PAGO"
        eh_entrada = l.tipo_movimento == "ENTRADA"
        val = float(l.valor_rs or 0.0)

        # Situação do prazo
        if eh_pago:
            situacao_prazo = "LIQUIDADO"
        elif l.data_vencimento < hoje:
            situacao_prazo = "VENCIDO"
        elif (l.data_vencimento - hoje).days <= 7:
            situacao_prazo = "VENCE EM BREVE"
        else:
            situacao_prazo = "A VENCER"

        livro_diario.append({
            "id": l.id,
            "data_competencia": l.data_competencia.isoformat(),
            "data_vencimento": l.data_vencimento.isoformat(),
            "data_liquidacao": l.data_liquidacao.isoformat() if l.data_liquidacao else None,
            "tipo_movimento": l.tipo_movimento,
            "codigo_conta": l.codigo_conta,
            "nome_conta": l.nome_conta,
            "grupo_contabil": l.grupo_contabil,
            "descricao": l.descricao,
            "fornecedor_cliente": l.fornecedor_cliente,
            "valor_rs": val,
            "status_pagamento": l.status_pagamento,
            "situacao_prazo": situacao_prazo,
            "forma_pagamento": l.forma_pagamento,
            "centro_custo_viveiro": l.centro_custo_viveiro,
            "arquivo_nota": l.arquivo_nota,
            "origem": l.origem,
        })

        # Soma no Plano de Contas
        if l.nome_conta not in mapa_plano_contas:
            mapa_plano_contas[l.nome_conta] = {
                "codigo_conta": l.codigo_conta,
                "nome_conta": l.nome_conta,
                "grupo_contabil": l.grupo_contabil,
                "tipo_movimento": l.tipo_movimento,
                "realizado_rs": 0.0,
                "pendente_rs": 0.0,
                "total_competencia_rs": 0.0,
                "qtd_lancamentos": 0
            }
        mapa_plano_contas[l.nome_conta]["total_competencia_rs"] += val
        mapa_plano_contas[l.nome_conta]["qtd_lancamentos"] += 1
        if eh_pago:
            mapa_plano_contas[l.nome_conta]["realizado_rs"] += val
        else:
            mapa_plano_contas[l.nome_conta]["pendente_rs"] += val

        # Soma no Fluxo de Caixa
        mes_ref = l.data_vencimento.month
        if eh_entrada:
            if eh_pago:
                fluxo["entradas_realizadas"] += val
                fluxo["mensal"][mes_ref]["entradas_pagas"] += val
            else:
                fluxo["entradas_a_receber"] += val
        else:
            if eh_pago:
                fluxo["saidas_pagas"] += val
                fluxo["mensal"][mes_ref]["saidas_pagas"] += val
            else:
                fluxo["saidas_a_pagar"] += val
                fluxo["mensal"][mes_ref]["pendentes"] += val

        # Soma na DRE (se regime == CAIXA, considera apenas PAGO; se COMPETENCIA, considera todos exceto CAPEX)
        entra_na_dre = True if regime.upper() == "COMPETENCIA" else eh_pago
        if entra_na_dre and l.grupo_contabil != "CAPEX":
            if l.grupo_contabil == "RECEITA_BRUTA":
                dre["receita_bruta"] += val
            elif l.grupo_contabil == "DEDUCOES":
                dre["deducoes_impostos"] += val
            elif l.grupo_contabil == "CUSTO_VARIAVEL":
                dre["custos_variaveis"] += val
            elif l.grupo_contabil == "DESPESA_FIXA":
                dre["despesas_fixas"] += val
            elif l.grupo_contabil == "RESULTADO_FINANCEIRO":
                if eh_entrada:
                    dre["resultado_financeiro"] += val
                else:
                    dre["resultado_financeiro"] -= val

    dre["receita_liquida"] = round(dre["receita_bruta"] - dre["deducoes_impostos"], 2)
    dre["margem_contribuicao"] = round(dre["receita_liquida"] - dre["custos_variaveis"], 2)
    dre["ebitda"] = round(dre["margem_contribuicao"] - dre["despesas_fixas"], 2)
    dre["lucro_liquido"] = round(dre["ebitda"] + dre["resultado_financeiro"], 2)

    fluxo["saldo_caixa_realizado"] = round(fluxo["entradas_realizadas"] - fluxo["saidas_pagas"], 2)
    fluxo["saldo_projetado_final"] = round(
        fluxo["saldo_caixa_realizado"] + fluxo["entradas_a_receber"] - fluxo["saidas_a_pagar"], 2
    )

    # Logs de Backups e Redundâncias Bloqueadas
    logs_bkp = db.query(LogBackupContabil).filter(
        LogBackupContabil.fazenda_id == fazenda.id
    ).order_by(desc(LogBackupContabil.id)).limit(15).all()

    total_duplicatas_bloqueadas = sum(lb.duplicatas_bloqueadas for lb in logs_bkp)

    # Inspeciona pastas físicas do Drive (01_ENVIAR_NOTAS_AQUI, 02_ARQUIVADAS_POR_MES, 03_BACKUPS_DIARIOS)
    dir_inbox = DIRETORIO_CONTABIL / "01_ENVIAR_NOTAS_AQUI"
    dir_arch = DIRETORIO_CONTABIL / "02_ARQUIVADAS_POR_MES"
    dir_bkp = DIRETORIO_CONTABIL / "03_BACKUPS_DIARIOS"

    arquivos_inbox = [f.name for f in dir_inbox.glob("*") if f.is_file() and not f.name.startswith("LEIA_ME")] if dir_inbox.exists() else []
    arquivos_bkp = [
        {
            "nome": f.name,
            "tamanho_kb": round(f.stat().st_size / 1024, 1),
            "data_hora": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        }
        for f in sorted(dir_bkp.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    ] if dir_bkp.exists() else []

    return {
        "fazenda": {
            "id": fazenda.id,
            "codigo": fazenda.codigo,
            "nome": fazenda.nome
        },
        "regime_selecionado": regime.upper(),
        "centro_custo_selecionado": centro_custo,
        "dre": dre,
        "fluxo_caixa": fluxo,
        "plano_de_contas": sorted(mapa_plano_contas.values(), key=lambda x: x["codigo_conta"]),
        "livro_diario": livro_diario,
        "ged_e_backups": {
            "pasta_entrada_notas": str(dir_inbox),
            "pasta_arquivadas": str(dir_arch),
            "pasta_backups": str(dir_bkp),
            "notas_aguardando_ia": arquivos_inbox,
            "backups_diarios": arquivos_bkp,
            "total_redundancias_bloqueadas": total_duplicatas_bloqueadas,
            "historico_sincronizacoes": [
                {
                    "id": lb.id,
                    "tipo_operacao": lb.tipo_operacao,
                    "arquivo_backup": lb.arquivo_backup,
                    "novos_lancamentos": lb.novos_lancamentos,
                    "atualizacoes_status": lb.atualizacoes_status,
                    "duplicatas_bloqueadas": lb.duplicatas_bloqueadas,
                    "detalhes": lb.detalhes,
                    "data_hora": lb.created_at.strftime("%d/%m/%Y %H:%M:%S")
                }
                for lb in logs_bkp
            ]
        }
    }


@router.post("/lancamentos", summary="Cadastrar novo lançamento contábil com bloqueio estrito anti-redundância")
def criar_lancamento_contabil(
    dados: NovoLancamentoContabilInput,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cria um lançamento no Livro Diário aplicando a regra estrita:
    Se tiver o mesmo Valor + Fornecedor + Data de Vencimento na mesma Fazenda, descarta automaticamente!
    Caso o viveiro não seja informado, mantém como 'Geral da Fazenda' para decisão do usuário.
    """
    chave = calcular_chave_contabil_estrita(
        fazenda.id, dados.fornecedor_cliente, dados.data_vencimento, dados.valor_rs
    )

    existente = db.query(LancamentoContabil).filter(
        LancamentoContabil.chave_dedup == chave
    ).first()

    if existente:
        # Registra no log de redundâncias bloqueadas
        db.add(LogBackupContabil(
            fazenda_id=fazenda.id,
            tipo_operacao="BLOQUEIO_REDUNDANCIA_AUTOMATICO",
            arquivo_backup="Monitor Anti-Duplicidade",
            novos_lancamentos=0,
            atualizacoes_status=0,
            duplicatas_bloqueadas=1,
            detalhes=f"Descartado automaticamente: {dados.fornecedor_cliente} - R$ {dados.valor_rs:.2f} (venc. {dados.data_vencimento})."
        ))
        db.commit()
        return {
            "status": "bloqueado_redundancia",
            "duplicata_descartada": True,
            "mensagem": (
                f"Informação redundante bloqueada automaticamente: já consta lançamento para "
                f"'{dados.fornecedor_cliente}' no valor de R$ {dados.valor_rs:.2f} com vencimento em {dados.data_vencimento}."
            )
        }

    partes = dados.nome_conta.split(" - ", 1)
    cod_conta = partes[0].strip() if len(partes) > 1 else "3.1.01"
    grupo = mapear_grupo_contabil(cod_conta)
    centro_custo = dados.centro_custo_viveiro.strip() if dados.centro_custo_viveiro else "Geral da Fazenda"

    novo = LancamentoContabil(
        fazenda_id=fazenda.id,
        data_competencia=dados.data_competencia,
        data_vencimento=dados.data_vencimento,
        data_liquidacao=dados.data_liquidacao or (dados.data_vencimento if dados.status_pagamento == "PAGO" else None),
        tipo_movimento=dados.tipo_movimento.upper(),
        codigo_conta=cod_conta,
        nome_conta=dados.nome_conta,
        grupo_contabil=grupo,
        descricao=dados.descricao,
        fornecedor_cliente=dados.fornecedor_cliente.strip(),
        valor_rs=dados.valor_rs,
        status_pagamento=dados.status_pagamento.upper(),
        forma_pagamento=dados.forma_pagamento,
        centro_custo_viveiro=centro_custo,
        arquivo_nota=dados.arquivo_nota,
        origem="MANUAL_ERP",
        chave_dedup=chave
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "status": "sucesso",
        "duplicata_descartada": False,
        "id": novo.id,
        "centro_custo_viveiro": novo.centro_custo_viveiro,
        "mensagem": "Lançamento contábil registrado com sucesso."
    }


@router.patch("/lancamentos/{lancamento_id}/alocar-viveiro", summary="Direcionar custo/receita para um viveiro específico ou Geral da Fazenda")
def alocar_viveiro_lancamento(
    lancamento_id: int,
    payload: AtualizarViveiroInput,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Permite ao usuário decidir manualmente a qual viveiro pertence um custo que não veio explícito na nota."""
    lanc = db.query(LancamentoContabil).filter(
        LancamentoContabil.id == lancamento_id,
        LancamentoContabil.fazenda_id == fazenda.id
    ).first()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento contábil não encontrado.")

    lanc.centro_custo_viveiro = payload.centro_custo_viveiro.strip() or "Geral da Fazenda"
    db.commit()
    return {
        "status": "sucesso",
        "id": lanc.id,
        "centro_custo_viveiro": lanc.centro_custo_viveiro,
        "mensagem": f"Lançamento direcionado para '{lanc.centro_custo_viveiro}'."
    }


@router.patch("/lancamentos/{lancamento_id}/status", summary="Alternar status entre PAGO e PENDENTE")
def atualizar_status_lancamento(
    lancamento_id: int,
    payload: AtualizarStatusInput,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dá baixa em 1 clique em uma conta pendente ou reabre para pendente."""
    lanc = db.query(LancamentoContabil).filter(
        LancamentoContabil.id == lancamento_id,
        LancamentoContabil.fazenda_id == fazenda.id
    ).first()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento contábil não encontrado.")

    novo_st = payload.status_pagamento.strip().upper()
    lanc.status_pagamento = "PAGO" if novo_st == "PAGO" else "PENDENTE"
    lanc.data_liquidacao = payload.data_liquidacao or (date.today() if lanc.status_pagamento == "PAGO" else None)
    db.commit()
    return {
        "status": "sucesso",
        "id": lanc.id,
        "status_pagamento": lanc.status_pagamento,
        "data_liquidacao": lanc.data_liquidacao.isoformat() if lanc.data_liquidacao else None
    }


@router.post("/sincronizar-planilha", summary="Sincronizar planilha oficial Registro_de_Custos_e_Contas.xlsx com backup diário")
def sincronizar_planilha_contabil_drive(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Lê de forma gradativa a planilha Registro_de_Custos_e_Contas.xlsx, bloqueia duplicatas e gera backup diário."""
    if not PLANILHA_CONTABIL_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Planilha não encontrada em {PLANILHA_CONTABIL_PATH}")

    res = IngestorService.processar_planilha_contabil(
        db=db,
        arquivo_ou_caminho=PLANILHA_CONTABIL_PATH,
        fazenda_id=fazenda.id,
        fazenda_codigo=fazenda.codigo
    )
    return {"status": "sucesso", "resultado": res}


@router.post("/upload-planilha", summary="Upload manual da planilha contábil (.xlsx)")
async def upload_planilha_contabil(
    file: UploadFile = File(...),
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Recebe arquivo .xlsx via navegador e processa com bloqueio estrito anti-duplicidade."""
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Envie um arquivo Excel (.xlsx).")

    conteudo = await file.read()
    res = IngestorService.processar_planilha_contabil(
        db=db,
        arquivo_ou_caminho=conteudo,
        fazenda_id=fazenda.id,
        fazenda_codigo=fazenda.codigo
    )
    return {"status": "sucesso", "arquivo": file.filename, "resultado": res}


@router.post("/backup-agora", summary="Realizar backup imediato da planilha contábil em 03_BACKUPS_DIARIOS")
def criar_backup_contabil_agora(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Salva uma cópia imediata da planilha Registro_de_Custos_e_Contas.xlsx na pasta 03_BACKUPS_DIARIOS."""
    import shutil as _shutil

    if not PLANILHA_CONTABIL_PATH.exists():
        raise HTTPException(status_code=404, detail="Planilha oficial não encontrada para backup.")

    dir_bkp = DIRETORIO_CONTABIL / "03_BACKUPS_DIARIOS"
    dir_bkp.mkdir(parents=True, exist_ok=True)
    nome_bkp = f"Registro_de_Custos_e_Contas_BACKUP_{datetime.now().strftime('%Y-%m-%d_%Hh%M')}.xlsx"
    destino = dir_bkp / nome_bkp
    _shutil.copy2(PLANILHA_CONTABIL_PATH, destino)

    log = LogBackupContabil(
        fazenda_id=fazenda.id,
        tipo_operacao="BACKUP_DIARIO_MANUAL",
        arquivo_backup=nome_bkp,
        novos_lancamentos=0,
        atualizacoes_status=0,
        duplicatas_bloqueadas=0,
        detalhes="Backup preventivo acionado pelo usuário no ERP."
    )
    db.add(log)
    db.commit()

    return {
        "status": "sucesso",
        "arquivo_backup": nome_bkp,
        "caminho": str(destino),
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
