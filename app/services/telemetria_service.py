"""Caso de uso principal: o ESP32 envia uma leitura e recebe a decisão da bomba."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excecoes import RegraDeNegocio
from app.domain import regras
from app.domain.enums import AcaoIrrigacao, NivelEstresse, OrigemRecomendacao, Severidade, TipoAlerta
from app.domain.models import Alerta, LeituraSensor, Recomendacao
from app.schemas.leitura import LeituraCriar
from app.services import dispositivo_service


def processar_leitura(db: Session, dados: LeituraCriar) -> dict:
    dispositivo = dispositivo_service.obter_por_codigo(db, dados.codigo_dispositivo)
    if not dispositivo.ativo:
        raise RegraDeNegocio(f"Dispositivo '{dispositivo.codigo}' está desativado.")
    propriedade = dispositivo.propriedade

    indice = regras.calcular_indice_estresse(
        dados.umidade_solo, dados.temperatura_ar, dados.umidade_ar, propriedade.umidade_maxima_ideal
    )
    nivel = regras.classificar_estresse(indice)
    decisao = regras.decidir_irrigacao(
        dados.umidade_solo, dados.temperatura_ar, dados.umidade_ar, dados.probabilidade_chuva,
        propriedade.umidade_minima_ideal, propriedade.umidade_maxima_ideal,
    )

    leitura = LeituraSensor(
        dispositivo_id=dispositivo.id,
        umidade_solo=dados.umidade_solo,
        temperatura_ar=dados.temperatura_ar,
        umidade_ar=dados.umidade_ar,
        probabilidade_chuva=dados.probabilidade_chuva,
        bomba_ligada=dados.bomba_ligada,
        indice_estresse=indice,
    )
    db.add(leitura)
    db.flush()  # gera o id da leitura dentro da mesma transação

    recomendacao = Recomendacao(
        propriedade_id=propriedade.id,
        leitura_id=leitura.id,
        acao=decisao.acao,
        origem=OrigemRecomendacao.REGRAS,
        motivo=decisao.motivo,
    )
    db.add(recomendacao)

    alertas = _gerar_alertas(propriedade.id, dados, nivel, indice, decisao.acao)
    db.add_all(alertas)

    dispositivo.ultima_comunicacao = datetime.now(timezone.utc)
    db.commit()
    for obj in (leitura, recomendacao, *alertas):
        db.refresh(obj)

    return {
        "leitura": leitura,
        "nivel_estresse": nivel.value,
        "recomendacao": recomendacao,
        "ligar_bomba": decisao.acao == AcaoIrrigacao.IRRIGAR,
        "alertas_gerados": alertas,
    }


def _gerar_alertas(propriedade_id: int, dados: LeituraCriar, nivel: NivelEstresse,
                   indice: int, acao: AcaoIrrigacao) -> list[Alerta]:
    alertas: list[Alerta] = []
    if nivel == NivelEstresse.CRITICO:
        alertas.append(Alerta(
            propriedade_id=propriedade_id, tipo=TipoAlerta.ESTRESSE_HIDRICO, severidade=Severidade.ALTA,
            mensagem=f"Estresse hídrico crítico (índice {indice}/100). Solo com {dados.umidade_solo:.0f}% de umidade.",
        ))
    if acao == AcaoIrrigacao.AGUARDAR_CHUVA:
        alertas.append(Alerta(
            propriedade_id=propriedade_id, tipo=TipoAlerta.CHUVA_PREVISTA, severidade=Severidade.MEDIA,
            mensagem=f"Bomba d'água desligada devido à previsão de chuva ({dados.probabilidade_chuva:.0f}%).",
        ))
    if dados.umidade_solo >= 90:
        alertas.append(Alerta(
            propriedade_id=propriedade_id, tipo=TipoAlerta.SOLO_ENCHARCADO, severidade=Severidade.BAIXA,
            mensagem=f"Solo encharcado ({dados.umidade_solo:.0f}%). Verifique vazamentos ou excesso de rega.",
        ))
    return alertas


def listar_leituras(db: Session, dispositivo_id: int | None = None, propriedade_id: int | None = None,
                    limite: int = 50) -> list[LeituraSensor]:
    from app.domain.models import Dispositivo

    consulta = select(LeituraSensor).order_by(LeituraSensor.registrada_em.desc(), LeituraSensor.id.desc())
    if dispositivo_id:
        consulta = consulta.where(LeituraSensor.dispositivo_id == dispositivo_id)
    if propriedade_id:
        consulta = consulta.join(Dispositivo).where(Dispositivo.propriedade_id == propriedade_id)
    return list(db.scalars(consulta.limit(limite)))
