"""Gota Inteligente API — backend da CitizenTech de irrigação inteligente."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alertas, dispositivos, leituras, painel, produtores, propriedades, recomendacoes
from app.core.config import settings
from app.core.excecoes import registrar_handlers

app = FastAPI(
    title=settings.api_titulo,
    version=settings.api_versao,
    description=(
        "Backend da **Gota Inteligente**: recebe a telemetria do ESP32 (umidade do solo, clima), "
        "cruza com a previsão de chuva, decide se a bomba deve ser ligada e gera alertas para o "
        "app do agricultor e para o painel regional do Sindicato Rural / Prefeitura."
    ),
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
registrar_handlers(app)

API_PREFIXO = "/api/v1"
for modulo in (produtores, propriedades, dispositivos, leituras, recomendacoes, alertas, painel):
    app.include_router(modulo.router, prefix=API_PREFIXO)


@app.get("/health", tags=["Status"], summary="Verifica se a API está no ar")
def health():
    return {"status": "ok", "servico": settings.api_titulo, "versao": settings.api_versao}
