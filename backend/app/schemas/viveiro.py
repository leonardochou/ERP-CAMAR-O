"""Schemas Pydantic v2 para Viveiros (Multi-Tenant)."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ViveiroBase(BaseModel):
    """Atributos base de um viveiro."""
    fazenda_id: Optional[str] = Field(None, description="ID da fazenda proprietária")
    codigo: str = Field(..., description="Código identificador do tanque (ex: V-01, V-15)")
    nome_operacional: str = Field(..., description="Nome operacional de campo")
    nome_pai: Optional[str] = Field(None, description="Nome do pai no mapa, ex: Viveiro 1")
    numero_pai: Optional[int] = Field(None, description="Número oficial do pai de 1 a 10")
    setor: str = Field(..., description="Setor topográfico (Norte, Oeste, Central, Leste)")
    area_m2: float = Field(..., gt=0, description="Área em metros quadrados")
    area_ha: float = Field(..., gt=0, description="Área em hectares")
    area_satelite_m2: Optional[float] = Field(None, description="Área original do satélite Google Maps")
    area_ajustada_m2: Optional[float] = Field(None, description="Área calibrada por medição precisa")
    profundidade_media_m: float = Field(1.20, gt=0, description="Profundidade média em metros")
    volume_m3: float = Field(..., gt=0, description="Volume cúbico útil de água")
    tipo_uso: str = Field("Engorda", description="Uso do tanque: Engorda, Berçário, Bacia, Parado")
    origem_metragem: Optional[str] = Field("SATELITE_GOOGLE_MAPS", description="Origem da metragem")
    ativo: bool = Field(True, description="Indicador se o tanque está apto à operação")
    observacoes: Optional[str] = None


class ViveiroCreate(ViveiroBase):
    """Schema para criação de um novo viveiro."""
    pass


class ViveiroUpdate(BaseModel):
    """Schema para atualização parcial de dados do viveiro."""
    nome_operacional: Optional[str] = None
    nome_pai: Optional[str] = None
    numero_pai: Optional[int] = None
    setor: Optional[str] = None
    area_m2: Optional[float] = Field(None, gt=0)
    area_ha: Optional[float] = Field(None, gt=0)
    area_ajustada_m2: Optional[float] = Field(None, gt=0)
    profundidade_media_m: Optional[float] = Field(None, gt=0)
    volume_m3: Optional[float] = Field(None, gt=0)
    tipo_uso: Optional[str] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None


class ViveiroAjusteMetragemRequest(BaseModel):
    """Schema para solicitação de calibração de metragem (Satélite vs Campo)."""
    area_ajustada_m2: float = Field(..., gt=0, description="Nova área calibrada em metros quadrados")
    profundidade_media_m: Optional[float] = Field(None, gt=0, description="Profundidade média em metros (padrão 1.20)")
    observacoes: Optional[str] = Field(None, description="Motivo ou método de medição (ex: Trena, Drone, Topografia)")


class ViveiroResponse(ViveiroBase):
    """Schema de retorno completo do viveiro."""
    id: int
    fazenda_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ViveiroMapaItem(BaseModel):
    """Item resumido do viveiro para o mapa interativo 2D dos 15 tanques."""
    id: int
    fazenda_id: str
    codigo: str
    nome_operacional: str
    nome_pai: Optional[str] = None
    numero_pai: Optional[int] = None
    setor: str
    area_m2: float
    area_ha: float
    area_satelite_m2: Optional[float] = None
    area_ajustada_m2: Optional[float] = None
    volume_m3: float
    tipo_uso: str = "Engorda"
    status_cor: str = Field("VAZIO", description="OTIMO (verde), ATENCAO (amarelo), CRITICO (vermelho), VAZIO (cinza)")
    ciclo_ativo_id: Optional[int] = None
    numero_lote: Optional[str] = None
    doc_atual: Optional[int] = None
    ultimo_o2: Optional[float] = None
    ultimo_peso_g: Optional[float] = None
    biomassa_estimada_kg: Optional[float] = None
