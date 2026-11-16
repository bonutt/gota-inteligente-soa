from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import AcaoIrrigacao, OrigemRecomendacao


class RecomendacaoCriar(BaseModel):
    """Usado pelo modelo de IA (Python) ou pelo técnico para registrar uma decisão."""

    propriedade_id: int = Field(gt=0)
    acao: AcaoIrrigacao
    origem: OrigemRecomendacao = OrigemRecomendacao.IA
    motivo: str = Field(min_length=5, max_length=1000,
                        examples=["Modelo prevê 90% de chuva em 2h; não ligar a bomba."])
    confianca: float | None = Field(default=None, ge=0, le=1, examples=[0.87])
    leitura_id: int | None = Field(default=None, gt=0)


class RecomendacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    propriedade_id: int
    leitura_id: int | None
    acao: AcaoIrrigacao
    origem: OrigemRecomendacao
    motivo: str
    confianca: float | None
    criada_em: DataHoraUTC
