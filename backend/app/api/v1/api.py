"""Agregador de roteadores da API v1 do ERP CAMARÃO."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    fazendas,
    viveiros,
    ciclos,
    alimentacao,
    agua,
    biometrias,
    despescas,
    auditoria,
    whatsapp,
    relatorios,
    ingestao,
    equipe,
    contabilidade,
)

api_router = APIRouter()

api_router.include_router(fazendas.router, prefix="/fazendas", tags=["Fazendas & Multi-Tenant"])
api_router.include_router(viveiros.router, prefix="/viveiros", tags=["Viveiros & Topografia"])
api_router.include_router(ciclos.router, prefix="/ciclos", tags=["Ciclos de Cultivo & Safra"])
api_router.include_router(alimentacao.router, prefix="/alimentacao", tags=["Arraçoamento & Sobras"])
api_router.include_router(agua.router, prefix="/agua", tags=["Qualidade da Água"])
api_router.include_router(biometrias.router, prefix="/biometrias", tags=["Biometrias & Zootecnia"])
api_router.include_router(despescas.router, prefix="/despescas", tags=["Despescas & Faturamento"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["Central de Auditoria Ativa"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["Assistente WhatsApp & Alertas"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["Relatórios & Dashboards"])
api_router.include_router(ingestao.router, prefix="/ingestao", tags=["Ingestão & Sincronização"])
api_router.include_router(equipe.router, prefix="/equipe", tags=["Equipe & Vigia Noturno"])
api_router.include_router(contabilidade.router, prefix="/contabilidade", tags=["Hub Contábil, DRE & Fluxo de Caixa"])
