from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dispositivo import DispositivoAtualizar, DispositivoCriar, DispositivoResposta
from app.services import dispositivo_service

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos (ESP32)"])


@router.get("", response_model=list[DispositivoResposta], summary="Lista dispositivos")
def listar(propriedade_id: int | None = None, db: Session = Depends(get_db)):
    return dispositivo_service.listar(db, propriedade_id)


@router.get("/{dispositivo_id}", response_model=DispositivoResposta, summary="Busca um dispositivo")
def obter(dispositivo_id: int, db: Session = Depends(get_db)):
    return dispositivo_service.obter(db, dispositivo_id)


@router.post("", response_model=DispositivoResposta, status_code=status.HTTP_201_CREATED,
             summary="Cadastra um kit ESP32 numa propriedade")
def criar(dados: DispositivoCriar, db: Session = Depends(get_db)):
    return dispositivo_service.criar(db, dados)


@router.patch("/{dispositivo_id}", response_model=DispositivoResposta, summary="Ativa/desativa ou edita")
def atualizar(dispositivo_id: int, dados: DispositivoAtualizar, db: Session = Depends(get_db)):
    return dispositivo_service.atualizar(db, dispositivo_id, dados)


@router.delete("/{dispositivo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove dispositivo")
def remover(dispositivo_id: int, db: Session = Depends(get_db)):
    dispositivo_service.remover(db, dispositivo_id)
