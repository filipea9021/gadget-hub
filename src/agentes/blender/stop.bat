@echo off
echo Parando servidor Blender...
docker-compose -f docker/docker-compose.yml down
echo.
echo [OK] Servidor parado.
pause
