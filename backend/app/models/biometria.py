"""Modelo ORM para registros de biometria amostral e cálculo de indicadores zootécnicos."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Biometria(Base):
    """Representa a pesagem por amostragem em tarrafa e cálculo zootécnico de crescimento."""
    __tablename__ = "biometrias"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_cultivo.id", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    doc = Column(Integer, nullable=False)  # Dias de Cultivo

    # Dados Amostrais de Campo
    peso_medio_g = Column(Float, nullable=False)      # Peso médio individual aferido (g)
    amostra_qtd = Column(Integer, default=100)        # Camarões pesados na amostra

    # Indicadores de Ganho e Crescimento
    ganho_peso_semanal_g = Column(Float, nullable=True)  # Ganho de peso desde a última pesagem (g)
    gmd_g_dia = Column(Float, nullable=True)             # Ganho Médio Diário ponderal (g/dia)
    sobrevivencia_estimada_pct = Column(Float, default=80.0)  # Projeção de sobrevivência (ex: 80%)

    # Indicadores Populacionais e de Biomassa
    populacao_estimada = Column(Integer, nullable=True)  # PLs * (Sobrevivência / 100)
    biomassa_estimada_kg = Column(Float, nullable=True)  # Populacao * Peso / 1000

    # Conversão Alimentar Parcial
    racao_acumulada_ate_data_kg = Column(Float, nullable=True)
    fca_parcial = Column(Float, nullable=True)           # Ração Acumulada / Biomassa Estimada

    uniformidade_pct = Column(Float, nullable=True)      # % dentro da faixa comercial
    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ciclo_id", "data", name="uq_biometria_ciclo_data"),
    )

    # Relacionamento
    ciclo = relationship("CicloCultivo", back_populates="biometrias")
