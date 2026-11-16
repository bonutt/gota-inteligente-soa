@echo off
REM ============================================================
REM  Gota Inteligente API - prepara o ambiente e sobe a API
REM  Uso: de dois cliques neste arquivo (Windows)
REM ============================================================
cd /d "%~dp0"
echo [1/5] Criando ambiente virtual (.venv)...
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv || python -m venv .venv
)
echo [2/5] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt
echo [3/5] Aplicando migracoes (alembic upgrade head)...
".venv\Scripts\python.exe" -m alembic upgrade head
".venv\Scripts\python.exe" -m alembic current
echo [4/5] Populando dados simulados (seed)...
".venv\Scripts\python.exe" -m scripts.seed
echo [5/5] API no ar em http://localhost:8000  (Swagger: http://localhost:8000/docs)
echo Para parar, feche esta janela ou aperte Ctrl+C.
".venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000
pause
