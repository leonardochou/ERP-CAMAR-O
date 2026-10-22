"""Gerenciador de contexto Multi-Tenant e injeção de dependência da Fazenda ativa."""
from typing import Optional
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.fazenda import Fazenda

# Identificadores determinísticos das fazendas padrão
FAZENDA_PADRAO_CODIGO = "FAZ_ARRENDADA"
FAZENDA_PADRAO_ID = "11111111-1111-1111-1111-111111111111"
FAZENDA_HAKKA_CODIGO = "FAZ_HAKKA"
FAZENDA_HAKKA_ID = "22222222-2222-2222-2222-222222222222"


def get_current_fazenda(
    x_fazenda_id: Optional[str] = Header(None, alias="X-Fazenda-Id"),
    db: Session = Depends(get_db)
) -> Fazenda:
    """Dependency FastAPI para extrair a fazenda ativa via Header 'X-Fazenda-Id' com fallback para FAZ_ARRENDADA."""
    if x_fazenda_id:
        # Permite passar tanto o UUID quanto o código amigável (ex: FAZ_ARRENDADA, FAZ_HAKKA)
        fazenda = db.query(Fazenda).filter(
            (Fazenda.id == x_fazenda_id) | (Fazenda.codigo == x_fazenda_id)
        ).first()

        if not fazenda:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fazenda identificada por '{x_fazenda_id}' não foi encontrada no sistema."
            )
        return fazenda

    # Fallback automático para a Fazenda Arrendada padrão
    fazenda_padrao = db.query(Fazenda).filter(Fazenda.codigo == FAZENDA_PADRAO_CODIGO).first()
    if not fazenda_padrao:
        # Se porventura o seed ainda não tiver sido executado, tenta a primeira existente
        fazenda_padrao = db.query(Fazenda).first()
        if not fazenda_padrao:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Nenhuma fazenda configurada na base de dados. Execute a rotina de inicialização."
            )

    return fazenda_padrao
