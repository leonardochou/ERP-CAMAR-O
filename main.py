"""Ponto de entrada raiz para execução em nuvem (Render, Railway, etc.)."""
import os
import sys
from pathlib import Path

# Adiciona o diretório backend no path de busca do Python
base_dir = Path(__file__).resolve().parent
backend_dir = base_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
