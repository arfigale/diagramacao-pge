@echo off
rem Instala ou atualiza a skill diagramacao-pge: pasta de skills, ambiente, fonte e zip.
rem De dois cliques neste arquivo.
setlocal
set "AQUI=%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%AQUI%scripts\instalar.py" %*
    goto fim
)
where python >nul 2>nul
if %errorlevel%==0 (
    python "%AQUI%scripts\instalar.py" %*
    goto fim
)
echo Nao encontrei Python neste computador. Instale em python.org (3.10 ou mais novo), marcando "Add python.exe to PATH".
:fim
pause
