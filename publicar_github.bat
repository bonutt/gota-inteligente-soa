@echo off
REM ============================================================
REM  Publica este projeto em https://github.com/bonutt/gota-inteligente-soa
REM  Uso: de dois cliques neste arquivo (precisa do Git instalado)
REM ============================================================
cd /d "%~dp0"
set LOG=publicar_log.txt
echo Publicando no GitHub... > %LOG%
if not exist ".git" git init -b main >> %LOG% 2>&1
git config user.name >nul 2>&1 || git config user.name "Luigi Bonuccelli"
git config user.email >nul 2>&1 || git config user.email "bonuccellibr@gmail.com"
git add -A >> %LOG% 2>&1
git commit -m "Gota Inteligente API - entrega de SOA e Web Services" -m "Backend FastAPI com dominio em camadas, SQLAlchemy, migracoes Alembic, seed de dados simulados, colecao do Insomnia, evidencias de testes e testes automatizados." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Egwzw9iu1tVFqPdUgieuAZ" >> %LOG% 2>&1
git branch -M main >> %LOG% 2>&1
git remote remove origin >nul 2>&1
git remote add origin https://github.com/bonutt/gota-inteligente-soa.git >> %LOG% 2>&1
echo. >> %LOG%
echo Enviando (se abrir uma janela de login do GitHub, entre com a conta bonutt)...
git push -u origin main >> %LOG% 2>&1
if errorlevel 1 (echo FALHOU >> %LOG%) else (echo SUCESSO >> %LOG%)
type %LOG%
echo.
echo Pronto. Pode fechar esta janela.
pause
