"""Endpoints REST para gestão de Ciclos de Cultivo e Lotes com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.ciclo import CicloCultivo
from app.models.viveiro import Viveiro
from app.models.alimentacao import LancamentoAlimentacao
from app.models.despesca import DespescaVenda
from app.schemas.ciclo import (
    CicloCreate,
    CicloIniciarRequest,
    CicloUpdate,
    CicloResponse,
    DespescaParcialRequest,
    FechamentoSafraRequest,
    EncerramentoCicloRequest,
)
from app.services.zootecnia_service import ZootecniaService

router = APIRouter()


@router.get("/ativos", response_model=List[CicloResponse], summary="Listar ciclos ativos em cultivo na fazenda")
def listar_ciclos_ativos(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna todos os lotes que estão atualmente na água (em cultivo ativo ou com despesca parcial)."""
    return db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == fazenda.id,
        CicloCultivo.status.in_(["EM CULTIVO ATIVO", "DESPESCA_PARCIAL", "ATIVO"])
    ).order_by(CicloCultivo.data_povoamento.asc()).all()


@router.get("/historico", response_model=List[CicloResponse], summary="Listar histórico permanente de ciclos concluídos")
def listar_historico_ciclos(
    ano_safra: Optional[int] = None,
    viveiro_id: Optional[int] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna os ciclos finalizados e arquivados para relatórios executivos e auditoria de safras."""
    query = db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == fazenda.id,
        CicloCultivo.status.in_(["ENCERRADO", "DESPESCADO", "CONCLUIDA"])
    )
    if ano_safra is not None:
        query = query.filter(CicloCultivo.ano_safra == ano_safra)
    if viveiro_id is not None:
        query = query.filter(CicloCultivo.viveiro_id == viveiro_id)
    return query.order_by(CicloCultivo.data_despesca.desc()).all()


@router.get("/", response_model=List[CicloResponse], summary="Listar ciclos de cultivo da fazenda ativa")
def listar_ciclos(
    viveiro_id: Optional[int] = None,
    status_filtro: Optional[str] = None,
    ano_safra: Optional[int] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista os ciclos de cultivo da fazenda com opções de filtro por viveiro, status e ano-safra."""
    query = db.query(CicloCultivo).filter(CicloCultivo.fazenda_id == fazenda.id)
    if viveiro_id is not None:
        query = query.filter(CicloCultivo.viveiro_id == viveiro_id)
    if status_filtro is not None:
        query = query.filter(CicloCultivo.status == status_filtro)
    if ano_safra is not None:
        query = query.filter(CicloCultivo.ano_safra == ano_safra)
    return query.order_by(CicloCultivo.data_povoamento.desc()).all()


@router.post("/iniciar", response_model=CicloResponse, status_code=status.HTTP_201_CREATED, summary="Iniciar novo ciclo com numeração sequencial automática")
def iniciar_ciclo_sequencial(
    iniciar_in: CicloIniciarRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Inicia um novo ciclo em um viveiro vazio, gerando nome sequencial oficial (ex: V-01 • Ciclo 2026.1)."""
    viveiro = db.query(Viveiro).filter(
        Viveiro.id == iniciar_in.viveiro_id,
        Viveiro.fazenda_id == fazenda.id
    ).first()
    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro com ID {iniciar_in.viveiro_id} não encontrado nesta fazenda."
        )

    ano = iniciar_in.ano_safra or iniciar_in.data_povoamento.year

    # Buscar maior número sequencial para o viveiro no ano-safra
    maior_seq = db.query(func.max(CicloCultivo.numero_sequencial)).filter(
        CicloCultivo.fazenda_id == fazenda.id,
        CicloCultivo.viveiro_id == viveiro.id,
        CicloCultivo.ano_safra == ano
    ).scalar() or 0

    prox_seq = int(maior_seq) + 1
    codigo_oficial = f"{viveiro.codigo} • Ciclo {ano}.{prox_seq}"

    densidade = round(iniciar_in.pls_estocadas / viveiro.area_m2, 2) if viveiro.area_m2 > 0 else 0.0

    novo_ciclo = CicloCultivo(
        fazenda_id=fazenda.id,
        viveiro_id=viveiro.id,
        numero_lote=codigo_oficial,
        codigo_ciclo=codigo_oficial,
        ano_safra=ano,
        numero_sequencial=prox_seq,
        data_povoamento=iniciar_in.data_povoamento,
        pls_estocadas=iniciar_in.pls_estocadas,
        densidade_pl_m2=densidade,
        laboratorio=iniciar_in.laboratorio,
        peso_inicial_g=iniciar_in.peso_inicial_g,
        status="EM CULTIVO ATIVO",
        observacoes=iniciar_in.observacoes
    )
    db.add(novo_ciclo)
    db.commit()
    db.refresh(novo_ciclo)
    return novo_ciclo


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


@router.post("/", response_model=CicloResponse, status_code=status.HTTP_201_CREATED, summary="Iniciar novo ciclo de cultivo manual")
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

    lote_nome = ciclo_in.numero_lote or f"{viveiro.codigo} • Ciclo {ciclo_in.data_povoamento.year}.1"

    existente = db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == alvo_fazenda_id,
        CicloCultivo.numero_lote == lote_nome
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um ciclo cadastrado com o número de lote '{lote_nome}' nesta fazenda."
        )

    densidade = round(ciclo_in.pls_estocadas / viveiro.area_m2, 2) if viveiro.area_m2 > 0 else 0.0

    dados = ciclo_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["numero_lote"] = lote_nome
    if not dados.get("codigo_ciclo"):
        dados["codigo_ciclo"] = lote_nome
    if not dados.get("ano_safra"):
        dados["ano_safra"] = ciclo_in.data_povoamento.year
    dados["densidade_pl_m2"] = densidade

    novo_ciclo = CicloCultivo(**dados)
    db.add(novo_ciclo)
    db.commit()
    db.refresh(novo_ciclo)
    return novo_ciclo


@router.post("/{id}/despesca-parcial", response_model=CicloResponse, summary="Registrar despesca parcial (desbaste/raleio)")
def registrar_despesca_parcial(
    id: int,
    despesca_in: DespescaParcialRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra uma despesca parcial (desbaste) sem encerrar o lote, abatendo biomassa e mantendo o ciclo ativo."""
    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == id,
        CicloCultivo.fazenda_id == fazenda.id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo com ID {id} não encontrado."
        )

    faturamento = round(despesca_in.camarao_colhido_kg * (despesca_in.preco_kg_rs or 0.0), 2)
    venda = DespescaVenda(
        fazenda_id=fazenda.id,
        ciclo_id=ciclo.id,
        data=despesca_in.data,
        tipo_despesca="DESBASTE",
        gramatura_media_g=despesca_in.gramatura_media_g,
        camarao_colhido_kg=despesca_in.camarao_colhido_kg,
        comprador=despesca_in.comprador or "Mercado Local",
        preco_kg_rs=despesca_in.preco_kg_rs or 0.0,
        faturamento_bruto_rs=faturamento,
        observacoes=despesca_in.observacoes
    )
    db.add(venda)

    ciclo.despescas_parciais_kg = round((ciclo.despescas_parciais_kg or 0.0) + despesca_in.camarao_colhido_kg, 2)
    ciclo.status = "DESPESCA_PARCIAL"
    if despesca_in.observacoes:
        ciclo.observacoes = (ciclo.observacoes or "") + " | Desbaste: " + despesca_in.observacoes

    db.commit()
    db.refresh(ciclo)
    return ciclo


def _executar_fechamento_ciclo(
    id: int,
    fechamento_in: FechamentoSafraRequest,
    fazenda: Fazenda,
    db: Session,
    novo_status: str = "ENCERRADO"
) -> CicloCultivo:
    """Função interna consolidada de fechamento executivo de safra."""
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
    if racao_total == 0.0 and ciclo.racao_total_kg:
        racao_total = ciclo.racao_total_kg

    biomassa_total_colhida = round((ciclo.despescas_parciais_kg or 0.0) + fechamento_in.camarao_colhido_kg, 2)

    sobrevivencia, fca_final, produtividade = ZootecniaService.calcular_fechamento_safra(
        camarao_colhido_kg=biomassa_total_colhida,
        peso_final_g=fechamento_in.peso_final_g,
        pls_estocadas=ciclo.pls_estocadas,
        racao_total_ciclo_kg=racao_total,
        area_ha=area_ha
    )

    preco_unit = fechamento_in.preco_kg_rs or 22.0
    fat_calc = round(fechamento_in.camarao_colhido_kg * preco_unit, 2)
    faturamento_final = fechamento_in.faturamento_total_rs if fechamento_in.faturamento_total_rs is not None else fat_calc

    venda_final = DespescaVenda(
        fazenda_id=fazenda.id,
        ciclo_id=ciclo.id,
        data=fechamento_in.data_despesca,
        tipo_despesca="TOTAL",
        gramatura_media_g=fechamento_in.peso_final_g,
        camarao_colhido_kg=fechamento_in.camarao_colhido_kg,
        comprador=fechamento_in.comprador or "Mercado Local",
        preco_kg_rs=preco_unit,
        faturamento_bruto_rs=faturamento_final,
        observacoes=fechamento_in.observacoes
    )
    db.add(venda_final)

    fat_desbastes = db.query(func.sum(DespescaVenda.faturamento_bruto_rs)).filter(
        DespescaVenda.ciclo_id == ciclo.id,
        DespescaVenda.tipo_despesca == "DESBASTE"
    ).scalar() or 0.0
    fat_total_ciclo = round(fat_desbastes + faturamento_final, 2)

    ciclo.status = novo_status
    ciclo.data_despesca = fechamento_in.data_despesca
    ciclo.camarao_colhido_kg = biomassa_total_colhida
    ciclo.racao_total_kg = racao_total
    ciclo.peso_final_g = fechamento_in.peso_final_g
    ciclo.sobrevivencia_real_pct = sobrevivencia
    ciclo.fca_real_final = fca_final
    ciclo.produtividade_kg_ha = produtividade
    ciclo.faturamento_total_rs = fat_total_ciclo
    if fechamento_in.observacoes:
        ciclo.observacoes = (ciclo.observacoes or "") + " | " + fechamento_in.observacoes

    db.commit()
    db.refresh(ciclo)
    return ciclo


@router.post("/{id}/encerrar", response_model=CicloResponse, summary="Encerrar ciclo de cultivo definitivamente")
def encerrar_ciclo(
    id: int,
    fechamento_in: FechamentoSafraRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Realiza o fechamento definitivo do ciclo, arquivando no histórico permanente com status ENCERRADO."""
    return _executar_fechamento_ciclo(id, fechamento_in, fazenda, db, novo_status="ENCERRADO")


@router.post("/{id}/fechar", response_model=CicloResponse, summary="Encerrar safra (fechamento de despesca final)")
def fechar_safra(
    id: int,
    fechamento_in: FechamentoSafraRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Realiza o fechamento definitivo da safra com status DESPESCADO para compatibilidade de rotinas legadas."""
    return _executar_fechamento_ciclo(id, fechamento_in, fazenda, db, novo_status="DESPESCADO")
