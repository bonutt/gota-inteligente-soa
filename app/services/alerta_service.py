from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import NaoEncontrado
from app.domain.enums import Severidade
from app.domain.models import Alerta


def listar(db: Session, propriedade_id: int | None = None, lido: bool | None = None,
           severidade: Severidade | None = None, limite: int = 50) -> list[Alerta]:
    consulta = select(Alerta).order_by(Alerta.criado_em.desc(), Alerta.id.desc())
    if propriedade_id:
        consulta = consulta.where(Alerta.propriedade_id == propriedade_id)
    if lido is not None:
        consulta = consulta.where(Alerta.lido == lido)
    if severidade:
        consulta = consulta.where(Alerta.severidade == severidade)
    return list(db.scalars(consulta.limit(limite)))


def marcar_como_lido(db: Session, alerta_id: int) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if not alerta:
        raise NaoEncontrado(f"Alerta {alerta_id} não encontrado.")
    alerta.lido = True
    db.commit()
    db.refresh(alerta)
    return alerta
