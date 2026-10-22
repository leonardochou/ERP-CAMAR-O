"""Endpoints REST para a Central de Auditoria Ativa de Dados com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.auditoria import AuditoriaPendencia
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.schemas.auditoria import AuditoriaPendenciaResponse, AuditoriaResolucaoRequest

router = APIRouter()


@router.get("/pendencias", response_model=List[AuditoriaPendenciaResponse], summary="Listar pendências da auditoria")
def listar_pendencias(
    resolvido: Optional[bool] = False,
    severidade: Optional[str] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista as inconsistências, duplicatas e anomalias retidas para auditoria na fazenda ativa."""
    query = db.query(AuditoriaPendencia).filter(AuditoriaPendencia.fazenda_id == fazenda.id)
    if resolvido is not None:
        query = query.filter(AuditoriaPendencia.resolvido == resolvido)
    if severidade:
        query = query.filter(AuditoriaPendencia.severidade == severidade.upper())
    return query.order_by(AuditoriaPendencia.created_at.desc()).all()


@router.post("/{id}/resolver", response_model=AuditoriaPendenciaResponse, summary="Resolver pendência em 1 clique")
def resolver_pendencia(
    id: int,
    resolucao_in: AuditoriaResolucaoRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Executa a ação de resolução (MANTER_NOVO, MANTER_ANTIGO, SOMAR_TURNOS, DESCARTAR) e atualiza o status."""
    pendencia = db.query(AuditoriaPendencia).filter(
        AuditoriaPendencia.id == id,
        AuditoriaPendencia.fazenda_id == fazenda.id
    ).first()
    if not pendencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pendência com ID {id} não encontrada nesta fazenda."
        )

    acao = resolucao_in.acao.upper()
    if acao not in ["MANTER_NOVO", "MANTER_ANTIGO", "SOMAR_TURNOS", "DESCARTAR"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ação de resolução inválida '{resolucao_in.acao}'. Opções permitidas: MANTER_NOVO, MANTER_ANTIGO, SOMAR_TURNOS, DESCARTAR."
        )

    pendencia.resolvido = True
    pendencia.acao_resolucao = acao
    pendencia.resolvido_em = datetime.utcnow()

    db.commit()
    db.refresh(pendencia)
    return pendencia


@router.post("/verificar-dias-esquecidos", response_model=List[AuditoriaPendenciaResponse], summary="Detectar viveiros ativos sem dados há > 24h")
def verificar_dias_esquecidos(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Varre todos os viveiros em cultivo ativo da fazenda e cria pendências caso não haja lançamentos nas últimas 24h."""
    ciclos_ativos = db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == fazenda.id,
        CicloCultivo.status == "EM CULTIVO ATIVO"
    ).all()
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    novas_pendencias = []

    for ciclo in ciclos_ativos:
        viveiro = db.query(Viveiro).filter(Viveiro.id == ciclo.viveiro_id).first()
        viveiro_cod = viveiro.codigo if viveiro else f"ID-{ciclo.viveiro_id}"

        ultimo_trato = db.query(LancamentoAlimentacao).filter(
            LancamentoAlimentacao.ciclo_id == ciclo.id
        ).order_by(desc(LancamentoAlimentacao.data)).first()

        falta_trato = (not ultimo_trato) or (ultimo_trato.data < ontem)

        if falta_trato:
            ja_existe = db.query(AuditoriaPendencia).filter(
                AuditoriaPendencia.fazenda_id == fazenda.id,
                AuditoriaPendencia.viveiro_codigo == viveiro_cod,
                AuditoriaPendencia.tipo_anomalia == "DIA_ESQUECIDO",
                AuditoriaPendencia.resolvido == False
            ).first()

            if not ja_existe:
                pendencia = AuditoriaPendencia(
                    fazenda_id=fazenda.id,
                    origem="MANUAL",
                    entidade="ALIMENTACAO",
                    viveiro_codigo=viveiro_cod,
                    data_evento=hoje,
                    tipo_anomalia="DIA_ESQUECIDO",
                    severidade="ATENCAO",
                    mensagem=f"Viveiro ativo {viveiro_cod} sem lançamento de trato nas últimas 24h. Último registro: {ultimo_trato.data if ultimo_trato else 'Nenhum'}."
                )
                db.add(pendencia)
                novas_pendencias.append(pendencia)

    if novas_pendencias:
        db.commit()
        for p in novas_pendencias:
            db.refresh(p)

    return novas_pendencias
