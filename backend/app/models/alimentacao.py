"""Modelo ORM para lançamentos diários de arraçoamento e sobras de bandejas."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class LancamentoAlimentacao(Base):
    """Representa o arraçoamento diário por turnos e leituras de bandeja de um ciclo."""
    __tablename__ = "lancamentos_alimentacao"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_cultivo.id", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    doc = Column(Integer, nullable=False)  # Day of Culture (Dias de Cultivo)

    # Trato Matutino (Trato A)
    racao_manha_kg = Column(Float, default=0.0)
    sobra_manha = Column(Integer, nullable=True)  # 0: Limpa, 1: Pouca, 2: Normal, 3: Muita

    # Trato Vespertino (Trato B)
    racao_tarde_kg = Column(Float, default=0.0)
    sobra_tarde = Column(Integer, nullable=True)  # 0 a 3

    # Trato Noturno (Opcional / Turno C)
    racao_noite_kg = Column(Float, default=0.0)
    sobra_noite = Column(Integer, nullable=True)  # 0 a 3

    # Totalizadores Calculados
    total_dia_kg = Column(Float, default=0.0)
    consumo_acumulado_kg = Column(Float, default=0.0)

    # Hash SHA-256 para prevenção estrita de duplicações na ingestão
    hash_linha = Column(String(64), unique=True, index=True, nullable=True)
    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Restrição de unicidade: apenas um registro diário oficial por ciclo
    __table_args__ = (
        UniqueConstraint("ciclo_id", "data", name="uq_alimentacao_ciclo_data"),
    )

    # Relacionamento
    ciclo = relationship("CicloCultivo", back_populates="alimentacoes")
