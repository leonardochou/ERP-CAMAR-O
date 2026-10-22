"""Modelo ORM para registro de colheitas, despescas e vendas de camarão."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DespescaVenda(Base):
    """Representa um evento de colheita/faturamento de camarão do ciclo."""
    __tablename__ = "despescas_vendas"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_cultivo.id", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    tipo_despesca = Column(String(20), default="TOTAL")  # TOTAL ou DESBASTE
    gramatura_media_g = Column(Float, nullable=False)    # Gramatura aferida na balança
    camarao_colhido_kg = Column(Float, nullable=False)   # Peso líquido despescado (kg)
    comprador = Column(String(100), nullable=False)
    preco_kg_rs = Column(Float, nullable=False)          # Preço negociado por kg (R$)
    faturamento_bruto_rs = Column(Float, nullable=False) # camarao_colhido_kg * preco_kg_rs

    data_vencimento = Column(Date, nullable=True)
    status_pagamento = Column(String(20), default="A RECEBER")  # RECEBIDO, A RECEBER, EM ATRASO
    data_pagamento = Column(Date, nullable=True)
    forma_pagamento = Column(String(30), nullable=True)  # Pix, Boleto, TED, Dinheiro, Cheque
    numero_romaneio = Column(String(50), nullable=True)
    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    ciclo = relationship("CicloCultivo", back_populates="despescas")
