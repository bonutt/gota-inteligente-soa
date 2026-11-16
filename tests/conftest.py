import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.database import criar_engine, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path):
    url = f"sqlite:///{tmp_path / 'teste.db'}"
    cfg = Config("alembic.ini")
    cfg.cmd_opts = type("Opts", (), {"x": [f"url={url}"]})()
    command.upgrade(cfg, "head")  # o banco de teste é criado pelas próprias migrações

    engine = criar_engine(url)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture()
def cenario(client):
    """Cria produtor, propriedade e dispositivo para os testes."""
    produtor = client.post("/api/v1/produtores", json={
        "nome": "Produtor Teste", "municipio": "Ibiúna", "uf": "SP"}).json()
    propriedade = client.post("/api/v1/propriedades", json={
        "produtor_id": produtor["id"], "nome": "Sítio Teste", "municipio": "Ibiúna",
        "latitude": -23.6, "longitude": -47.2, "area_hectares": 2, "cultura": "Alface",
        "umidade_minima_ideal": 35, "umidade_maxima_ideal": 70}).json()
    dispositivo = client.post("/api/v1/dispositivos", json={
        "codigo": "gota-teste", "propriedade_id": propriedade["id"]}).json()
    return {"produtor": produtor, "propriedade": propriedade, "dispositivo": dispositivo}
