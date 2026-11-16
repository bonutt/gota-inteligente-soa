"""Regras de negócio da irrigação (funções puras, sem banco e sem HTTP).

Ficam isoladas aqui para serem fáceis de testar e de explicar:
- índice de estresse hídrico (0 a 100)
- decisão de irrigar, não irrigar ou aguardar a chuva
- estimativa de água economizada
"""
from dataclasses import dataclass

from app.core.config import settings
from app.domain.enums import AcaoIrrigacao, NivelEstresse


@dataclass(frozen=True)
class Decisao:
    acao: AcaoIrrigacao
    motivo: str


def _limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def calcular_indice_estresse(
    umidade_solo: float,
    temperatura_ar: float,
    umidade_ar: float,
    umidade_maxima_ideal: float,
) -> int:
    """Índice de 0 (sem estresse) a 100 (estresse máximo).

    Pesos:
      70% falta de água no solo em relação ao ideal da cultura
      20% calor (acima de 25 °C, saturando em 40 °C)
      10% ar seco (abaixo de 60% de umidade relativa)
    """
    deficit_solo = _limitar((umidade_maxima_ideal - umidade_solo) / umidade_maxima_ideal, 0, 1)
    calor = _limitar((temperatura_ar - 25) / 15, 0, 1)
    ar_seco = _limitar((60 - umidade_ar) / 60, 0, 1)
    return round(deficit_solo * 70 + calor * 20 + ar_seco * 10)


def classificar_estresse(indice: int | None) -> NivelEstresse:
    if indice is None:
        return NivelEstresse.SEM_DADOS
    if indice >= 70:
        return NivelEstresse.CRITICO
    if indice >= 40:
        return NivelEstresse.ATENCAO
    return NivelEstresse.NORMAL


def decidir_irrigacao(
    umidade_solo: float,
    temperatura_ar: float,
    umidade_ar: float,
    probabilidade_chuva: float,
    umidade_minima_ideal: float,
    umidade_maxima_ideal: float,
) -> Decisao:
    """Cruza o solo com a previsão do tempo para decidir se liga a bomba."""
    chuva_alta = probabilidade_chuva >= settings.limite_chuva_alta
    critico = settings.umidade_solo_critica

    if umidade_solo >= umidade_maxima_ideal:
        return Decisao(
            AcaoIrrigacao.NAO_IRRIGAR,
            f"Solo com {umidade_solo:.0f}% de umidade, acima do ideal ({umidade_maxima_ideal:.0f}%). Não é preciso irrigar.",
        )

    if umidade_solo < umidade_minima_ideal:
        if chuva_alta and umidade_solo >= critico:
            return Decisao(
                AcaoIrrigacao.AGUARDAR_CHUVA,
                f"Solo seco ({umidade_solo:.0f}%), mas há {probabilidade_chuva:.0f}% de chance de chuva. "
                "Bomba desligada para economizar água e energia.",
            )
        if chuva_alta:
            return Decisao(
                AcaoIrrigacao.IRRIGAR,
                f"Solo em nível crítico ({umidade_solo:.0f}%). Mesmo com {probabilidade_chuva:.0f}% de chance de chuva, "
                "irrigar agora para não perder a plantação.",
            )
        return Decisao(
            AcaoIrrigacao.IRRIGAR,
            f"Solo seco ({umidade_solo:.0f}%) e baixa chance de chuva ({probabilidade_chuva:.0f}%). Ligar a bomba.",
        )

    # Solo dentro da faixa ideal
    if chuva_alta:
        return Decisao(
            AcaoIrrigacao.NAO_IRRIGAR,
            f"Solo na faixa ideal ({umidade_solo:.0f}%) e {probabilidade_chuva:.0f}% de chance de chuva. Não irrigar.",
        )
    perto_do_minimo = umidade_solo < umidade_minima_ideal + 10
    if perto_do_minimo and temperatura_ar >= 32 and umidade_ar < 40:
        return Decisao(
            AcaoIrrigacao.IRRIGAR,
            f"Solo perto do mínimo ({umidade_solo:.0f}%) com calor de {temperatura_ar:.0f} °C e ar seco "
            f"({umidade_ar:.0f}%). Irrigação preventiva.",
        )
    return Decisao(
        AcaoIrrigacao.NAO_IRRIGAR,
        f"Solo na faixa ideal ({umidade_solo:.0f}%). Nenhuma ação necessária.",
    )


def litros_por_irrigacao(area_hectares: float) -> float:
    """Água usada numa irrigação: área (m²) × lâmina (m) × 1000 L/m³."""
    return area_hectares * 10_000 * (settings.lamina_irrigacao_mm / 1000) * 1000
