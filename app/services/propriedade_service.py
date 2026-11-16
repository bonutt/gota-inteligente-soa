from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import NaoEncontrado, RegraDeNegocio
from app.domain.models import Propriedade
from app.schemas.propriedade import PropriedadeAtualizar, PropriedadeCriar
from app.services import produtor_service


def listar(db: Session, municipio: str | None = None, produtor_id: int | None = None,
           pular: int = 0, limite: int = 50) -> list[Propriedade]:
    consulta = select(Propriedade).order_by(Propriedade.id)
    if municipio:
        consulta = consulta.where(Propriedade.municipio == municipio)
    if produtor_id:
        consulta = consulta.where(Propriedade.produtor_id == produtor_id)
    return list(db.scalars(consulta.offset(pular).limit(limite)))


def obter(db: Session, propriedade_id: int) -> Propriedade:
    propriedade = db.get(Propriedade, propriedade_id)
    if not propriedade:
        raise NaoEncontrado(f"Propriedade {propriedade_id} não encontrada.")
    return propriedade


def criar(db: Session, dados: PropriedadeCriar) -> Propriedade:
    produtor_service.obter(db, dados.produtor_id)  # garante que o produtor existe
    propriedade = Propriedade(**dados.model_dump())
    db.add(propriedade)
    db.commit()
    db.refresh(propriedade)
    return propriedade


def atualizar(db: Session, propriedade_id: int, dados: PropriedadeAtualizar) -> Propriedade:
    propriedade = obter(db, propriedade_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(propriedade, campo, valor)
    if propriedade.umidade_minima_ideal >= propriedade.umidade_maxima_ideal:
        db.rollback()
        raise RegraDeNegocio("umidade_minima_ideal deve ser menor que umidade_maxima_ideal.")
    db.commit()
    db.refresh(propriedade)
    return propriedade


def remover(db: Session, propriedade_id: int) -> None:
    propriedade = obter(db, propriedade_id)
    db.delete(propriedade)
    db.commit()
