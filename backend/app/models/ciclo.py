"""Modelo ORM para a entidade CicloCultivo (Lote de camarão)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class CicloCultivo(Base):
    """Representa uma safra ou lote de camarão povoados em um viveiro específico."""
    __tablename__ = "ciclos_cultivo"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    viveiro_id = Column(Integer, ForeignKey("viveiros.id", ondelete="CASCADE"), nullable=False, index=True)
    numero_lote = Column(String(50), index=True, nullable=False)
    data_povoamento = Column(Date, nullable=False)
    pls_estocadas = Column(Integer, nullable=False)  # Quantidade de pós-larvas (ex: 65000)
    densidade_pl_m2 = Column(Float, nullable=True)   # pls_estocadas / area_m2
    laboratorio = Column(String(50), nullable=True)  # ex: AQUATEC, NE, tecmaris
    peso_inicial_g = Column(Float, default=0.01)     # Padrão 0.01g
    status = Column(String(30), default="EM CULTIVO ATIVO", index=True)  # EM PREPARACAO, EM CULTIVO ATIVO, DESPESCADO

    # Métricas de Fechamento de Safra (Despesca)
    data_despesca = Column(Date, nullable=True)
    camarao_colhido_kg = Column(Float, nullable=True)
    peso_final_g = Column(Float, nullable=True)
    sobrevivencia_real_pct = Column(Float, nullable=True)
    fca_real_final = Column(Float, nullable=True)
    produtividade_kg_ha = Column(Float, nullable=True)
    faturamento_total_rs = Column(Float, nullable=True)
    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("fazenda_id", "numero_lote", name="uq_ciclo_fazenda_lote"),
    )

    # Relacionamentos
    viveiro = relationship("Viveiro", back_populates="ciclos")
    alimentacoes = relationship("LancamentoAlimentacao", back_populates="ciclo", cascade="all, delete-orphan")
    biometrias = relationship("Biometria", back_populates="ciclo", cascade="all, delete-orphan")
    despescas = relationship("DespescaVenda", back_populates="ciclo", cascade="all, delete-orphan")
