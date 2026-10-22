"""Endpoints REST para consolidação analítica e relatórios executivos (Camadas Macro e Micro) com Multi-Tenant."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria

router = APIRouter()


@router.get("/resumo-executivo", summary="KPIs consolidados para a Camada Macro do Dashboard")
def obter_resumo_executivo(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retorna os indicadores executivos globais da fazenda ativa."""
    total_viveiros = db.query(Viveiro).filter(Viveiro.fazenda_id == fazenda.id).count()
    ciclos_ativos = db.query(CicloCultivo).filter(
        CicloCultivo.fazenda_id == fazenda.id,
        CicloCultivo.status == "EM CULTIVO ATIVO"
    ).all()

    biomassa_total_kg = 0.0
    racao_total_acumulada_kg = 0.0
    total_fca_ponderado_num = 0.0
    total_fca_ponderado_den = 0.0

    tanques_otimo = 0
    tanques_atencao = 0
    tanques_critico = 0
    tanques_vazio = total_viveiros - len(ciclos_ativos)

    for ciclo in ciclos_ativos:
        ultima_bio = db.query(Biometria).filter(
            Biometria.ciclo_id == ciclo.id
        ).order_by(desc(Biometria.data)).first()

        if ultima_bio and ultima_bio.biomassa_estimada_kg:
            biomassa_total_kg += ultima_bio.biomassa_estimada_kg
            if ultima_bio.fca_parcial:
                total_fca_ponderado_num += (ultima_bio.fca_parcial * ultima_bio.biomassa_estimada_kg)
                total_fca_ponderado_den += ultima_bio.biomassa_estimada_kg

        racao_ciclo = db.query(func.sum(LancamentoAlimentacao.total_dia_kg)).filter(
            LancamentoAlimentacao.ciclo_id == ciclo.id
        ).scalar() or 0.0
        racao_total_acumulada_kg += racao_ciclo

        ultima_agua = db.query(MonitoramentoAgua).filter(
            MonitoramentoAgua.viveiro_id == ciclo.viveiro_id
        ).order_by(desc(MonitoramentoAgua.data)).first()

        status_tanque = ultima_agua.status_tanque if ultima_agua else "OTIMO"
        if status_tanque == "CRITICO":
            tanques_critico += 1
        elif status_tanque == "ATENCAO":
            tanques_atencao += 1
        else:
            tanques_otimo += 1

    fca_ponderado = round(total_fca_ponderado_num / total_fca_ponderado_den, 2) if total_fca_ponderado_den > 0 else 0.0

    return {
        "fazenda": {
            "id": fazenda.id,
            "codigo": fazenda.codigo,
            "nome": fazenda.nome,
            "tipo_propriedade": fazenda.tipo_propriedade,
            "municipio_uf": fazenda.municipio_uf
        },
        "total_viveiros": total_viveiros,
        "tanques_em_cultivo": len(ciclos_ativos),
        "biomassa_total_viva_kg": round(biomassa_total_kg, 2),
        "fca_ponderado_global": fca_ponderado,
        "consumo_total_racao_kg": round(racao_total_acumulada_kg, 2),
        "distribuicao_status": {
            "otimo": tanques_otimo,
            "atencao": tanques_atencao,
            "critico": tanques_critico,
            "vazio": tanques_vazio
        }
    }


@router.get("/viveiro/{codigo}/dashboard", summary="Dados consolidados para a Camada Micro do Viveiro")
def obter_dashboard_viveiro(
    codigo: str,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retorna dados da Camada Micro: curvas de crescimento, histórico de oxigênio e KPIs do viveiro."""
    viveiro = db.query(Viveiro).filter(
        Viveiro.fazenda_id == fazenda.id,
        Viveiro.codigo == codigo.upper()
    ).first()
    if not viveiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Viveiro '{codigo}' não encontrado na fazenda '{fazenda.nome}'."
        )

    ciclo_ativo = db.query(CicloCultivo).filter(
        CicloCultivo.viveiro_id == viveiro.id,
        CicloCultivo.status == "EM CULTIVO ATIVO"
    ).first()

    medicoes_agua = db.query(MonitoramentoAgua).filter(
        MonitoramentoAgua.viveiro_id == viveiro.id
    ).order_by(MonitoramentoAgua.data.asc()).limit(30).all()

    serie_agua = [
        {
            "data": m.data.isoformat(),
            "o2_manha": m.o2_manha,
            "o2_noite": m.o2_noite,
            "temperatura_manha": m.temperatura_manha,
            "salinidade_ppt": m.salinidade_ppt,
            "ph_manha": m.ph_manha,
            "ph_tarde": m.ph_tarde,
            "status_tanque": m.status_tanque
        }
        for m in medicoes_agua
    ]

    serie_biometria = []
    serie_alimentacao = []
    kpis = {}

    if ciclo_ativo:
        biometrias = db.query(Biometria).filter(
            Biometria.ciclo_id == ciclo_ativo.id
        ).order_by(Biometria.data.asc()).all()

        serie_biometria = [
            {
                "data": b.data.isoformat(),
                "doc": b.doc,
                "peso_medio_g": b.peso_medio_g,
                "gmd_g_dia": b.gmd_g_dia,
                "biomassa_estimada_kg": b.biomassa_estimada_kg,
                "fca_parcial": b.fca_parcial
            }
            for b in biometrias
        ]

        alimentacoes = db.query(LancamentoAlimentacao).filter(
            LancamentoAlimentacao.ciclo_id == ciclo_ativo.id
        ).order_by(LancamentoAlimentacao.data.asc()).all()

        serie_alimentacao = [
            {
                "data": a.data.isoformat(),
                "doc": a.doc,
                "total_dia_kg": a.total_dia_kg,
                "consumo_acumulado_kg": a.consumo_acumulado_kg,
                "sobra_manha": a.sobra_manha,
                "sobra_tarde": a.sobra_tarde
            }
            for a in alimentacoes
        ]

        ultima_bio = biometrias[-1] if biometrias else None
        racao_total = alimentacoes[-1].consumo_acumulado_kg if alimentacoes else 0.0

        kpis = {
            "lote": ciclo_ativo.numero_lote,
            "data_povoamento": ciclo_ativo.data_povoamento.isoformat(),
            "pls_estocadas": ciclo_ativo.pls_estocadas,
            "densidade_pl_m2": ciclo_ativo.densidade_pl_m2,
            "ultimo_peso_g": ultima_bio.peso_medio_g if ultima_bio else ciclo_ativo.peso_inicial_g,
            "biomassa_estimada_kg": ultima_bio.biomassa_estimada_kg if ultima_bio else 0.0,
            "fca_parcial": ultima_bio.fca_parcial if ultima_bio else None,
            "racao_total_acumulada_kg": racao_total
        }

    return {
        "fazenda_id": fazenda.id,
        "viveiro": {
            "codigo": viveiro.codigo,
            "nome_operacional": viveiro.nome_operacional,
            "setor": viveiro.setor,
            "area_ha": viveiro.area_ha,
            "profundidade_media_m": viveiro.profundidade_media_m,
            "volume_m3": viveiro.volume_m3,
            "tipo_uso": viveiro.tipo_uso
        },
        "ciclo_ativo": kpis,
        "serie_agua": serie_agua,
        "serie_biometria": serie_biometria,
        "serie_alimentacao": serie_alimentacao
    }
