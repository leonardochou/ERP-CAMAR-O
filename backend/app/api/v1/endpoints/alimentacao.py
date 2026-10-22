"""Endpoints REST para lançamentos diários de alimentação e sobras de bandejas com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.alimentacao import LancamentoAlimentacao
from app.models.ciclo import CicloCultivo
from app.schemas.alimentacao import LancamentoAlimentacaoCreate, LancamentoAlimentacaoResponse

router = APIRouter()


@router.get("/", response_model=List[LancamentoAlimentacaoResponse], summary="Listar lançamentos de alimentação")
def listar_alimentacoes(
    ciclo_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista a série temporal de arraçoamento de um lote na fazenda ativa."""
    query = db.query(LancamentoAlimentacao).filter(
        LancamentoAlimentacao.fazenda_id == fazenda.id,
        LancamentoAlimentacao.ciclo_id == ciclo_id
    )
    if data_inicio:
        query = query.filter(LancamentoAlimentacao.data >= data_inicio)
    if data_fim:
        query = query.filter(LancamentoAlimentacao.data <= data_fim)
    return query.order_by(LancamentoAlimentacao.data.asc()).all()


@router.post("/", response_model=LancamentoAlimentacaoResponse, status_code=status.HTTP_201_CREATED, summary="Registrar alimentação diária")
def registrar_alimentacao(
    lancamento_in: LancamentoAlimentacaoCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra tratos e sobras de um dia de cultivo, calculando total e consumo acumulado."""
    alvo_fazenda_id = lancamento_in.fazenda_id or fazenda.id

    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == lancamento_in.ciclo_id,
        CicloCultivo.fazenda_id == alvo_fazenda_id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo de cultivo com ID {lancamento_in.ciclo_id} não encontrado nesta fazenda."
        )

    existente = db.query(LancamentoAlimentacao).filter(
        LancamentoAlimentacao.ciclo_id == lancamento_in.ciclo_id,
        LancamentoAlimentacao.data == lancamento_in.data
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe lançamento de alimentação para o ciclo {lancamento_in.ciclo_id} na data {lancamento_in.data}."
        )

    total_dia = round(
        (lancamento_in.racao_manha_kg or 0.0) +
        (lancamento_in.racao_tarde_kg or 0.0) +
        (lancamento_in.racao_noite_kg or 0.0),
        2
    )

    ultimo_registro = db.query(LancamentoAlimentacao).filter(
        LancamentoAlimentacao.ciclo_id == lancamento_in.ciclo_id,
        LancamentoAlimentacao.data < lancamento_in.data
    ).order_by(desc(LancamentoAlimentacao.data)).first()

    consumo_anterior = ultimo_registro.consumo_acumulado_kg if ultimo_registro else 0.0
    consumo_acumulado = round(consumo_anterior + total_dia, 2)

    dados = lancamento_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["total_dia_kg"] = total_dia
    dados["consumo_acumulado_kg"] = consumo_acumulado

    novo_lancamento = LancamentoAlimentacao(**dados)
    db.add(novo_lancamento)
    db.commit()
    db.refresh(novo_lancamento)
    return novo_lancamento
