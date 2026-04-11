@echo off
echo ========================================
echo  GADGET HUB - Teste do Blender Server
echo ========================================
echo.

:: 1. Health check
echo [1/4] Testando health...
curl -s http://localhost:8585/api/health
echo.
echo.

:: 2. Stats
echo [2/4] Verificando stats...
curl -s http://localhost:8585/api/stats
echo.
echo.

:: 3. Submeter job de teste
echo [3/4] Submetendo job de render de teste...
curl -s -X POST http://localhost:8585/api/jobs ^
  -H "Content-Type: application/json" ^
  -d "{\"jobId\":\"test_001\",\"product\":{\"id\":\"TEST\",\"name\":\"Smart Plug Test\",\"sku\":\"SP-TEST\",\"category\":\"smart_plug\"},\"template\":\"electronics_small\",\"renders\":[{\"id\":\"hero\",\"lighting\":\"studio_3point\",\"background\":\"gradient_white\",\"resolution\":{\"x\":960,\"y\":960},\"samples\":32}],\"config\":{\"engine\":\"CYCLES\",\"samples\":32,\"resolution\":{\"x\":960,\"y\":960}}}"
echo.
echo.

:: 4. Listar jobs
echo [4/4] Listando jobs...
timeout /t 3 /nobreak >nul
curl -s http://localhost:8585/api/jobs
echo.
echo.

echo ========================================
echo  Teste completo!
echo ========================================
echo.
echo Se o job apareceu como "queued" ou "processing", esta tudo OK.
echo Os renders vao aparecer na pasta: blender\output\SP-TEST\
echo.
pause
