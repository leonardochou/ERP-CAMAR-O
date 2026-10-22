"""Esquemas Pydantic para validação e serialização do Módulo de Equipe, Vigia e Escalas."""
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


# -------------------------------------------------------------
# FUNCIONÁRIO
# -------------------------------------------------------------
class FuncionarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    apelido: Optional[str] = Field(None, max_length=50)
    cargo: str = Field(..., min_length=2, max_length=50)
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    chave_pix: Optional[str] = None
    tipo_contrato: str = Field("MENSALISTA", description="MENSALISTA ou DIARISTA")
    salario_base_mensal: float = Field(0.0, ge=0.0)
    valor_diaria_extra: float = Field(0.0, ge=0.0)
    encargos_estimados_pct: float = Field(0.0, ge=0.0)
    ativo: bool = True
    data_admissao: Optional[date] = None
    observacoes: Optional[str] = None


class FuncionarioCreate(FuncionarioBase):
    fazenda_id: Optional[str] = None


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    apelido: Optional[str] = None
    cargo: Optional[str] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    chave_pix: Optional[str] = None
    tipo_contrato: Optional[str] = None
    salario_base_mensal: Optional[float] = None
    valor_diaria_extra: Optional[float] = None
    encargos_estimados_pct: Optional[float] = None
    ativo: Optional[bool] = None
    data_admissao: Optional[date] = None
    observacoes: Optional[str] = None


class FuncionarioResponse(FuncionarioBase):
    id: int
    fazenda_id: str
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# ESCALA E APONTAMENTO DE OCORRÊNCIAS / EXTRAS
# -------------------------------------------------------------
class EscalaItemBase(BaseModel):
    funcionario_id: int
    data: date
    turno: str = Field("DIURNO", description="DIURNO, NOTURNO_VIGIA, FOLGA, FALTA_JUSTIFICADA, FALTA_INJUSTIFICADA, FERIAS")
    eh_extra: bool = False
    valor_diaria_aplicado: float = 0.0
    check_in_hora: Optional[str] = None
    check_out_hora: Optional[str] = None
    status_presenca: str = "AGENDADO"
    categoria_ocorrencia: str = "NORMAL"
    observacoes: Optional[str] = None


class EscalaItemCreate(EscalaItemBase):
    fazenda_id: Optional[str] = None


class EscalaApontamentoOcorrenciaRequest(BaseModel):
    """Requisição ágil para atualizar ocorrência, falta ou diária extra de um dia específico."""
    funcionario_id: int
    data: date
    turno: str
    eh_extra: bool = False
    valor_diaria_aplicado: float = 0.0
    status_presenca: str = "CONFIRMADO"
    categoria_ocorrencia: str = "NORMAL"
    observacoes: Optional[str] = None


class EscalaItemResponse(EscalaItemBase):
    id: int
    fazenda_id: str
    funcionario_nome: Optional[str] = None
    funcionario_apelido: Optional[str] = None
    funcionario_cargo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EscalaLoteRequest(BaseModel):
    itens: List[EscalaItemCreate]


class EscalaTemplateRequest(BaseModel):
    tipo_template: str = Field(..., description="12x36_VIGIAS ou 6x1_ARRACOADORES")
    data_inicio: date
    data_fim: date
    funcionario_ids: List[int]
    dia_folga_semanal: Optional[int] = 6  # 0=Segunda ... 6=Domingo (para 6x1)


class CheckInVigiaRequest(BaseModel):
    check_in_hora: Optional[str] = None
    check_out_hora: Optional[str] = None
    status_presenca: str = "CONFIRMADO"
    observacoes: Optional[str] = None


# -------------------------------------------------------------
# RESUMO FINANCEIRO E DE CUSTOS DE EQUIPE
# -------------------------------------------------------------
class ResumoCustosEquipeResponse(BaseModel):
    mes: int
    ano: int
    total_colaboradores: int
    total_salarios_fixos: float
    total_diarias_extras: float
    custo_total_folha: float
    total_faltas_registradas: int
    total_plantoes_noturnos: int
    custo_estimado_por_ha: float
    vigia_hoje_nome: Optional[str] = None
    vigia_hoje_status: Optional[str] = None
    vigia_hoje_horario: Optional[str] = None
