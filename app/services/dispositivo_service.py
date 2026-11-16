from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import Conflito, NaoEncontrado
from app.domain.models import Dispositivo
from app.schemas.dispositivo import DispositivoAtualizar, DispositivoCriar
from app.services import propriedade_service


def listar(db: Session, propriedade_id: int | None = None) -> list[Dispositivo]:
    consulta = select(Dispositivo).order_by(Dispositivo.id)
    if propriedade_id:
        consulta = consulta.where(Dispositivo.propriedade_id == propriedade_id)
    return list(db.scalars(consulta))


def obter(db: Session, dispositivo_id: int) -> Dispositivo:
    dispositivo = db.get(Dispositivo, dispositivo_id)
    if not dispositivo:
        raise NaoEncontrado(f"Dispositivo {dispositivo_id} não encontrado.")
    return dispositivo


def obter_por_codigo(db: Session, codigo: str) -> Dispositivo:
    dispositivo = db.scalar(select(Dispositivo).where(Dispositivo.codigo == codigo))
    if not dispositivo:
        raise NaoEncontrado(f"Dispositivo '{codigo}' não cadastrado.")
    return dispositivo


def criar(db: Session, dados: DispositivoCriar) -> Dispositivo:
    propriedade_service.obter(db, dados.propriedade_id)
    if db.scalar(select(Dispositivo).where(Dispositivo.codigo == dados.codigo)):
        raise Conflito(f"Já existe um dispositivo com o código '{dados.codigo}'.")
    dispositivo = Dispositivo(**dados.model_dump())
    db.add(dispositivo)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def atualizar(db: Session, dispositivo_id: int, dados: DispositivoAtualizar) -> Dispositivo:
    dispositivo = obter(db, dispositivo_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(dispositivo, campo, valor)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def remover(db: Session, dispositivo_id: int) -> None:
    db.delete(obter(db, dispositivo_id))
    db.commit()
