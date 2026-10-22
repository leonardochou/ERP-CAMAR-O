"""Configurações centrais do sistema ERP CAMARÃO."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação ERP CAMARÃO."""

    PROJECT_NAME: str = "ERP CAMARÃO - Ceará-Mirim/RN"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Diretórios de Controle e Dados
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODELOS_DIR: Path = BASE_DIR.parent / "MODELOS DE CONTROLE"
    DB_PATH: Path = BASE_DIR / "erp_camarao.db"

    # Conexão de Banco de Dados: SQLite local por padrão para desenvolvimento e testes,
    # permitindo PostgreSQL / Supabase através de DATABASE_URL em produção.
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

    # Limites Zootécnicos e de Qualidade de Água (Conforme POP Ceará-Mirim/RN)
    O2_CRITICO_MG_L: float = 3.0
    O2_ALERTA_MG_L: float = 3.8
    O2_OTIMO_MG_L: float = 4.0
    AMONIA_CRITICA_MG_L: float = 0.1
    NITRITO_CRITICO_MG_L: float = 0.2
    DELTA_PH_ALERTA: float = 0.8
    FCA_JOVEM_ALERTA: float = 1.8

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
