from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import NaoEncontrado
from app.domain.models import Produtor
from app.schemas.produtor import ProdutorAtualizar, ProdutorCriar


def listar(db: Session, municipio: str | None = None, pular: int = 0, limite: int = 50) -> list[Produtor]:
    consulta = select(Produtor).order_by(Produtor.id)
    if municipio:
        consulta = consulta.where(Produtor.municipio == municipio)
    return list(db.scalars(consulta.offset(pular).limit(limite)))


def obter(db: Session, produtor_id: int) -> Produtor:
    produtor = db.get(Produtor, produtor_id)
    if not produtor:
        raise NaoEncontrado(f"Produtor {produtor_id} não encontrado.")
    return produtor


def criar(db: Session, dados: ProdutorCriar) -> Produtor:
    produtor = Produtor(**dados.model_dump())
    db.add(produtor)
    db.commit()
    db.refresh(produtor)
    return produtor


def atualizar(db: Session, produtor_id: int, dados: ProdutorAtualizar) -> Produtor:
    produtor = obter(db, produtor_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produtor, campo, valor)
    db.commit()
    db.refresh(produtor)
    return produtor


def remover(db: Session, produtor_id: int) -> None:
    produtor = obter(db, produtor_id)
    db.delete(produtor)
    db.commit()
