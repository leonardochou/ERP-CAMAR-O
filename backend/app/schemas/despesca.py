"""Schemas Pydantic v2 para Despescas e Vendas de Camarão (Multi-Tenant)."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DespescaVendaBase(BaseModel):
    """Atributos base de venda de camarão despescado."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    ciclo_id: int = Field(..., description="ID do ciclo despescado")
    data: date = Field(..., description="Data da despesca ou emissão")
    tipo_despesca: str = Field("TOTAL", description="TOTAL ou DESBASTE")
    gramatura_media_g: float = Field(..., gt=0, description="Gramatura média aferida (g)")
    camarao_colhido_kg: float = Field(..., gt=0, description="Peso líquido em quilogramas")
    comprador: str = Field(..., description="Nome do comprador ou beneficiadora")
    preco_kg_rs: float = Field(..., gt=0, description="Preço por kg negociado (R$)")
    data_vencimento: Optional[date] = None
    status_pagamento: str = Field("A RECEBER", description="RECEBIDO, A RECEBER, EM ATRASO")
    data_pagamento: Optional[date] = None
    forma_pagamento: Optional[str] = None
    numero_romaneio: Optional[str] = None
    observacoes: Optional[str] = None


class DespescaVendaCreate(DespescaVendaBase):
    """Schema para cadastro de nova venda/despesca."""
    pass


class DespescaVendaUpdate(BaseModel):
    """Atualização de dados da venda/despesca."""
    status_pagamento: Optional[str] = None
    data_pagamento: Optional[date] = None
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None


class DespescaVendaResponse(DespescaVendaBase):
    """Schema de retorno completo com faturamento bruto calculado."""
    id: int
    fazenda_id: str
    faturamento_bruto_rs: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
