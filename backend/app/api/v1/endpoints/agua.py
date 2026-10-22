"""Endpoints REST para monitoramento físico-químico da qualidade da água com suporte Multi-Tenant."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.agua import MonitoramentoAgua
from app.models.viveiro import Viveiro
from app.models.auditoria import AuditoriaPendencia
from app.schemas.agua import MonitoramentoAguaCreate, MonitoramentoAguaResponse
from app.services.zootecnia_service import ZootecniaService

router = APIRouter()


@router.get("/", response_model=List[MonitoramentoAguaResponse], summary="Listar medições de água por viveiro")
def listar_medicoes_agua(
    viveiro_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista a série histórica de qualidade físico-química da água de um viveiro na fazenda ativa."""
    query = db.query(MonitoramentoAgua).filter(
        MonitoramentoAgua.fazenda_id == fazenda.id,
        MonitoramentoAgua.viveiro_id == viveiro_id
    )
    if data_inicio:
        query = query.filter(MonitoramentoAgua.data >= data_inicio)
    if data_fim:
        query = query.filter(MonitoramentoAgua.data <= data_fim)
    return query.order_by(MonitoramentoAgua.data.desc()).all()


@router.post("/", response_model=MonitoramentoAguaResponse, status_code=status.HTTP_201_CREATED, summary="Registrar medição de qualidade da água")
def registrar_medicao_agua(
    medicao_in: MonitoramentoAguaCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra medição física e química, calculando delta pH e avaliando anomalias zootécnicas."""
    alvo_fazenda_id = medicao_in.fazenda_id or fazenda.id

    viveiro = db.query(Viveiro).filter(
        Viveiro.id == medicao_in.viveiro_id,
        Viveiro.fazenda_id == alvo_fazenda_id
    ).first()
    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro com ID {medicao_in.viveiro_id} não encontrado nesta fazenda."
        )

    existente = db.query(MonitoramentoAgua).filter(
        MonitoramentoAgua.viveiro_id == medicao_in.viveiro_id,
        MonitoramentoAgua.data == medicao_in.data
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe registro de água para o viveiro {viveiro.codigo} na data {medicao_in.data}."
        )

    delta_ph = None
    if medicao_in.ph_manha is not None and medicao_in.ph_tarde is not None:
        delta_ph = round(medicao_in.ph_tarde - medicao_in.ph_manha, 2)

    status_tanque = ZootecniaService.classificar_status_agua(
        o2_manha=medicao_in.o2_manha,
        o2_noite=medicao_in.o2_noite,
        amonia_mg_l=medicao_in.amonia_mg_l,
        nitrito_mg_l=medicao_in.nitrito_mg_l,
        delta_ph=delta_ph,
        secchi_cm=medicao_in.transparencia_secchi_cm
    )

    dados = medicao_in.model_dump()
    dados["fazenda_id"] = alvo_fazenda_id
    dados["delta_ph"] = delta_ph
    dados["status_tanque"] = status_tanque

    nova_medicao = MonitoramentoAgua(**dados)
    db.add(nova_medicao)

    if status_tanque == "CRITICO":
        motivo = []
        if medicao_in.o2_manha is not None and medicao_in.o2_manha < 3.0:
            motivo.append(f"O2 Matutino crítico: {medicao_in.o2_manha} mg/L (<3.0)")
        if medicao_in.o2_noite is not None and medicao_in.o2_noite < 3.0:
            motivo.append(f"O2 Noturno crítico: {medicao_in.o2_noite} mg/L (<3.0)")
        if medicao_in.amonia_mg_l is not None and medicao_in.amonia_mg_l > 0.1:
            motivo.append(f"Amônia tóxica: {medicao_in.amonia_mg_l} mg/L (>0.1)")
        if medicao_in.nitrito_mg_l is not None and medicao_in.nitrito_mg_l > 0.2:
            motivo.append(f"Nitrito crítico: {medicao_in.nitrito_mg_l} mg/L (>0.2)")

        pendencia = AuditoriaPendencia(
            fazenda_id=alvo_fazenda_id,
            origem="MANUAL",
            entidade="AGUA",
            viveiro_codigo=viveiro.codigo,
            data_evento=medicao_in.data,
            tipo_anomalia="O2_CRITICO" if ("O2" in " ".join(motivo)) else "AMONIA_CRITICA",
            severidade="CRITICA",
            mensagem=" | ".join(motivo) or "Parâmetro crítico de qualidade da água detectado."
        )
        db.add(pendencia)

    db.commit()
    db.refresh(nova_medicao)
    return nova_medicao
