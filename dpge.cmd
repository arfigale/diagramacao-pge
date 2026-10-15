@echo off
rem Ponto de entrada da skill diagramacao-pge no Windows.
rem Usa o Python do computador (py ou python). Uso: dpge.cmd build documento.html
setlocal
set "AQUI=%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%AQUI%scripts\dpge.py" %*
    exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
    python "%AQUI%scripts\dpge.py" %*
    exit /b
)
echo Nao encontrei Python neste computador. Instale em python.org (3.10 ou mais novo).
exit /b 1
