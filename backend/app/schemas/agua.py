"""Schemas Pydantic v2 para monitoramento de qualidade da água (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MonitoramentoAguaBase(BaseModel):
    """Atributos base do monitoramento físico-químico da água."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    viveiro_id: int = Field(..., description="ID do viveiro monitorado")
    ciclo_id: Optional[int] = Field(None, description="ID do ciclo ativo se houver")
    data: date = Field(..., description="Data da medição")
    dia_ciclo: Optional[int] = Field(None, ge=0)

    # Parâmetros Matutinos
    o2_manha: Optional[float] = Field(None, ge=0, description="Oxigênio Dissolvido matutino (mg/L)")
    temperatura_manha: Optional[float] = Field(None, description="Temperatura da água manhã (°C)")
    ph_manha: Optional[float] = Field(None, ge=0, le=14, description="pH matutino")

    # Parâmetros Noturnos/Vespertinos
    o2_noite: Optional[float] = Field(None, ge=0, description="Oxigênio Dissolvido noturno (mg/L)")
    temperatura_noite: Optional[float] = Field(None, description="Temperatura da água noite (°C)")
    ph_tarde: Optional[float] = Field(None, ge=0, le=14, description="pH vespertino")

    # Parâmetros Químicos Gerais
    salinidade_ppt: Optional[float] = Field(None, ge=0, description="Salinidade (ppt)")
    transparencia_secchi_cm: Optional[float] = Field(None, ge=0, description="Transparência Secchi (cm)")
    amonia_mg_l: Optional[float] = Field(None, ge=0, description="Amônia total (mg/L)")
    nitrito_mg_l: Optional[float] = Field(None, ge=0, description="Nitrito (mg/L)")
    alcalinidade_mg_l: Optional[float] = Field(None, ge=0, description="Alcalinidade (mg/L CaCO3)")

    acoes_adotadas: Optional[str] = None


class MonitoramentoAguaCreate(MonitoramentoAguaBase):
    """Schema para gravação de nova medição de água."""
    hash_linha: Optional[str] = None


class MonitoramentoAguaUpdate(BaseModel):
    """Atualização parcial dos parâmetros de água."""
    o2_manha: Optional[float] = Field(None, ge=0)
    o2_noite: Optional[float] = Field(None, ge=0)
    temperatura_manha: Optional[float] = None
    temperatura_noite: Optional[float] = None
    ph_manha: Optional[float] = Field(None, ge=0, le=14)
    ph_tarde: Optional[float] = Field(None, ge=0, le=14)
    salinidade_ppt: Optional[float] = Field(None, ge=0)
    transparencia_secchi_cm: Optional[float] = Field(None, ge=0)
    amonia_mg_l: Optional[float] = Field(None, ge=0)
    nitrito_mg_l: Optional[float] = Field(None, ge=0)
    alcalinidade_mg_l: Optional[float] = Field(None, ge=0)
    acoes_adotadas: Optional[str] = None


class MonitoramentoAguaResponse(MonitoramentoAguaBase):
    """Schema de retorno do monitoramento com status classificado."""
    id: int
    fazenda_id: str
    delta_ph: Optional[float] = None
    status_tanque: str
    hash_linha: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
