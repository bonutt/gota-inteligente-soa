from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alerta import AlertaResposta
from app.schemas.recomendacao import RecomendacaoResposta


class LeituraCriar(BaseModel):
    """Corpo enviado pelo ESP32 a cada ciclo de leitura."""

    codigo_dispositivo: str = Field(min_length=3, max_length=40, examples=["gota-001"])
    umidade_solo: float = Field(ge=0, le=100, examples=[22.5])
    temperatura_ar: float = Field(ge=-20, le=60, examples=[31.0])
    umidade_ar: float = Field(ge=0, le=100, examples=[45.0])
    probabilidade_chuva: float = Field(ge=0, le=100, examples=[90.0])
    bomba_ligada: bool = Field(default=False)


class LeituraResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    dispositivo_id: int
    umidade_solo: float
    temperatura_ar: float
    umidade_ar: float
    probabilidade_chuva: float
    bomba_ligada: bool
    indice_estresse: int | None
    registrada_em: DataHoraUTC


class LeituraProcessada(BaseModel):
    """Resposta para o ESP32: a leitura salva + o que fazer com a bomba."""

    leitura: LeituraResposta
    nivel_estresse: str
    recomendacao: RecomendacaoResposta
    ligar_bomba: bool
    alertas_gerados: list[AlertaResposta]
