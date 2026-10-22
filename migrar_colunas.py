"""Script de migração de colunas topográficas no SQLite."""
import sqlite3
from pathlib import Path

novas_colunas = [
    ("nome_pai", "TEXT"),
    ("numero_pai", "INTEGER"),
    ("area_satelite_m2", "REAL"),
    ("area_ajustada_m2", "REAL"),
    ("origem_metragem", "TEXT DEFAULT 'SATELITE_GOOGLE_MAPS'")
]

paths = [
    Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\backend\erp_camarao.db"),
    Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\erp_camarao.db")
]

for p in paths:
    if p.exists():
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(viveiros)")
        cols = [r[1] for r in cur.fetchall()]
        print(f"Banco: {p.name} - Colunas existentes: {len(cols)}")
        for col_name, col_type in novas_colunas:
            if col_name not in cols:
                cur.execute(f"ALTER TABLE viveiros ADD COLUMN {col_name} {col_type}")
                print(f"  + Adicionada coluna: {col_name}")
        conn.commit()
        conn.close()

print("Migração concluída!")
