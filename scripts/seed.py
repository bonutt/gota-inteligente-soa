"""Popula o banco com dados SIMULADOS para demonstração (nenhum dado pessoal real).

Uso (depois de rodar `alembic upgrade head`):
    python -m scripts.seed
"""
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.domain.models import Produtor
from app.schemas.dispositivo import DispositivoCriar
from app.schemas.leitura import LeituraCriar
from app.schemas.produtor import ProdutorCriar
from app.schemas.propriedade import PropriedadeCriar
from app.services import dispositivo_service, produtor_service, propriedade_service, telemetria_service

PRODUTORES = [
    ProdutorCriar(nome="Maria Aparecida (simulado)", telefone="(15) 90000-0001", municipio="Ibiúna", uf="SP"),
    ProdutorCriar(nome="José Carlos (simulado)", telefone="(15) 90000-0002", municipio="Piedade", uf="SP"),
    ProdutorCriar(nome="Ana Lúcia (simulado)", telefone="(11) 90000-0003", municipio="Mogi das Cruzes", uf="SP"),
]

# (índice do produtor, dados da propriedade, código do ESP32)
PROPRIEDADES = [
    (0, dict(nome="Sítio Boa Esperança", municipio="Ibiúna", latitude=-23.656, longitude=-47.222,
             area_hectares=2.5, cultura="Alface", umidade_minima_ideal=40, umidade_maxima_ideal=75), "gota-001"),
    (1, dict(nome="Chácara Santa Luzia", municipio="Piedade", latitude=-23.712, longitude=-47.427,
             area_hectares=4.0, cultura="Tomate", umidade_minima_ideal=35, umidade_maxima_ideal=70), "gota-002"),
    (2, dict(nome="Sítio Três Irmãos", municipio="Mogi das Cruzes", latitude=-23.522, longitude=-46.188,
             area_hectares=1.8, cultura="Morango", umidade_minima_ideal=45, umidade_maxima_ideal=80), "gota-003"),
    (0, dict(nome="Sítio Água Limpa", municipio="Ibiúna", latitude=-23.640, longitude=-47.190,
             area_hectares=3.2, cultura="Couve", umidade_minima_ideal=35, umidade_maxima_ideal=70), "gota-004"),
]

# Leituras simuladas: (código, umidade_solo, temperatura, umidade_ar, chance_chuva, bomba_ligada)
LEITURAS = [
    ("gota-001", 55, 24, 65, 10, False),   # normal
    ("gota-001", 30, 29, 50, 90, False),   # seco, mas vai chover -> AGUARDAR_CHUVA
    ("gota-002", 25, 33, 35, 15, False),   # seco e sem chuva -> IRRIGAR
    ("gota-002", 12, 35, 30, 80, False),   # crítico -> IRRIGAR mesmo com chuva
    ("gota-003", 60, 26, 60, 40, True),    # faixa ideal
    ("gota-003", 38, 28, 55, 85, False),   # seco, vai chover -> AGUARDAR_CHUVA
    ("gota-004", 92, 22, 80, 20, False),   # encharcado
]


def main() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(func.count(Produtor.id))):
            print("Banco já possui dados. Seed ignorado.")
            return
        produtores = [produtor_service.criar(db, p) for p in PRODUTORES]
        for idx_produtor, dados, codigo in PROPRIEDADES:
            prop = propriedade_service.criar(db, PropriedadeCriar(produtor_id=produtores[idx_produtor].id, **dados))
            dispositivo_service.criar(db, DispositivoCriar(codigo=codigo, propriedade_id=prop.id,
                                                           descricao=f"Kit ESP32 - {prop.nome}"))
        for codigo, solo, temp, umid, chuva, bomba in LEITURAS:
            telemetria_service.processar_leitura(db, LeituraCriar(
                codigo_dispositivo=codigo, umidade_solo=solo, temperatura_ar=temp,
                umidade_ar=umid, probabilidade_chuva=chuva, bomba_ligada=bomba,
            ))
        print(f"Seed concluído: {len(PRODUTORES)} produtores, {len(PROPRIEDADES)} propriedades, "
              f"{len(LEITURAS)} leituras simuladas.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
