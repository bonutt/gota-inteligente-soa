from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict, Field


class DispositivoCriar(BaseModel):
    codigo: str = Field(min_length=3, max_length=40, pattern=r"^[a-z0-9\-]+$", examples=["gota-001"])
    propriedade_id: int = Field(gt=0)
    descricao: str | None = Field(default=None, max_length=200, examples=["ESP32 + sensor de solo no canteiro 1"])


class DispositivoAtualizar(BaseModel):
    descricao: str | None = Field(default=None, max_length=200)
    ativo: bool | None = None


class DispositivoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    propriedade_id: int
    descricao: str | None
    ativo: bool
    ultima_comunicacao: DataHoraUTC | None
    criado_em: DataHoraUTC
