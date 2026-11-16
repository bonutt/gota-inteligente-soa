from app.schemas.tipos import DataHoraUTC

from pydantic import BaseModel

from app.domain.enums import NivelEstresse


class SituacaoPropriedade(BaseModel):
    propriedade_id: int
    propriedade: str
    produtor: str
    municipio: str
    cultura: str
    area_hectares: float
    latitude: float
    longitude: float
    umidade_solo: float | None
    temperatura_ar: float | None
    probabilidade_chuva: float | None
    indice_estresse: int | None
    nivel_estresse: NivelEstresse
    ultima_acao: str | None
    ultima_leitura_em: DataHoraUTC | None
    alertas_nao_lidos: int


class ResumoRegional(BaseModel):
    municipio: str | None
    total_propriedades: int
    propriedades_criticas: int
    propriedades_atencao: int
    propriedades_normais: int
    propriedades_sem_dados: int
    indice_medio_estresse: float | None
    irrigacoes_evitadas: int
    litros_economizados_estimados: float


class PainelEstresseHidrico(BaseModel):
    resumo: ResumoRegional
    propriedades: list[SituacaoPropriedade]
