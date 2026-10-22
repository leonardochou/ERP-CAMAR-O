"""Endpoints REST para gestão de Fazendas (Multi-Tenant)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.fazenda import Fazenda
from app.schemas.fazenda import FazendaCreate, FazendaUpdate, FazendaResponse

router = APIRouter()


@router.get("/", response_model=List[FazendaResponse], summary="Listar todas as fazendas cadastradas")
def listar_fazendas(db: Session = Depends(get_db)):
    """Retorna as propriedades rurais registradas no ERP (ex: Fazenda Arrendada, Fazenda Hakka)."""
    return db.query(Fazenda).order_by(Fazenda.created_at.asc()).all()


@router.get("/{id_ou_codigo}", response_model=FazendaResponse, summary="Obter dados de uma fazenda")
def obter_fazenda(id_ou_codigo: str, db: Session = Depends(get_db)):
    """Busca uma fazenda por seu UUID ou código identificador."""
    fazenda = db.query(Fazenda).filter(
        (Fazenda.id == id_ou_codigo) | (Fazenda.codigo == id_ou_codigo)
    ).first()
    if not fazenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fazenda identificada por '{id_ou_codigo}' não encontrada."
        )
    return fazenda


@router.post("/", response_model=FazendaResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar nova fazenda")
def criar_fazenda(fazenda_in: FazendaCreate, db: Session = Depends(get_db)):
    """Cadastra uma nova propriedade rural na arquitetura Multi-Tenant."""
    existente = db.query(Fazenda).filter(Fazenda.codigo == fazenda_in.codigo).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma fazenda com o código '{fazenda_in.codigo}'."
        )

    dados = fazenda_in.model_dump(exclude_unset=True)
    nova_fazenda = Fazenda(**dados)
    db.add(nova_fazenda)
    db.commit()
    db.refresh(nova_fazenda)
    return nova_fazenda


@router.put("/{id_ou_codigo}", response_model=FazendaResponse, summary="Atualizar dados de uma fazenda")
def atualizar_fazenda(id_ou_codigo: str, fazenda_in: FazendaUpdate, db: Session = Depends(get_db)):
    """Atualiza dados cadastrais da fazenda."""
    fazenda = db.query(Fazenda).filter(
        (Fazenda.id == id_ou_codigo) | (Fazenda.codigo == id_ou_codigo)
    ).first()
    if not fazenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fazenda '{id_ou_codigo}' não encontrada."
        )

    update_data = fazenda_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fazenda, field, value)

    db.commit()
    db.refresh(fazenda)
    return fazenda
