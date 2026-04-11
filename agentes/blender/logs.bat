@echo off
echo Mostrando logs do servidor Blender (Ctrl+C para sair)...
echo.
docker-compose -f docker/docker-compose.yml logs -f
