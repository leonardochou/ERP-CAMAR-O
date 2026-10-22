"""Modelo de dados para Gestão de Funcionários, Vigia Noturno e Escalas de Trabalho."""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date

from app.models.base import Base


class Funcionario(Base):
    """Cadastro de colaboradores da fazenda (arraçoadores, vigias, operadores)."""
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id"), nullable=False, index=True)

    nome = Column(String(100), nullable=False)
    apelido = Column(String(50), nullable=True)  # Nome de campo (ex: 'Zé do Motor', 'Carlinhos')
    cargo = Column(String(50), nullable=False)   # Vigia Noturno, Arraçoador, Operador de Máquinas, etc.
    telefone = Column(String(30), nullable=True)
    whatsapp = Column(String(30), nullable=True)
    chave_pix = Column(String(100), nullable=True)  # Chave PIX para pagamentos

    # Dados de Remuneração e Contrato
    tipo_contrato = Column(String(20), default="MENSALISTA")  # MENSALISTA ou DIARISTA
    salario_base_mensal = Column(Float, default=0.0)         # Salário fixo mensal em R$
    valor_diaria_extra = Column(Float, default=0.0)          # Valor em R$ por diária ou plantão noturno extra
    encargos_estimados_pct = Column(Float, default=0.0)      # % de encargos/ajuda de custo estimada

    ativo = Column(Boolean, default=True)
    data_admissao = Column(Date, default=date.today)
    observacoes = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    fazenda = relationship("Fazenda", backref="funcionarios")
    escalas = relationship("EscalaTrabalho", back_populates="funcionario", cascade="all, delete-orphan")


class EscalaTrabalho(Base):
    """Mapeamento diário de horários, turnos, folgas, faltas e diárias extras de cada colaborador."""
    __tablename__ = "escalas_trabalho"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id"), nullable=False, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False, index=True)

    data = Column(Date, nullable=False, index=True)
    turno = Column(String(30), nullable=False, default="DIURNO")
    # Valores de turno: 'DIURNO', 'NOTURNO_VIGIA', 'FOLGA', 'FALTA_JUSTIFICADA', 'FALTA_INJUSTIFICADA', 'FERIAS'

    # Extras e Diárias Cumpridas
    eh_extra = Column(Boolean, default=False)                # Se foi plantão/diária extra além do normal
    valor_diaria_aplicado = Column(Float, default=0.0)      # Valor financeiro da diária/extra em R$

    # Horários e Presença
    check_in_hora = Column(String(10), nullable=True)       # ex: '21:00'
    check_out_hora = Column(String(10), nullable=True)      # ex: '06:00'
    status_presenca = Column(String(20), default="AGENDADO") # 'AGENDADO', 'CONFIRMADO', 'FALTOU'

    # Ocorrências e Observações do Dia
    categoria_ocorrencia = Column(String(30), default="NORMAL")
    # 'NORMAL', 'COBERTURA_TURNO', 'ATRASO', 'ATESTADO', 'MANUTENCAO_EMERGENCIAL', 'OUTRO'
    observacoes = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    funcionario = relationship("Funcionario", back_populates="escalas")
