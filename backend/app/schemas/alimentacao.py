"""Schemas Pydantic v2 para lançamentos diários de arraçoamento e sobras (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LancamentoAlimentacaoBase(BaseModel):
    """Atributos base de arraçoamento diário."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    ciclo_id: int = Field(..., description="ID do ciclo de cultivo")
    data: date = Field(..., description="Data do trato diário")
    doc: int = Field(..., ge=0, description="Dias de Cultivo (DOC)")

    # Trato Matutino
    racao_manha_kg: float = Field(0.0, ge=0, description="Quilogramas no trato da manhã")
    sobra_manha: Optional[int] = Field(None, ge=0, le=3, description="Nível de sobra: 0 (limpa) a 3 (muita)")

    # Trato Vespertino
    racao_tarde_kg: float = Field(0.0, ge=0, description="Quilogramas no trato da tarde")
    sobra_tarde: Optional[int] = Field(None, ge=0, le=3, description="Nível de sobra: 0 a 3")

    # Trato Noturno
    racao_noite_kg: float = Field(0.0, ge=0, description="Quilogramas no trato da noite")
    sobra_noite: Optional[int] = Field(None, ge=0, le=3, description="Nível de sobra: 0 a 3")

    observacoes: Optional[str] = None


class LancamentoAlimentacaoCreate(LancamentoAlimentacaoBase):
    """Schema para gravação de novo arraçoamento diário."""
    hash_linha: Optional[str] = None


class LancamentoAlimentacaoUpdate(BaseModel):
    """Atualização de dados de arraçoamento."""
    racao_manha_kg: Optional[float] = Field(None, ge=0)
    sobra_manha: Optional[int] = Field(None, ge=0, le=3)
    racao_tarde_kg: Optional[float] = Field(None, ge=0)
    sobra_tarde: Optional[int] = Field(None, ge=0, le=3)
    racao_noite_kg: Optional[float] = Field(None, ge=0)
    sobra_noite: Optional[int] = Field(None, ge=0, le=3)
    observacoes: Optional[str] = None


class LancamentoAlimentacaoResponse(LancamentoAlimentacaoBase):
    """Schema de retorno do arraçoamento com totais acumulados."""
    id: int
    fazenda_id: str
    total_dia_kg: float
    consumo_acumulado_kg: float
    hash_linha: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
