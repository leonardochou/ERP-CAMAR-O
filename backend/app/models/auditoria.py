"""Modelo ORM para a Central de Auditoria Ativa de Dados (Quality Engine)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from app.core.database import Base


class AuditoriaPendencia(Base):
    """Representa uma divergência, anomalia ou pendência retida para validação pelo gestor."""
    __tablename__ = "auditoria_pendencias"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    origem = Column(String(30), default="MANUAL")     # MANUAL, EXCEL, WHATSAPP
    entidade = Column(String(30), nullable=False)     # ALIMENTACAO, AGUA, BIOMETRIA, CICLO
    viveiro_codigo = Column(String(10), nullable=False, index=True)
    data_evento = Column(Date, nullable=False, index=True)

    tipo_anomalia = Column(String(40), nullable=False, index=True)
    # CONFLITO_DADOS, O2_CRITICO, AMONIA_CRITICA, SOBRA_CRONICA, FCA_DESVIO, DIA_ESQUECIDO

    severidade = Column(String(20), default="ATENCAO", index=True)  # INFO, ATENCAO, CRITICA
    mensagem = Column(String(255), nullable=False)

    dados_atuais_json = Column(Text, nullable=True)   # JSON do registro atual no banco
    dados_novos_json = Column(Text, nullable=True)    # JSON do dado divergente proposto

    resolvido = Column(Boolean, default=False, index=True)
    acao_resolucao = Column(String(30), nullable=True)  # MANTER_NOVO, MANTER_ANTIGO, SOMAR_TURNOS, DESCARTAR
    resolvido_em = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
