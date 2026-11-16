from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.leitura import LeituraCriar, LeituraProcessada, LeituraResposta
from app.services import telemetria_service

router = APIRouter(prefix="/leituras", tags=["Leituras (telemetria)"])


@router.post("", response_model=LeituraProcessada, status_code=status.HTTP_201_CREATED,
             summary="ESP32 envia leitura e recebe a decisão da bomba")
def registrar(dados: LeituraCriar, db: Session = Depends(get_db)):
    """Salva a leitura, calcula o índice de estresse hídrico, decide se a bomba
    deve ser ligada (cruzando solo + previsão de chuva) e gera alertas."""
    return telemetria_service.processar_leitura(db, dados)


@router.get("", response_model=list[LeituraResposta], summary="Histórico de leituras")
def listar(dispositivo_id: int | None = None, propriedade_id: int | None = None,
           limite: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return telemetria_service.listar_leituras(db, dispositivo_id, propriedade_id, limite)
