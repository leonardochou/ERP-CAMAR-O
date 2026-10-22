"""Schemas Pydantic v2 para a Central de Auditoria Ativa de Dados (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AuditoriaPendenciaBase(BaseModel):
    """Atributos base da pendência de auditoria."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    origem: str = Field("MANUAL", description="Origem do dado: MANUAL, EXCEL, WHATSAPP")
    entidade: str = Field(..., description="Entidade afetada: ALIMENTACAO, AGUA, BIOMETRIA, CICLO")
    viveiro_codigo: str = Field(..., description="Código do viveiro (ex: V-03)")
    data_evento: date = Field(..., description="Data do evento auditado")
    tipo_anomalia: str = Field(..., description="CONFLITO_DADOS, O2_CRITICO, AMONIA_CRITICA, SOBRA_CRONICA, FCA_DESVIO, DIA_ESQUECIDO")
    severidade: str = Field("ATENCAO", description="Severidade: INFO, ATENCAO, CRITICA")
    mensagem: str = Field(..., description="Descrição compreensível do alerta")
    dados_atuais_json: Optional[str] = None
    dados_novos_json: Optional[str] = None


class AuditoriaPendenciaCreate(AuditoriaPendenciaBase):
    """Schema para abertura de nova pendência."""
    pass


class AuditoriaResolucaoRequest(BaseModel):
    """Payload para resolução de uma pendência em 1 clique."""
    acao: str = Field(..., description="MANTER_NOVO, MANTER_ANTIGO, SOMAR_TURNOS, DESCARTAR")


class AuditoriaPendenciaResponse(AuditoriaPendenciaBase):
    """Schema de retorno da pendência com status de resolução."""
    id: int
    fazenda_id: str
    resolvido: bool
    acao_resolucao: Optional[str] = None
    resolvido_em: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
