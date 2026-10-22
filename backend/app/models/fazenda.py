"""Modelo ORM para a entidade Fazenda (Multi-Tenant)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Fazenda(Base):
    """Representa uma propriedade agrícola/fazenda cadastrada no ERP (Multi-Tenant)."""
    __tablename__ = "fazendas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    codigo = Column(String(30), unique=True, nullable=False, index=True)  # ex: FAZ_ARRENDADA, FAZ_HAKKA
    nome = Column(String(100), nullable=False)                            # ex: "Fazenda Arrendada", "Fazenda Hakka"
    tipo_propriedade = Column(String(20), default="arrendada")            # 'arrendada' ou 'propria'
    municipio_uf = Column(String(100), default="Ceará-Mirim/RN")          # Localização geográfica
    status = Column(String(20), default="ativa", index=True)              # 'ativa', 'inativa', 'planejada'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    viveiros = relationship("Viveiro", back_populates="fazenda", cascade="all, delete-orphan")
