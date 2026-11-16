from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import NaoEncontrado
from app.domain.models import LeituraSensor, Recomendacao
from app.schemas.recomendacao import RecomendacaoCriar
from app.services import propriedade_service


def criar(db: Session, dados: RecomendacaoCriar) -> Recomendacao:
    propriedade_service.obter(db, dados.propriedade_id)
    if dados.leitura_id and not db.get(LeituraSensor, dados.leitura_id):
        raise NaoEncontrado(f"Leitura {dados.leitura_id} não encontrada.")
    recomendacao = Recomendacao(**dados.model_dump())
    db.add(recomendacao)
    db.commit()
    db.refresh(recomendacao)
    return recomendacao


def listar(db: Session, propriedade_id: int | None = None, limite: int = 50) -> list[Recomendacao]:
    consulta = select(Recomendacao).order_by(Recomendacao.criada_em.desc(), Recomendacao.id.desc())
    if propriedade_id:
        consulta = consulta.where(Recomendacao.propriedade_id == propriedade_id)
    return list(db.scalars(consulta.limit(limite)))


def ultima(db: Session, propriedade_id: int) -> Recomendacao:
    propriedade_service.obter(db, propriedade_id)
    recomendacao = db.scalar(
        select(Recomendacao)
        .where(Recomendacao.propriedade_id == propriedade_id)
        .order_by(Recomendacao.criada_em.desc(), Recomendacao.id.desc())
        .limit(1)
    )
    if not recomendacao:
        raise NaoEncontrado(f"Nenhuma recomendação para a propriedade {propriedade_id}.")
    return recomendacao
