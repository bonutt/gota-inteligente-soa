from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recomendacao import RecomendacaoCriar, RecomendacaoResposta
from app.services import recomendacao_service

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.post("", response_model=RecomendacaoResposta, status_code=status.HTTP_201_CREATED,
             summary="Registra decisão vinda da IA (Python) ou manual")
def criar(dados: RecomendacaoCriar, db: Session = Depends(get_db)):
    return recomendacao_service.criar(db, dados)


@router.get("", response_model=list[RecomendacaoResposta], summary="Histórico de recomendações")
def listar(propriedade_id: int | None = None, limite: int = Query(50, ge=1, le=500),
           db: Session = Depends(get_db)):
    return recomendacao_service.listar(db, propriedade_id, limite)


@router.get("/ultima/{propriedade_id}", response_model=RecomendacaoResposta,
            summary="Última recomendação da propriedade (usada pelo app e pelo ESP32)")
def ultima(propriedade_id: int, db: Session = Depends(get_db)):
    return recomendacao_service.ultima(db, propriedade_id)
