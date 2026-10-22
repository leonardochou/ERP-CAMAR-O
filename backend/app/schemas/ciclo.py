"""Schemas Pydantic v2 para Ciclos de Cultivo e Lotes (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CicloBase(BaseModel):
    """Atributos base de um ciclo de cultivo."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    viveiro_id: int = Field(..., description="ID do viveiro associado")
    numero_lote: str = Field(..., description="Identificador do lote (ex: LOTE-2026-01-V03)")
    data_povoamento: date = Field(..., description="Data de povoamento das pós-larvas")
    pls_estocadas: int = Field(..., gt=0, description="Quantidade total de pós-larvas estocadas")
    laboratorio: Optional[str] = Field(None, description="Laboratório fornecedor das PLs (ex: AQUATEC)")
    peso_inicial_g: float = Field(0.01, gt=0, description="Peso médio inicial das PLs (g)")
    status: str = Field("EM CULTIVO ATIVO", description="EM PREPARACAO, EM CULTIVO ATIVO, DESPESCADO")
    observacoes: Optional[str] = None


class CicloCreate(CicloBase):
    """Schema para início de um novo ciclo de cultivo."""
    densidade_pl_m2: Optional[float] = None


class CicloUpdate(BaseModel):
    """Atualização parcial de dados cadastrais do ciclo."""
    laboratorio: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None


class FechamentoSafraRequest(BaseModel):
    """Payload para encerramento de lote e registro da despesca final."""
    data_despesca: date = Field(..., description="Data da despesca final")
    camarao_colhido_kg: float = Field(..., gt=0, description="Total líquido despescado em kg")
    peso_final_g: float = Field(..., gt=0, description="Peso médio individual final em gramas")
    faturamento_total_rs: Optional[float] = Field(None, ge=0)
    observacoes: Optional[str] = None


class CicloResponse(CicloBase):
    """Schema de retorno completo do ciclo com indicadores consolidados."""
    id: int
    fazenda_id: str
    densidade_pl_m2: Optional[float] = None
    data_despesca: Optional[date] = None
    camarao_colhido_kg: Optional[float] = None
    peso_final_g: Optional[float] = None
    sobrevivencia_real_pct: Optional[float] = None
    fca_real_final: Optional[float] = None
    produtividade_kg_ha: Optional[float] = None
    faturamento_total_rs: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
