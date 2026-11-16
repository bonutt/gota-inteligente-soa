from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict

from app.domain.enums import Severidade, TipoAlerta


class AlertaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    propriedade_id: int
    tipo: TipoAlerta
    severidade: Severidade
    mensagem: str
    lido: bool
    criado_em: DataHoraUTC
