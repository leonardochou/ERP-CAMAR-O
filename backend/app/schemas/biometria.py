"""Schemas Pydantic v2 para Biometrias e Cálculos Zootécnicos (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BiometriaBase(BaseModel):
    """Atributos base da biometria amostral."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    ciclo_id: int = Field(..., description="ID do ciclo de cultivo")
    data: date = Field(..., description="Data da pesagem em campo")
    doc: int = Field(..., ge=0, description="Dias de Cultivo (DOC)")
    peso_medio_g: float = Field(..., gt=0, description="Peso médio individual em gramas")
    amostra_qtd: int = Field(100, gt=0, description="Quantidade de camarões na amostra")
    sobrevivencia_estimada_pct: float = Field(80.0, gt=0, le=100, description="Estimativa de sobrevivência (%)")
    uniformidade_pct: Optional[float] = Field(None, ge=0, le=100, description="Uniformidade do lote (%)")
    observacoes: Optional[str] = None


class BiometriaCreate(BiometriaBase):
    """Schema para entrada de nova biometria."""
    pass


class BiometriaUpdate(BaseModel):
    """Atualização parcial de dados da biometria."""
    peso_medio_g: Optional[float] = Field(None, gt=0)
    amostra_qtd: Optional[int] = Field(None, gt=0)
    sobrevivencia_estimada_pct: Optional[float] = Field(None, gt=0, le=100)
    uniformidade_pct: Optional[float] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = None


class BiometriaResponse(BiometriaBase):
    """Schema de retorno da biometria com os indicadores zootécnicos calculados."""
    id: int
    fazenda_id: str
    ganho_peso_semanal_g: Optional[float] = None
    gmd_g_dia: Optional[float] = None
    populacao_estimada: Optional[int] = None
    biomassa_estimada_kg: Optional[float] = None
    racao_acumulada_ate_data_kg: Optional[float] = None
    fca_parcial: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
