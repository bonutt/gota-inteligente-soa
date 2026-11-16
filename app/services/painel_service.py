"""Visão regional para o Sindicato Rural / Prefeitura (consumida pelo painel C# WinForms)."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.domain import regras
from app.domain.enums import AcaoIrrigacao, NivelEstresse
from app.domain.models import Alerta, Dispositivo, LeituraSensor, Propriedade, Recomendacao


def montar_painel(db: Session, municipio: str | None = None) -> dict:
    consulta = select(Propriedade).options(joinedload(Propriedade.produtor)).order_by(Propriedade.id)
    if municipio:
        consulta = consulta.where(Propriedade.municipio == municipio)
    propriedades = list(db.scalars(consulta))

    situacoes = []
    irrigacoes_evitadas = 0
    litros = 0.0
    for prop in propriedades:
        leitura = db.scalar(
            select(LeituraSensor).join(Dispositivo)
            .where(Dispositivo.propriedade_id == prop.id)
            .order_by(LeituraSensor.registrada_em.desc(), LeituraSensor.id.desc()).limit(1)
        )
        ultima_rec = db.scalar(
            select(Recomendacao).where(Recomendacao.propriedade_id == prop.id)
            .order_by(Recomendacao.criada_em.desc(), Recomendacao.id.desc()).limit(1)
        )
        nao_lidos = db.scalar(
            select(func.count(Alerta.id)).where(Alerta.propriedade_id == prop.id, Alerta.lido.is_(False))
        ) or 0
        evitadas = db.scalar(
            select(func.count(Recomendacao.id)).where(
                Recomendacao.propriedade_id == prop.id,
                Recomendacao.acao == AcaoIrrigacao.AGUARDAR_CHUVA,
            )
        ) or 0
        irrigacoes_evitadas += evitadas
        litros += evitadas * regras.litros_por_irrigacao(prop.area_hectares)

        indice = leitura.indice_estresse if leitura else None
        situacoes.append({
            "propriedade_id": prop.id,
            "propriedade": prop.nome,
            "produtor": prop.produtor.nome,
            "municipio": prop.municipio,
            "cultura": prop.cultura,
            "area_hectares": prop.area_hectares,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
            "umidade_solo": leitura.umidade_solo if leitura else None,
            "temperatura_ar": leitura.temperatura_ar if leitura else None,
            "probabilidade_chuva": leitura.probabilidade_chuva if leitura else None,
            "indice_estresse": indice,
            "nivel_estresse": regras.classificar_estresse(indice),
            "ultima_acao": ultima_rec.acao.value if ultima_rec else None,
            "ultima_leitura_em": leitura.registrada_em if leitura else None,
            "alertas_nao_lidos": nao_lidos,
        })

    # Ordena da mais crítica para a menos crítica (sem dados por último)
    situacoes.sort(key=lambda s: -1 if s["indice_estresse"] is None else s["indice_estresse"], reverse=True)

    def contar(nivel: NivelEstresse) -> int:
        return sum(1 for s in situacoes if s["nivel_estresse"] == nivel)

    indices = [s["indice_estresse"] for s in situacoes if s["indice_estresse"] is not None]
    resumo = {
        "municipio": municipio,
        "total_propriedades": len(situacoes),
        "propriedades_criticas": contar(NivelEstresse.CRITICO),
        "propriedades_atencao": contar(NivelEstresse.ATENCAO),
        "propriedades_normais": contar(NivelEstresse.NORMAL),
        "propriedades_sem_dados": contar(NivelEstresse.SEM_DADOS),
        "indice_medio_estresse": round(sum(indices) / len(indices), 1) if indices else None,
        "irrigacoes_evitadas": irrigacoes_evitadas,
        "litros_economizados_estimados": round(litros, 1),
    }
    return {"resumo": resumo, "propriedades": situacoes}
