from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PropriedadeBase(BaseModel):
    nome: str = Field(min_length=3, max_length=120, examples=["Sítio Boa Esperança"])
    municipio: str = Field(min_length=2, max_length=80, examples=["Ibiúna"])
    latitude: float = Field(ge=-90, le=90, examples=[-23.656])
    longitude: float = Field(ge=-180, le=180, examples=[-47.222])
    area_hectares: float = Field(gt=0, le=10_000, examples=[2.5])
    cultura: str = Field(min_length=2, max_length=60, examples=["Alface"])
    umidade_minima_ideal: float = Field(default=35, ge=0, le=100)
    umidade_maxima_ideal: float = Field(default=70, ge=0, le=100)

    @model_validator(mode="after")
    def _faixa_valida(self):
        if self.umidade_minima_ideal >= self.umidade_maxima_ideal:
            raise ValueError("umidade_minima_ideal deve ser menor que umidade_maxima_ideal")
        return self


class PropriedadeCriar(PropriedadeBase):
    produtor_id: int = Field(gt=0)


class PropriedadeAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    municipio: str | None = Field(default=None, min_length=2, max_length=80)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area_hectares: float | None = Field(default=None, gt=0, le=10_000)
    cultura: str | None = Field(default=None, min_length=2, max_length=60)
    umidade_minima_ideal: float | None = Field(default=None, ge=0, le=100)
    umidade_maxima_ideal: float | None = Field(default=None, ge=0, le=100)


class PropriedadeResposta(PropriedadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    produtor_id: int
    criado_em: DataHoraUTC
