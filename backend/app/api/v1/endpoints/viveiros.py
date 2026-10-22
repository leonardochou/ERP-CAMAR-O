"""Endpoints REST para gestão de Viveiros (Tanques) com suporte Multi-Tenant e Calibração de Metragem."""
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.schemas.viveiro import (
    ViveiroCreate,
    ViveiroUpdate,
    ViveiroResponse,
    ViveiroMapaItem,
    ViveiroAjusteMetragemRequest
)

router = APIRouter()


@router.get("/", response_model=List[ViveiroResponse], summary="Listar viveiros da fazenda ativa")
def listar_viveiros(
    ativo: Optional[bool] = None,
    setor: Optional[str] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna o inventário dos tanques pertencentes à fazenda ativa no contexto."""
    query = db.query(Viveiro).filter(Viveiro.fazenda_id == fazenda.id)
    if ativo is not None:
        query = query.filter(Viveiro.ativo == ativo)
    if setor is not None:
        query = query.filter(Viveiro.setor == setor)
    return query.order_by(Viveiro.codigo).all()


@router.get("/mapa", response_model=List[ViveiroMapaItem], summary="Status consolidado para o Mapa 2D com numeração do pai e metragens")
def mapa_viveiros(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna o estado operacional, nomeação do pai (1 a 10) e dupla metragem (Satélite vs Ajustada) para o Mapa 2D."""
    viveiros = db.query(Viveiro).filter(Viveiro.fazenda_id == fazenda.id).order_by(Viveiro.codigo).all()
    resultado = []

    for v in viveiros:
        ciclo_ativo = db.query(CicloCultivo).filter(
            CicloCultivo.viveiro_id == v.id,
            CicloCultivo.status == "EM CULTIVO ATIVO"
        ).first()

        ultima_agua = db.query(MonitoramentoAgua).filter(
            MonitoramentoAgua.viveiro_id == v.id
        ).order_by(desc(MonitoramentoAgua.data)).first()

        status_cor = "VAZIO" if not ciclo_ativo else "OTIMO"
        doc_atual = None
        ultimo_o2 = None
        ultimo_peso = None
        biomassa = None

        if ultima_agua:
            ultimo_o2 = ultima_agua.o2_manha if ultima_agua.o2_manha is not None else ultima_agua.o2_noite
            if ciclo_ativo:
                status_cor = ultima_agua.status_tanque

        if ciclo_ativo:
            ultima_biometria = db.query(Biometria).filter(
                Biometria.ciclo_id == ciclo_ativo.id
            ).order_by(desc(Biometria.data)).first()

            if ultima_biometria:
                doc_atual = ultima_biometria.doc
                ultimo_peso = ultima_biometria.peso_medio_g
                biomassa = ultima_biometria.biomassa_estimada_kg

        resultado.append(ViveiroMapaItem(
            id=v.id,
            fazenda_id=v.fazenda_id,
            codigo=v.codigo,
            nome_operacional=v.nome_operacional,
            nome_pai=v.nome_pai,
            numero_pai=v.numero_pai,
            setor=v.setor,
            area_m2=v.area_m2,
            area_ha=v.area_ha,
            area_satelite_m2=v.area_satelite_m2,
            area_ajustada_m2=v.area_ajustada_m2,
            volume_m3=v.volume_m3,
            tipo_uso=v.tipo_uso,
            status_cor=status_cor,
            ciclo_ativo_id=ciclo_ativo.id if ciclo_ativo else None,
            numero_lote=ciclo_ativo.numero_lote if ciclo_ativo else None,
            doc_atual=doc_atual,
            ultimo_o2=ultimo_o2,
            ultimo_peso_g=ultimo_peso,
            biomassa_estimada_kg=biomassa
        ))

    return resultado


@router.get("/{codigo}", response_model=ViveiroResponse, summary="Obter dados de um viveiro por código ou ID")
def obter_viveiro(
    codigo: str,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna os dados de um tanque na fazenda ativa."""
    query = db.query(Viveiro).filter(Viveiro.fazenda_id == fazenda.id)
    if codigo.isdigit():
        viveiro = query.filter(Viveiro.id == int(codigo)).first()
    else:
        viveiro = query.filter(Viveiro.codigo == codigo.upper()).first()

    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro '{codigo}' não encontrado na fazenda '{fazenda.nome}'."
        )
    return viveiro


@router.post("/", response_model=ViveiroResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo viveiro")
def criar_viveiro(
    viveiro_in: ViveiroCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Cadastra um novo viveiro na fazenda ativa."""
    alvo_fazenda_id = viveiro_in.fazenda_id or fazenda.id

    existente = db.query(Viveiro).filter(
        Viveiro.fazenda_id == alvo_fazenda_id,
        Viveiro.codigo == viveiro_in.codigo.upper()
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um viveiro cadastrado com o código '{viveiro_in.codigo}' nesta fazenda."
        )

    dados = viveiro_in.model_dump()
    dados["codigo"] = dados["codigo"].upper()
    dados["fazenda_id"] = alvo_fazenda_id

    novo_viveiro = Viveiro(**dados)
    db.add(novo_viveiro)
    db.commit()
    db.refresh(novo_viveiro)
    return novo_viveiro


@router.patch("/{identificador}/metragem", response_model=ViveiroResponse, summary="Calibrar e ajustar metragem do viveiro (Satélite vs Campo)")
def ajustar_metragem_viveiro(
    identificador: str,
    ajuste_in: ViveiroAjusteMetragemRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Calibra a metragem de campo do viveiro, recalculando automaticamente hectares e volume útil de água."""
    query = db.query(Viveiro).filter(Viveiro.fazenda_id == fazenda.id)
    if identificador.isdigit():
        viveiro = query.filter(Viveiro.id == int(identificador)).first()
    else:
        viveiro = query.filter(Viveiro.codigo == identificador.upper()).first()

    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro '{identificador}' não encontrado na fazenda '{fazenda.nome}'."
        )

    if ajuste_in.area_ajustada_m2 <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A área ajustada deve ser estritamente maior que zero."
        )

    profundidade = ajuste_in.profundidade_media_m or viveiro.profundidade_media_m or 1.20
    nova_area_m2 = round(ajuste_in.area_ajustada_m2, 2)
    nova_area_ha = round(nova_area_m2 / 10000.0, 4)
    novo_volume_m3 = round(nova_area_m2 * profundidade, 2)

    viveiro.area_ajustada_m2 = nova_area_m2
    viveiro.area_m2 = nova_area_m2
    viveiro.area_ha = nova_area_ha
    viveiro.profundidade_media_m = profundidade
    viveiro.volume_m3 = novo_volume_m3
    viveiro.origem_metragem = "MEDICAO_CAMPO"
    if ajuste_in.observacoes:
        viveiro.observacoes = ajuste_in.observacoes

    db.commit()
    db.refresh(viveiro)
    return viveiro


@router.put("/{codigo}", response_model=ViveiroResponse, summary="Atualizar dados gerais de um viveiro")
def atualizar_viveiro(
    codigo: str,
    viveiro_in: ViveiroUpdate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Atualiza atributos cadastrais ou de área do viveiro na fazenda ativa."""
    viveiro = db.query(Viveiro).filter(
        Viveiro.fazenda_id == fazenda.id,
        Viveiro.codigo == codigo.upper()
    ).first()
    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro '{codigo}' não encontrado."
        )

    update_data = viveiro_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(viveiro, field, value)

    # Recalcula área e volume se área foi alterada
    if "area_m2" in update_data:
        viveiro.area_ha = round(viveiro.area_m2 / 10000.0, 4)
        viveiro.volume_m3 = round(viveiro.area_m2 * (viveiro.profundidade_media_m or 1.20), 2)

    db.commit()
    db.refresh(viveiro)
    return viveiro
