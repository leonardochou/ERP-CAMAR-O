"""Modelos ORM para o Módulo de Contabilidade, DRE, Fluxo de Caixa, Anti-Redundância e Backups."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from app.core.database import Base


class LancamentoContabil(Base):
    """Representa um lançamento no Livro Diário Contábil (Entrada ou Saída) com Duplo Regime e Chave Anti-Redundância."""
    __tablename__ = "lancamentos_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)

    # Datas para Duplo Regime Contábil
    data_competencia = Column(Date, nullable=False, index=True)  # Emissão / Competência (base da DRE)
    data_vencimento = Column(Date, nullable=False, index=True)   # Vencimento (base da Projeção de Caixa)
    data_liquidacao = Column(Date, nullable=True, index=True)    # Pagamento / Recebimento efetivo (base do Caixa Realizado)

    # Classificação no Plano de Contas Hierárquico
    tipo_movimento = Column(String(15), nullable=False, default="SAIDA")  # ENTRADA ou SAIDA
    codigo_conta = Column(String(20), nullable=False, index=True)         # Ex: '3.1.01'
    nome_conta = Column(String(120), nullable=False)                      # Ex: '3.1.01 - Ração e Nutrição'
    grupo_contabil = Column(String(50), nullable=False, index=True)       # RECEITA_BRUTA, DEDUCOES, CUSTO_VARIAVEL, DESPESA_FIXA, RESULTADO_FINANCEIRO, CAPEX

    # Detalhes do Documento / Histórico
    descricao = Column(String(255), nullable=False)
    fornecedor_cliente = Column(String(120), nullable=False, index=True)
    valor_rs = Column(Float, nullable=False)
    status_pagamento = Column(String(20), nullable=False, default="PENDENTE")  # PAGO ou PENDENTE
    forma_pagamento = Column(String(40), nullable=True, default="Boleto Bancário")

    # Alocação Opcional por Viveiro (sob controle do usuário: 'Geral da Fazenda' ou 'V-01'..'V-15')
    centro_custo_viveiro = Column(String(30), nullable=False, default="Geral da Fazenda", index=True)

    # Rastreabilidade GED e Bloqueio Estrito Anti-Redundância
    arquivo_nota = Column(String(180), nullable=True)
    origem = Column(String(30), nullable=False, default="PLANILHA_EXCEL")  # PLANILHA_EXCEL, GED_DRIVE_IA, MANUAL_ERP
    chave_dedup = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256(Fazenda|Fornecedor|Vencimento|Valor)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LogBackupContabil(Base):
    """Registra o histórico de backups diários da planilha e lotes sincronizados com bloqueio de duplicatas."""
    __tablename__ = "logs_backups_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(String(36), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_operacao = Column(String(40), nullable=False, default="SYNC_E_BACKUP_DIARIO")
    arquivo_backup = Column(String(200), nullable=True)
    novos_lancamentos = Column(Integer, default=0)
    atualizacoes_status = Column(Integer, default=0)
    duplicatas_bloqueadas = Column(Integer, default=0)
    detalhes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
