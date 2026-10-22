"""Endpoints REST para biometrias periódicas e indicadores de crescimento zootécnico com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.biometria import Biometria
from app.models.ciclo import CicloCultivo
from app.models.viveiro import Viveiro
from app.models.alimentacao import LancamentoAlimentacao
from app.models.auditoria import AuditoriaPendencia
from app.schemas.biometria import BiometriaCreate, BiometriaResponse
from app.services.zootecnia_service import ZootecniaService

router = APIRouter()


@router.get("/", response_model=List[BiometriaResponse], summary="Listar biometrias de um ciclo")
def listar_biometrias(
    ciclo_id: int,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista o histórico de biometrias amostrais e crescimento do ciclo na fazenda ativa."""
    return db.query(Biometria).filter(
        Biometria.fazenda_id == fazenda.id,
        Biometria.ciclo_id == ciclo_id
    ).order_by(Biometria.data.asc()).all()


@router.post("/", response_model=BiometriaResponse, status_code=status.HTTP_201_CREATED, summary="Registrar biometria amostral")
def registrar_biometria(
    biometria_in: BiometriaCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra pesagem amostral, calculando GMD, biomassa e FCA parcial com exatidão."""
    alvo_fazenda_id = biometria_in.fazenda_id or fazenda.id

    ciclo = db.query(CicloCultivo).filter(
        CicloCultivo.id == biometria_in.ciclo_id,
        CicloCultivo.fazenda_id == alvo_fazenda_id
    ).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo de cultivo com ID {biometria_in.ciclo_id} não encontrado nesta fazenda."
        )

    existente = db.query(Biometria).filter(
        Biometria.ciclo_id == biometria_in.ciclo_id,
        Biometria.data == biometria_in.data
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe biometria registrada para o ciclo {ciclo.numero_lote} na data {biometria_in.data}."
        )

    biometria_anterior = db.query(Biometria).filter(
        Biometria.ciclo_id == biometria_in.ciclo_id,
        Biometria.data < biometria_in.data
    ).order_by(desc(Biometria.data)).first()

    if biometria_anterior:
        dias_intervalo = (biometria_in.data - biometria_anterior.data).days
        ganho_peso = round(biometria_in.peso_medio_g - biometria_anterior.peso_medio_g, 2)
        gmd = ZootecniaService.calcular_gmd(
            peso_atual_g=biometria_in.peso_medio_g,
            peso_anterior_g=biometria_anterior.peso_medio_g,
            dias_intervalo=dias_intervalo
        )
    else:
        ganho_peso = round(biometria_in.peso_medio_g - ciclo.peso_inicial_g, 2)
        dias_intervalo = biometria_in.doc if biometria_in.doc > 0 else 1
        gmd = ZootecniaService.calcular_gmd(
            peso_atual_g=biometria_in.peso_medio_g,
            peso_anterior_g=ciclo.peso_inicial_g,
            dias_intervalo=dias_intervalo
        )

    populacao = ZootecniaService.calcular_populacao_estimada(
        pls_estocadas=ciclo.pls_estocadas,
        sobrevivencia_pct=biometria_in.sobrevivencia_estimada_pct
    )

    biomassa = ZootecniaService.calcular_biomassa_estimada_kg(
        populacao_viva=populacao,
        peso_medio_g=biometria_in.peso_medio_g
    )

    racao_acumulada = db.query(func.sum(LancamentoAlimentacao.total_dia_kg)).filter(
        LancamentoAlimentacao.ciclo_id == ciclo.id,
        LancamentoAlimentacao.data <= biometria_in.data
    ).scalar() or 0.0

    fca_parcial = ZootecniaService.calcular_fca_parcial(
        racao_acumulada_kg=racao_acumulada,
        biomassa_estimada_kg=biomassa
    )

    dados = biometria_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["ganho_peso_semanal_g"] = ganho_peso
    dados["gmd_g_dia"] = gmd
    dados["populacao_estimada"] = populacao
    dados["biomassa_estimada_kg"] = biomassa
    dados["racao_acumulada_ate_data_kg"] = racao_acumulada
    dados["fca_parcial"] = fca_parcial

    nova_biometria = Biometria(**dados)
    db.add(nova_biometria)

    if fca_parcial is not None and fca_parcial > 1.8 and biometria_in.peso_medio_g < 10.0:
        viveiro = db.query(Viveiro).filter(Viveiro.id == ciclo.viveiro_id).first()
        pendencia = AuditoriaPendencia(
            fazenda_id=alvo_fazenda_id,
            origem="MANUAL",
            entidade="BIOMETRIA",
            viveiro_codigo=viveiro.codigo if viveiro else "DESCONHECIDO",
            data_evento=biometria_in.data,
            tipo_anomalia="FCA_DESVIO",
            severidade="ATENCAO",
            mensagem=f"FCA Parcial crítico de {fca_parcial} para camarão jovem ({biometria_in.peso_medio_g}g). Suspeita de sobra excessiva ou desvio."
        )
        db.add(pendencia)

    db.commit()
    db.refresh(nova_biometria)
    return nova_biometria
