from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.produtor import ProdutorAtualizar, ProdutorCriar, ProdutorResposta
from app.services import produtor_service

router = APIRouter(prefix="/produtores", tags=["Produtores"])


@router.get("", response_model=list[ProdutorResposta], summary="Lista produtores")
def listar(municipio: str | None = None, pular: int = Query(0, ge=0), limite: int = Query(50, ge=1, le=200),
           db: Session = Depends(get_db)):
    return produtor_service.listar(db, municipio, pular, limite)


@router.get("/{produtor_id}", response_model=ProdutorResposta, summary="Busca um produtor")
def obter(produtor_id: int, db: Session = Depends(get_db)):
    return produtor_service.obter(db, produtor_id)


@router.post("", response_model=ProdutorResposta, status_code=status.HTTP_201_CREATED, summary="Cadastra produtor")
def criar(dados: ProdutorCriar, db: Session = Depends(get_db)):
    return produtor_service.criar(db, dados)


@router.put("/{produtor_id}", response_model=ProdutorResposta, summary="Atualiza produtor")
def atualizar(produtor_id: int, dados: ProdutorAtualizar, db: Session = Depends(get_db)):
    return produtor_service.atualizar(db, produtor_id, dados)


@router.delete("/{produtor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove produtor")
def remover(produtor_id: int, db: Session = Depends(get_db)):
    produtor_service.remover(db, produtor_id)
