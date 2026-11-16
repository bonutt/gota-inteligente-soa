from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict, Field


class ProdutorBase(BaseModel):
    nome: str = Field(min_length=3, max_length=120, examples=["Maria Aparecida"])
    telefone: str | None = Field(default=None, max_length=20, examples=["(15) 99999-0000"])
    municipio: str = Field(min_length=2, max_length=80, examples=["Ibiúna"])
    uf: str = Field(min_length=2, max_length=2, pattern="^[A-Z]{2}$", examples=["SP"])


class ProdutorCriar(ProdutorBase):
    pass


class ProdutorAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    telefone: str | None = Field(default=None, max_length=20)
    municipio: str | None = Field(default=None, min_length=2, max_length=80)
    uf: str | None = Field(default=None, pattern="^[A-Z]{2}$")


class ProdutorResposta(ProdutorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: DataHoraUTC
