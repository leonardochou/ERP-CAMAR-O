"""Endpoints REST para gestão de Ciclos de Cultivo e Lotes com suporte Multi-Tenant."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.ciclo import CicloCultivo
from app.models.viveiro import Viveiro
from app.models.alimentacao import LancamentoAlimentacao
from app.schemas.ciclo import CicloCreate, CicloUpdate, CicloResponse, FechamentoSafraRequest
from app.services.zootecnia_service import ZootecniaService

router = APIRouter()


@router.get("/", response_model=List[CicloResponse], summary="Listar ciclos de cultivo da fazenda ativa")
def listar_ciclos(
    viveiro_id: Optional[int] = None,
    status_filtro: Optional[str] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista os ciclos de cultivo da fazenda com opções de filtro por viveiro e status."""
    query = db.query(CicloCultivo).filter(CicloCultivo.fazenda_id == fazenda.id)
    if viveiro_id is not None:
        query = query.filter(CicloCultivo.viveiro_id == viveiro_id)
    if status_filtro is not None:
        query = query.filter(CicloCultivo.status == status_filtro)
    return query.order_by(CicloCultivo.data_povoamento.desc()).all()


@router.get("/{id}", response_model=CicloResponse, summary="Obter dados de um ciclo por ID")
def obter_ciclo(
    id: int,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna os dados detalhados de um ciclo de cultivo."""
    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == id,
        CicloCultivo.fazenda_id == fazenda.id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo com ID {id} não encontrado na fazenda ativa."
        )
    return ciclo


@router.post("/", response_model=CicloResponse, status_code=status.HTTP_201_CREATED, summary="Iniciar novo ciclo de cultivo")
def criar_ciclo(
    ciclo_in: CicloCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Inicia um novo ciclo de cultivo em um viveiro específico, calculando a densidade inicial."""
    alvo_fazenda_id = ciclo_in.fazenda_id or fazenda.id

    viveiro = db.query(Viveiro).filter(
        Viveiro.id == ciclo_in.viveiro_id,
        Viveiro.fazenda_id == alvo_fazenda_id
    ).first()
    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro com ID {ciclo_in.viveiro_id} não encontrado nesta fazenda."
        )

    existente = db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == alvo_fazenda_id,
        CicloCultivo.numero_lote == ciclo_in.numero_lote
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um ciclo cadastrado com o número de lote '{ciclo_in.numero_lote}' nesta fazenda."
        )

    densidade = round(ciclo_in.pls_estocadas / viveiro.area_m2, 2) if viveiro.area_m2 > 0 else 0.0

    dados = ciclo_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["densidade_pl_m2"] = densidade

    novo_ciclo = CicloCultivo(**dados)
    db.add(novo_ciclo)
    db.commit()
    db.refresh(novo_ciclo)
    return novo_ciclo


@router.post("/{id}/fechar", response_model=CicloResponse, summary="Encerrar safra (fechamento de despesca final)")
def fechar_safra(
    id: int,
    fechamento_in: FechamentoSafraRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Realiza o fechamento definitivo do lote, calculando sobrevivência real, FCA final e produtividade."""
    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == id,
        CicloCultivo.fazenda_id == fazenda.id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo com ID {id} não encontrado."
        )

    viveiro = db.query(Viveiro).filter(Viveiro.id == ciclo.viveiro_id).first()
    area_ha = viveiro.area_ha if viveiro else 1.0

    racao_total = db.query(func.sum(LancamentoAlimentacao.total_dia_kg)).filter(
        LancamentoAlimentacao.ciclo_id == ciclo.id
    ).scalar() or 0.0

    sobrevivencia, fca_final, produtividade = ZootecniaService.calcular_fechamento_safra(
        camarao_colhido_kg=fechamento_in.camarao_colhido_kg,
        peso_final_g=fechamento_in.peso_final_g,
        pls_estocadas=ciclo.pls_estocadas,
        racao_total_ciclo_kg=racao_total,
        area_ha=area_ha
    )

    ciclo.status = "DESPESCADO"
    ciclo.data_despesca = fechamento_in.data_despesca
    ciclo.camarao_colhido_kg = fechamento_in.camarao_colhido_kg
    ciclo.peso_final_g = fechamento_in.peso_final_g
    ciclo.sobrevivencia_real_pct = sobrevivencia
    ciclo.fca_real_final = fca_final
    ciclo.produtividade_kg_ha = produtividade
    if fechamento_in.faturamento_total_rs is not None:
        ciclo.faturamento_total_rs = fechamento_in.faturamento_total_rs
    if fechamento_in.observacoes:
        ciclo.observacoes = (ciclo.observacoes or "") + " | " + fechamento_in.observacoes

    db.commit()
    db.refresh(ciclo)
    return ciclo
