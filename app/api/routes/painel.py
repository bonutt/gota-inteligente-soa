from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.painel import PainelEstresseHidrico
from app.services import painel_service

router = APIRouter(prefix="/painel", tags=["Painel regional (C# WinForms)"])


@router.get("/estresse-hidrico", response_model=PainelEstresseHidrico,
            summary="Estresse hídrico das propriedades da região")
def estresse_hidrico(municipio: str | None = None, db: Session = Depends(get_db)):
    """Consumido pelo painel do Sindicato Rural / Prefeitura: situação de cada
    propriedade (da mais crítica para a menos crítica) e indicadores da região."""
    return painel_service.montar_painel(db, municipio)
