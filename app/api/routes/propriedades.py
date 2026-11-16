from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.propriedade import PropriedadeAtualizar, PropriedadeCriar, PropriedadeResposta
from app.services import propriedade_service

router = APIRouter(prefix="/propriedades", tags=["Propriedades"])


@router.get("", response_model=list[PropriedadeResposta], summary="Lista propriedades")
def listar(municipio: str | None = None, produtor_id: int | None = None,
           pular: int = Query(0, ge=0), limite: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return propriedade_service.listar(db, municipio, produtor_id, pular, limite)


@router.get("/{propriedade_id}", response_model=PropriedadeResposta, summary="Busca uma propriedade")
def obter(propriedade_id: int, db: Session = Depends(get_db)):
    return propriedade_service.obter(db, propriedade_id)


@router.post("", response_model=PropriedadeResposta, status_code=status.HTTP_201_CREATED,
             summary="Cadastra propriedade")
def criar(dados: PropriedadeCriar, db: Session = Depends(get_db)):
    return propriedade_service.criar(db, dados)


@router.put("/{propriedade_id}", response_model=PropriedadeResposta, summary="Atualiza propriedade")
def atualizar(propriedade_id: int, dados: PropriedadeAtualizar, db: Session = Depends(get_db)):
    return propriedade_service.atualizar(db, propriedade_id, dados)


@router.delete("/{propriedade_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove propriedade")
def remover(propriedade_id: int, db: Session = Depends(get_db)):
    propriedade_service.remover(db, propriedade_id)
