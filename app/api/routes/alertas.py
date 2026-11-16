from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.enums import Severidade
from app.schemas.alerta import AlertaResposta
from app.services import alerta_service

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("", response_model=list[AlertaResposta], summary="Alertas (app do agricultor e painel)")
def listar(propriedade_id: int | None = None, lido: bool | None = None, severidade: Severidade | None = None,
           limite: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return alerta_service.listar(db, propriedade_id, lido, severidade, limite)


@router.patch("/{alerta_id}/lido", response_model=AlertaResposta, summary="Marca alerta como lido")
def marcar_lido(alerta_id: int, db: Session = Depends(get_db)):
    return alerta_service.marcar_como_lido(db, alerta_id)
