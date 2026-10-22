"""Modelo ORM para a entidade Viveiro (Tanque de cultivo)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Viveiro(Base):
    """Representa um viveiro/tanque na infraestrutura da fazenda em Ceará-Mirim/RN."""
    __tablename__ = "viveiros"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(10), index=True, nullable=False)  # ex: V-01, V-02 ... V-15
    nome_operacional = Column(String(50), nullable=False)    # ex: "C1", "Tanque Central 1"
    nome_pai = Column(String(50), nullable=True)            # Nome oficial do pai, ex: "Viveiro 1"
    numero_pai = Column(Integer, nullable=True)             # 1 a 10 (ou None para tanques de apoio)
    setor = Column(String(20), nullable=False)              # "Norte", "Oeste", "Central", "Leste"
    area_m2 = Column(Float, nullable=False)                  # Área operacional vigente (em m²)
    area_ha = Column(Float, nullable=False)                  # Área operacional em hectares
    area_satelite_m2 = Column(Float, nullable=True)         # Metragem original obtida via Google Maps / Satélite
    area_ajustada_m2 = Column(Float, nullable=True)         # Metragem calibrada / medida no campo
    profundidade_media_m = Column(Float, default=1.20)
    volume_m3 = Column(Float, nullable=False)                # area_m2 * profundidade
    tipo_uso = Column(String(40), default="Engorda")        # Engorda, Berçário, Bacia, Parado
    origem_metragem = Column(String(50), default="SATELITE_GOOGLE_MAPS") # SATELITE_GOOGLE_MAPS ou MEDICAO_CAMPO
    ativo = Column(Boolean, default=True)
    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("fazenda_id", "codigo", name="uq_viveiro_fazenda_codigo"),
    )

    # Relacionamentos
    fazenda = relationship("Fazenda", back_populates="viveiros")
    ciclos = relationship("CicloCultivo", back_populates="viveiro", cascade="all, delete-orphan")
    monitoramentos_agua = relationship("MonitoramentoAgua", back_populates="viveiro", cascade="all, delete-orphan")
