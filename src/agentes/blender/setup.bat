@echo off
echo ========================================
echo  GADGET HUB - Blender Server Setup
echo ========================================
echo.

:: Verificar se Docker está rodando
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Docker nao esta rodando!
    echo.
    echo Abra o Docker Desktop e espere ele iniciar.
    echo Depois rode este script de novo.
    pause
    exit /b 1
)
echo [OK] Docker esta rodando

:: Criar pasta de output se não existir
if not exist "output" mkdir output
echo [OK] Pasta output criada

:: Build da imagem
echo.
echo Construindo imagem Docker do Blender...
echo (primeira vez demora ~5 min - baixa Blender 4.1)
echo.
docker-compose -f docker/docker-compose.yml build
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha no build da imagem!
    pause
    exit /b 1
)
echo.
echo [OK] Imagem construida com sucesso

:: Subir o container
echo.
echo Iniciando servidor Blender...
docker-compose -f docker/docker-compose.yml up -d
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao iniciar container!
    pause
    exit /b 1
)

:: Esperar o servidor subir
echo.
echo Aguardando servidor iniciar...
timeout /t 10 /nobreak >nul

:: Testar health
echo.
echo Testando conexao...
curl -s http://localhost:8585/api/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [AVISO] Servidor ainda iniciando... aguarde mais 20 segundos
    timeout /t 20 /nobreak >nul
    curl -s http://localhost:8585/api/health >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERRO] Servidor nao respondeu. Verifique os logs:
        echo   docker-compose -f docker/docker-compose.yml logs
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo  SERVIDOR BLENDER RODANDO!
echo ========================================
echo.
echo  URL:    http://localhost:8585
echo  Health: http://localhost:8585/api/health
echo  Jobs:   http://localhost:8585/api/jobs
echo  Stats:  http://localhost:8585/api/stats
echo.
echo  Comandos uteis:
echo    Ver logs:    docker-compose -f docker/docker-compose.yml logs -f
echo    Parar:       docker-compose -f docker/docker-compose.yml down
echo    Reiniciar:   docker-compose -f docker/docker-compose.yml restart
echo.
echo  Agora rode o sistema de agentes:
echo    cd ..
echo    npm run dev
echo.
pause
