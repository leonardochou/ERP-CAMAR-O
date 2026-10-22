"""Aplicação principal FastAPI do ERP CAMARÃO (Ceará-Mirim/RN)."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.init_db import init_db
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação: inicializa tabelas e seed com tolerância a falhas de rede."""
    try:
        init_db()
        print("✅ Banco de dados inicializado com sucesso e sincronizado!")
    except Exception as e:
        print(f"⚠️ Aviso: Falha temporária ao sincronizar banco remoto ({e}). O ERP iniciará normalmente.")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API RESTful de Gestão Zootécnica e Financeira para Fazenda de Camarão Marinho (Litopenaeus vannamei em Ceará-Mirim/RN).",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração de CORS para comunicação fluida com Next.js PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta as rotas da versão 1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root():
    """Redireciona para o dashboard operacional."""
    return RedirectResponse(url="/dashboard")


@app.get("/health", tags=["Health Check"])
def health():
    """Health check estruturado para monitoramento de infraestrutura."""
    return {"status": "ok"}


@app.get("/dashboard", include_in_schema=False)
def dashboard_view():
    """Serve a interface gráfica do ERP."""
    caminho_dashboard = settings.BASE_DIR.parent / "dashboard_interativo_prototipo.html"
    if caminho_dashboard.exists():
        return FileResponse(caminho_dashboard)
    caminho_alt = settings.BASE_DIR / "dashboard_interativo_prototipo.html"
    if caminho_alt.exists():
        return FileResponse(caminho_alt)
    return {"erro": "Arquivo do dashboard não encontrado."}
