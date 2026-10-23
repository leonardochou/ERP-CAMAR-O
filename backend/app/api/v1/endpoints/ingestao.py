"""Endpoints REST para Ingestão e Sincronização de Planilhas Excel com o ERP CAMARÃO."""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.services.ingestor_service import IngestorService

router = APIRouter()

# Diretório padrão onde residem os modelos oficiais na nuvem/disco
DIRETORIO_MODELOS_LOCAL = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\MODELOS DE CONTROLE")


@router.post("/sincronizar-modelos", summary="Sincronizar automaticamente as planilhas do Google Drive")
def sincronizar_modelos_drive(
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Varre as pastas de 'MODELOS DE CONTROLE', processa e reconcilia os dados no banco relacional."""
    caminho_alimentacao = (
        DIRETORIO_MODELOS_LOCAL / "Controle de alimentação e biometria" / "Controle_Alimentacao_e_Biometria.xlsx"
    )
    caminho_agua = (
        DIRETORIO_MODELOS_LOCAL / "Controle de qualidade de agua" / "Controle_Qualidade_Agua.xlsx"
    )
    caminho_contabil = (
        DIRETORIO_MODELOS_LOCAL / "Registro de custos e contas" / "Registro_de_Custos_e_Contas.xlsx"
    )

    resultados = {
        "status": "sucesso",
        "fazenda_codigo": fazenda.codigo,
        "fazenda_nome": fazenda.nome,
        "arquivos_processados": {}
    }

    if caminho_alimentacao.exists():
        res_ali = IngestorService.processar_planilha_alimentacao(
            db=db,
            arquivo_ou_caminho=caminho_alimentacao,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )
        resultados["arquivos_processados"]["alimentacao"] = res_ali
    else:
        resultados["arquivos_processados"]["alimentacao"] = {
            "status": "erro",
            "detalhes": f"Arquivo não encontrado em {caminho_alimentacao}"
        }

    if caminho_agua.exists():
        res_agu = IngestorService.processar_planilha_agua(
            db=db,
            arquivo_ou_caminho=caminho_agua,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )
        resultados["arquivos_processados"]["qualidade_agua"] = res_agu
    else:
        resultados["arquivos_processados"]["qualidade_agua"] = {
            "status": "erro",
            "detalhes": f"Arquivo não encontrado em {caminho_agua}"
        }

    if caminho_contabil.exists():
        res_cont = IngestorService.processar_planilha_contabil(
            db=db,
            arquivo_ou_caminho=caminho_contabil,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )
        resultados["arquivos_processados"]["contabilidade"] = res_cont
    else:
        resultados["arquivos_processados"]["contabilidade"] = {
            "status": "erro",
            "detalhes": f"Arquivo não encontrado em {caminho_contabil}"
        }

    return resultados


@router.post("/upload-alimentacao", summary="Upload manual de planilha de Alimentação e Biometria (.xlsx)")
async def upload_planilha_alimentacao(
    file: UploadFile = File(...),
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Permite ao usuário subir uma planilha .xlsx diretamente via browser e rodar a ingestão e auditoria."""
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo inválido. Apenas planilhas Excel (.xlsx) são aceitas."
        )

    conteudo = await file.read()
    try:
        resultado = IngestorService.processar_planilha_alimentacao(
            db=db,
            arquivo_ou_caminho=conteudo,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )
        return {
            "status": "sucesso",
            "arquivo": file.filename,
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar planilha: {str(e)}"
        )


@router.post("/upload-agua", summary="Upload manual de planilha de Qualidade da Água (.xlsx)")
async def upload_planilha_agua(
    file: UploadFile = File(...),
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Permite ao usuário subir uma planilha de qualidade da água e atualizar os parâmetros zootécnicos."""
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo inválido. Apenas planilhas Excel (.xlsx) são aceitas."
        )

    conteudo = await file.read()
    try:
        resultado = IngestorService.processar_planilha_agua(
            db=db,
            arquivo_ou_caminho=conteudo,
            fazenda_id=fazenda.id,
            fazenda_codigo=fazenda.codigo
        )
        return {
            "status": "sucesso",
            "arquivo": file.filename,
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar planilha: {str(e)}"
        )
