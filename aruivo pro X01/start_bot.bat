@echo off
title CIS — Bot Telegram
cd /d "%~dp0"

echo.
echo  ====================================
echo   CIS — Content Intelligence System
echo   Bot Telegram
echo  ====================================
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo Instala Python em: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Instala / atualiza dependências
echo [1/2] Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: Inicia o bot
echo [2/2] Iniciando o bot...
echo.
python telegram_bot.py

pause
