"""Script utilitário para iniciar o servidor backend FastAPI com Uvicorn."""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}...")
    print("Acesse a documentação interativa em: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
