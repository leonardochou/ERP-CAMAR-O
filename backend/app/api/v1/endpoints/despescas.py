"""Endpoints REST para despescas e faturamento comercial de camarão com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.despesca import DespescaVenda
from app.models.ciclo import CicloCultivo
from app.schemas.despesca import DespescaVendaCreate, DespescaVendaUpdate, DespescaVendaResponse

router = APIRouter()


@router.get("/", response_model=List[DespescaVendaResponse], summary="Listar vendas e despescas")
def listar_despescas(
    ciclo_id: Optional[int] = None,
    status_pagamento: Optional[str] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista as despescas parciais e totais com status comercial na fazenda ativa."""
    query = db.query(DespescaVenda).filter(DespescaVenda.fazenda_id == fazenda.id)
    if ciclo_id is not None:
        query = query.filter(DespescaVenda.ciclo_id == ciclo_id)
    if status_pagamento is not None:
        query = query.filter(DespescaVenda.status_pagamento == status_pagamento)
    return query.order_by(DespescaVenda.data.desc()).all()


@router.post("/", response_model=DespescaVendaResponse, status_code=status.HTTP_201_CREATED, summary="Registrar nova venda de despesca")
def registrar_despesca(
    venda_in: DespescaVendaCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Cadastra a venda/despesca calculando o faturamento bruto exato."""
    alvo_fazenda_id = venda_in.fazenda_id or fazenda.id

    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == venda_in.ciclo_id,
        CicloCultivo.fazenda_id == alvo_fazenda_id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo com ID {venda_in.ciclo_id} não encontrado nesta fazenda."
        )

    faturamento = round(venda_in.camarao_colhido_kg * venda_in.preco_kg_rs, 2)
    dados = venda_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["faturamento_bruto_rs"] = faturamento

    nova_venda = DespescaVenda(**dados)
    db.add(nova_venda)
    db.commit()
    db.refresh(nova_venda)
    return nova_venda


@router.put("/{id}", response_model=DespescaVendaResponse, summary="Atualizar status de pagamento da venda")
def atualizar_status_venda(
    id: int,
    venda_in: DespescaVendaUpdate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Atualiza status de recebimento, data e forma de pagamento na fazenda ativa."""
    venda = db.query(DespescaVenda).filter(
        DespescaVenda.id == id,
        DespescaVenda.fazenda_id == fazenda.id
    ).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venda com ID {id} não encontrada."
        )

    update_data = venda_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venda, field, value)

    db.commit()
    db.refresh(venda)
    return venda
