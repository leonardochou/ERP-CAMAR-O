"""Script utilitário para gerar o arquivo SQL compatível com PostgreSQL / Supabase."""
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
backend_dir = base_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
import app.models
from app.core.database import Base

ddl = [
    "-- =========================================================",
    "-- SCHEMA DDL OFICIAL - ERP CAMARÃO (Ceará-Mirim/RN)",
    "-- Compatibilidade Total: PostgreSQL 14+ / Supabase",
    "-- Tabelas Zootécnicas, Operacionais, Multi-Tenant e Contabilidade",
    "-- Idempotente: seguro para rodar em base nova ou já existente",
    "-- =========================================================\n",
    "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
    "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";\n",
]

for table in Base.metadata.sorted_tables:
    stmt = str(CreateTable(table).compile(dialect=postgresql.dialect())).strip()
    stmt = stmt.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
    ddl.append(f"-- Tabela: {table.name}")
    ddl.append(stmt + ";\n")

sql_path = base_dir / "supabase_schema.sql"
with open(sql_path, "w", encoding="utf-8") as f:
    f.write("\n".join(ddl))

print(f"Sucesso! {len(Base.metadata.sorted_tables)} tabelas exportadas para {sql_path.name}")
