# Setup do Blender Server — Windows

## Pré-requisitos

- Docker Desktop instalado e rodando (ícone na barra de tarefas, baleia verde)
- Node.js 18+ instalado

## Passo 1 — Subir o Servidor Blender

Abra o terminal (PowerShell ou CMD) e navegue até a pasta:

```cmd
cd gadget-hub\agentes\blender
```

Rode o setup automático:

```cmd
setup.bat
```

O que ele faz:
1. Verifica se o Docker está rodando
2. Constrói a imagem Docker com Blender 4.1 (~5 min na primeira vez)
3. Sobe o container na porta 8585
4. Testa se o servidor respondeu

Quando aparecer "SERVIDOR BLENDER RODANDO!" está pronto.

## Passo 2 — Testar o Servidor

```cmd
test.bat
```

Isso envia um job de render de teste e mostra o resultado. Se aparecer `"status": "queued"`, está tudo funcionando.

## Passo 3 — Rodar o Sistema de Agentes

Abra outro terminal:

```cmd
cd gadget-hub\agentes
npm install
npm run dev
```

Vai aparecer o menu de comandos. O Blender já aparece como agente registrado.

Teste os comandos:

```
> status()                    -- ver todos os agentes (incluindo Blender)
> renderStatus()              -- ver fila do Blender
> templates()                 -- ver templates de cena
> paletas()                   -- ver paletas cinematográficas
```

## Passo 4 — Gerar Primeiro Render

### Render de produto:
```
> render({id: 'P1', nome: 'Smart Plug WiFi', sku: 'SP001', categoria: 'smart_plug'}, ['hero', 'multiAngle'])
```

### Render completo (todos os tipos relevantes):
```
> renderCompleto({id: 'P2', nome: 'Fone Bluetooth', sku: 'FB001', categoria: 'fone'})
```

### Vídeo cinematográfico:
```
> cinematic({id: 'P3', nome: 'Smartwatch Pro', sku: 'SW001', categoria: 'smartwatch'}, {palette: 'cyber_purple', cameraStyle: 'push_in'})
```

### Conteúdo abstrato para redes sociais:
```
> cinematicContent('sphere', {palette: 'tech_blue'})
```

### Batch (6 vídeos automáticos):
```
> cinematicBatch()
```

## Comandos Úteis

| Comando | O que faz |
|---------|-----------|
| `setup.bat` | Build + inicia o servidor |
| `test.bat` | Testa se o servidor funciona |
| `stop.bat` | Para o servidor |
| `logs.bat` | Mostra logs em tempo real |

## Verificar no Navegador

- Health: http://localhost:8585/api/health
- Jobs: http://localhost:8585/api/jobs
- Stats: http://localhost:8585/api/stats

## Onde ficam os renders?

Na pasta `gadget-hub\agentes\blender\output\`, organizados por SKU do produto:

```
output/
├── SP001/
│   ├── hero.png
│   ├── multi_angle_front.png
│   ├── multi_angle_right.png
│   ├── multi_angle_back.png
│   └── multi_angle_top.png
├── FB001/
│   ├── hero.png
│   ├── turntable_360.mp4
│   └── exploded_view.mp4
└── cinematic_sphere/
    ├── cinematic_video.mp4
    ├── cinematic_thumbnail.png
    └── keyframe_0060.png
```

## Problemas Comuns

**Docker não inicia:** Certifique que o Docker Desktop está aberto e com a baleia verde na barra de tarefas. Se pedir para ativar WSL2, siga as instruções.

**Build falha no download do Blender:** A URL do Blender pode mudar. Verifique em https://www.blender.org/download/ e atualize a variável `BLENDER_URL` no Dockerfile.

**Servidor não responde na porta 8585:** Verifique se nenhum outro programa está usando essa porta. Mude `BLENDER_PORT=8586` no `.env` se precisar.

**Render demora muito:** No Docker sem GPU, um render Cycles com 128 samples pode demorar 1-3 minutos por imagem. Para testes rápidos, use amostras baixas (32).
