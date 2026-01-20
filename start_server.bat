@echo off
REM Script para iniciar o servidor de validação de licenças no Windows

echo ========================================
echo Servidor de Validacao de Licencas
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python primeiro.
    pause
    exit /b 1
)

REM Verifica se Flask está instalado
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask nao encontrado. Instalando...
    pip install flask
)

echo Iniciando servidor...
echo.
echo Servidor rodando em: http://localhost:5000
echo Pressione Ctrl+C para parar
echo.

REM Inicia o servidor
python license_server.py

pause

