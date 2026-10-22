"""Schemas Pydantic v2 para integração com Assistente WhatsApp."""
from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class WhatsAppMensagemEntrada(BaseModel):
    """Payload recebido via webhook do WhatsApp (áudio ou texto)."""
    remetente: str = Field(..., description="Número de telefone ou identificador do operador")
    tipo_mensagem: str = Field("texto", description="texto ou audio")
    texto: Optional[str] = Field(None, description="Conteúdo do texto ou transcrição")
    audio_url: Optional[str] = Field(None, description="URL do arquivo de áudio se recebido via mídia")


class WhatsAppParametrosExtraidos(BaseModel):
    """Parâmetros zootécnicos extraídos estruturadamente da mensagem do operador."""
    viveiro_codigo: str
    data: Optional[date] = None
    turno: Optional[str] = None  # manha, tarde, noite
    racao_kg: Optional[float] = None
    sobra_nivel: Optional[int] = None  # 0 a 3
    o2_mg_l: Optional[float] = None
    ph: Optional[float] = None
    salinidade_ppt: Optional[float] = None
    peso_medio_g: Optional[float] = None
    observacao: Optional[str] = None


class AlertaEmergenciaRequest(BaseModel):
    """Disparo imediato de alerta de emergência para a equipe e vigia noturno."""
    destinatario: str = Field(..., description="Número ou grupo de destino (ex: vigia noturno)")
    viveiro_codigo: str = Field(..., description="Tanque em estado crítico")
    parametro_critico: str = Field(..., description="Ex: Oxigênio Dissolvido < 3.0 mg/L")
    valor_aferido: float = Field(..., description="Valor medido que disparou o alerta")
    mensagem: str = Field(..., description="Mensagem enfática de alerta")
