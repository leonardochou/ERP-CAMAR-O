"""Modelo ORM para medições físico-químicas de qualidade da água."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class MonitoramentoAgua(Base):
    """Representa as medições de parâmetros da água do viveiro (diurno e noturno)."""
    __tablename__ = "monitoramentos_agua"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    viveiro_id = Column(Integer, ForeignKey("viveiros.id", ondelete="CASCADE"), nullable=False, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_cultivo.id", ondelete="SET NULL"), nullable=True, index=True)
    data = Column(Date, nullable=False, index=True)
    dia_ciclo = Column(Integer, nullable=True)

    # Parâmetros Matutinos (Alvorecer ~05:30h)
    o2_manha = Column(Float, nullable=True)           # Oxigênio Dissolvido (mg/L)
    temperatura_manha = Column(Float, nullable=True)  # Temperatura (°C)
    ph_manha = Column(Float, nullable=True)           # pH Matutino

    # Parâmetros Vespertinos / Noturnos
    o2_noite = Column(Float, nullable=True)           # Oxigênio Dissolvido Noturno (mg/L)
    temperatura_noite = Column(Float, nullable=True)  # Temperatura (°C)
    ph_tarde = Column(Float, nullable=True)           # pH Vespertino
    delta_ph = Column(Float, nullable=True)           # ph_tarde - ph_manha

    # Parâmetros Gerais e Químicos
    salinidade_ppt = Column(Float, nullable=True)     # Salinidade (g/L ou ppt)
    transparencia_secchi_cm = Column(Float, nullable=True)  # Disco de Secchi (cm)
    amonia_mg_l = Column(Float, nullable=True)        # Amônia total tóxica (mg/L)
    nitrito_mg_l = Column(Float, nullable=True)       # Nitrito (mg/L)
    alcalinidade_mg_l = Column(Float, nullable=True)  # Alcalinidade total (mg/L CaCO3)

    # Status e Ações
    status_tanque = Column(String(20), default="OTIMO", index=True)  # OTIMO, ATENCAO, CRITICO
    acoes_adotadas = Column(String(255), nullable=True)

    # Hash SHA-256 para prevenção de duplicatas na ingestão
    hash_linha = Column(String(64), unique=True, index=True, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("viveiro_id", "data", name="uq_agua_viveiro_data"),
    )

    # Relacionamento
    viveiro = relationship("Viveiro", back_populates="monitoramentos_agua")
