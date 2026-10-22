"""Schemas Pydantic v2 para Fazendas (Multi-Tenant)."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FazendaBase(BaseModel):
    """Atributos base de uma fazenda."""
    codigo: str = Field(..., description="Código identificador único (ex: FAZ_ARRENDADA, FAZ_HAKKA)")
    nome: str = Field(..., description="Nome comercial ou de registro da fazenda")
    tipo_propriedade: str = Field("arrendada", description="'arrendada' ou 'propria'")
    municipio_uf: str = Field("Ceará-Mirim/RN", description="Município e Estado de localização")
    status: str = Field("ativa", description="'ativa', 'inativa', 'planejada'")


class FazendaCreate(FazendaBase):
    """Schema para cadastro de nova fazenda."""
    id: Optional[str] = None


class FazendaUpdate(BaseModel):
    """Atualização parcial de dados cadastrais da fazenda."""
    nome: Optional[str] = None
    tipo_propriedade: Optional[str] = None
    municipio_uf: Optional[str] = None
    status: Optional[str] = None


class FazendaResponse(FazendaBase):
    """Schema de retorno da fazenda."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
