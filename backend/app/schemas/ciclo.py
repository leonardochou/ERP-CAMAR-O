"""Schemas Pydantic v2 para Ciclos de Cultivo e Lotes (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CicloBase(BaseModel):
    """Atributos base de um ciclo de cultivo."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    viveiro_id: int = Field(..., description="ID do viveiro associado")
    numero_lote: Optional[str] = Field(None, description="Identificador do lote (ex: LOTE-2026-01-V03 ou V-01 • Ciclo 2026.1)")
    codigo_ciclo: Optional[str] = Field(None, description="Código executivo do ciclo (ex: V-01 • Ciclo 2026.1)")
    ano_safra: Optional[int] = Field(None, description="Ano-safra do cultivo (ex: 2026)")
    numero_sequencial: Optional[int] = Field(1, description="Número da safra no viveiro (1, 2, 3...)")
    data_povoamento: date = Field(..., description="Data de povoamento das pós-larvas")
    pls_estocadas: int = Field(..., gt=0, description="Quantidade total de pós-larvas estocadas")
    laboratorio: Optional[str] = Field(None, description="Laboratório fornecedor das PLs (ex: AQUATEC)")
    peso_inicial_g: float = Field(0.01, gt=0, description="Peso médio inicial das PLs (g)")
    status: str = Field("EM CULTIVO ATIVO", description="EM PREPARACAO, EM CULTIVO ATIVO, DESPESCA_PARCIAL, DESPESCADO, ENCERRADO")
    observacoes: Optional[str] = None


class CicloCreate(CicloBase):
    """Schema para início de um novo ciclo de cultivo."""
    densidade_pl_m2: Optional[float] = None


class CicloIniciarRequest(BaseModel):
    """Payload para início guiado de novo ciclo com numeração sequencial automática."""
    viveiro_id: int = Field(..., description="ID do viveiro associado")
    ano_safra: Optional[int] = Field(None, description="Ano-safra (padrão ano atual)")
    data_povoamento: date = Field(..., description="Data de início do povoamento")
    pls_estocadas: int = Field(..., gt=0, description="Quantidade de pós-larvas")
    laboratorio: Optional[str] = Field("AQUATEC", description="Laboratório de origem")
    peso_inicial_g: float = Field(0.01, gt=0, description="Gramatura inicial das pós-larvas")
    observacoes: Optional[str] = None


class CicloUpdate(BaseModel):
    """Atualização parcial de dados cadastrais do ciclo."""
    laboratorio: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None


class DespescaParcialRequest(BaseModel):
    """Payload para registro de despesca parcial (desbaste/raleio)."""
    data: date = Field(..., description="Data da despesca parcial")
    camarao_colhido_kg: float = Field(..., gt=0, description="Total colhido no desbaste (kg)")
    gramatura_media_g: float = Field(..., gt=0, description="Gramatura média aferida (g)")
    comprador: Optional[str] = Field("Mercado Local", description="Comprador ou destino")
    preco_kg_rs: Optional[float] = Field(22.0, ge=0, description="Preço por kg negociado (R$)")
    observacoes: Optional[str] = None


class FechamentoSafraRequest(BaseModel):
    """Payload para encerramento de lote e registro da despesca final."""
    data_despesca: date = Field(..., description="Data da despesca final")
    camarao_colhido_kg: float = Field(..., gt=0, description="Total líquido despescado em kg")
    peso_final_g: float = Field(..., gt=0, description="Peso médio individual final em gramas")
    faturamento_total_rs: Optional[float] = Field(None, ge=0)
    preco_kg_rs: Optional[float] = Field(None, ge=0)
    comprador: Optional[str] = None
    observacoes: Optional[str] = None


class EncerramentoCicloRequest(FechamentoSafraRequest):
    """Alias para encerramento executivo de ciclo de cultivo."""
    pass


class CicloResponse(CicloBase):
    """Schema de retorno completo do ciclo com indicadores consolidados."""
    id: int
    fazenda_id: str
    densidade_pl_m2: Optional[float] = None
    racao_total_kg: Optional[float] = 0.0
    despescas_parciais_kg: Optional[float] = 0.0
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
