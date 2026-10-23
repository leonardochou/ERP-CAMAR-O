"""Modelos de banco de dados ORM do ERP CAMARÃO."""
from app.core.database import Base
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.despesca import DespescaVenda
from app.models.auditoria import AuditoriaPendencia
from app.models.funcionario import Funcionario, EscalaTrabalho
from app.models.contabilidade import LancamentoContabil, LogBackupContabil

__all__ = [
    "Base",
    "Fazenda",
    "Viveiro",
    "CicloCultivo",
    "LancamentoAlimentacao",
    "MonitoramentoAgua",
    "Biometria",
    "DespescaVenda",
    "AuditoriaPendencia",
    "Funcionario",
    "EscalaTrabalho",
    "LancamentoContabil",
    "LogBackupContabil",
]
