# PLANO DE REESTRUTURAÇÃO MODULAR V3 — Stark Ecosystem

**Data:** 2026-04-11  
**Versão:** 3.4 (+ Asset Loader sec.13, Pipeline 2D sec.14, Backend Engine sec.15, Custom App + n8n sec.16, Estratégia de Nicho sec.17, Web Factory detalhado sec.18)  
**Autor:** Filipe + Claude  
**Orçamento mensal:** até €200 (meta operacional: €50–80)  
**Objetivo:** Transformar o Gadget Hub num ecossistema modular com módulos independentes — Marketing Studio (prioridade 1), App Factory (futuro), Web Factory (futuro) — todos dentro do mesmo workspace, com comunicação controlada, Blender headless na nuvem, produção híbrida de conteúdo (3D + 2D), e produção diária de 10 vídeos de qualidade.

---

## 1. ESTADO ATUAL DO PROJETO

### O que já temos e funciona

O Gadget Hub tem uma base sólida com 7 agentes autónomos que estendem `AgenteBase`:

| Agente | Função | Estado |
|--------|--------|--------|
| AgenteShopify | CRUD de produtos, gestão da loja | Funcional |
| AgenteCJ | Importação de produtos CJ Dropshipping | Funcional |
| AgentePrecos | Cálculo dinâmico de preços e margens | Funcional |
| AgenteMarketing | Campanhas publicitárias (TikTok, Meta) | Funcional |
| AgenteEstoque | Controlo de stock e alertas | Funcional |
| AgenteBlender | Renders 3D e vídeos cinematográficos | Funcional |
| AgenteAutomacao | FAQs, webhooks, emails, hashtags | Funcional |

### Infraestrutura existente

- Manager de agentes com EventEmitter (comunicação por eventos)
- Pipeline de comunicação entre agentes (CJ→Shopify+Blender, Blender→Marketing, etc.)
- AI Router com LLM (comandos em linguagem natural via Claude/GPT/Ollama)
- API REST + WebSocket unificada (Express)
- SQLite para persistência de estado dos agentes
- Config centralizada com modos: demo / semi / autónomo
- Logger estruturado com níveis
- REPL interativo para comandos manuais
- Sub-módulo Blender com scripts Python, templates de cena, Docker config
- Templates de copy por funil (awareness, conversion, remarketing)

### Estrutura de pastas atual

```
/gadget-hub
├── main.js                    ← Ponto de entrada + pipeline + REPL
├── src/
│   ├── agentes/               ← 7 agentes
│   │   ├── blender/           ← Sub-módulo Blender (scripts, templates, docker)
│   │   ├── agente-marketing.js
│   │   ├── agente-automacao.js
│   │   ├── agente-shopify.js
│   │   ├── agente-cj.js
│   │   ├── agente-precos.js
│   │   └── agente-estoque.js
│   ├── ai/                    ← llm-client.js, router.js, prompts.js
│   ├── api/                   ← Express + WebSocket (server.js)
│   ├── core/                  ← agente-base.js, config.js, logger.js, database.js, manager.js
│   └── dashboard/             ← Frontend
├── config/
├── data/
├── archive/                   ← Código legado arquivado
└── testes/
```

---

## 2. IDEIAS EXTRAÍDAS E ADAPTADAS AO PROJETO

### IDEIA 1: Marketing Studio — Produtora de Conteúdo Independente

**Conceito:** Extrair o AgenteBlender e as capacidades de produção de conteúdo do Gadget Hub e criar um módulo independente que funciona como uma "mini produtora" interna. Não serve apenas a loja — pode criar conteúdo para qualquer cliente, projeto pessoal, hobby, ou venda direta.

**O que muda no Gadget Hub:**
- O AgenteMarketing atual fica apenas como "gestor de campanhas + cliente" que faz pedidos ao Marketing Studio
- O AgenteBlender sai do Gadget Hub e vive dentro do Marketing Studio
- O pipeline em main.js passa a enviar pedidos via Message Bus em vez de chamar Blender direto

**Capacidades do Marketing Studio:**
- Geração automática de roteiros via IA (LLM)
- Pipeline completo: pedido → roteiro → cena Blender → render → armazenamento → distribuição
- Biblioteca de vídeos reutilizáveis organizados por categoria
- Suporte a múltiplos "clientes" (loja, clientes externos, pessoal, hobby)
- Publicação automatizada (agendar posts, armazenar para repost futuro)
- Blender headless (sem interface) controlado por scripts Python
- Render em batch (lote de vídeos processados de uma vez)

### IDEIA 2: Blender como Microserviço (Headless)

**Conceito extraído da conversa:** O Blender pode correr em modo headless (sem interface gráfica) controlado inteiramente por scripts Python via linha de comando. Isto permite correr na nuvem, em servidores sem monitor, e automatizar completamente a produção.

**Como funciona na prática:**
```bash
# Correr Blender sem interface, executando um script Python
blender -b template.blend -P gerar_video.py -- --produto "Fone X5" --estilo "cinematografico"
```

**O que já é possível com Blender + Python (validado pela comunidade):**
- Criar objetos, materiais, luzes e câmaras automaticamente
- Animar objectos (rotação, movimento, física)
- Carregar modelos externos (.glb, .obj, .fbx)
- Gerar keyframes e animações procedurais
- Configurar motor de render (EEVEE para velocidade, Cycles para qualidade)
- Renderizar vídeo completo (.mp4) sem abrir interface
- Processar em loop: gerar variações automáticas (cor, câmara, iluminação)
- Render em batch: processar fila de múltiplos vídeos sequencialmente
- Simulação de física (queda, água, fumaça) via código
- Criação procedural de cenas inteiras (cidades, ambientes, grids de objectos)

### IDEIA 3: Pipeline de Produção — 10 Vídeos/Dia

**Conceito:** Em vez de escala massiva (100+ vídeos/dia), focar em 10 vídeos de qualidade por dia. Isto reduz custos drasticamente e permite validar o sistema antes de escalar.

**Distribuição diária sugerida:**
- 3 vídeos de produto (marketing da loja)
- 3 vídeos virais (cortes, reels, shorts)
- 2 vídeos de teste (novos templates, estilos)
- 2 vídeos para clientes ou uso pessoal

**Tempo de render estimado:** 2-5 min por vídeo → 10 vídeos = ~50 minutos de GPU/dia

### IDEIA 4: Infraestrutura Cloud Híbrida

**Conceito:** Não depender só do PC local. Usar modelo híbrido — desenvolvimento e testes local, render pesado na nuvem. GPU na nuvem liga só quando precisa (pay-per-use).

**Fluxo:**
```
PC local (Stark) → cria pedidos → envia para fila
                                        ↓
                              Servidor nuvem (GPU)
                                        ↓
                              Blender headless renderiza
                                        ↓
                              Vídeo pronto → storage
                                        ↓
                              PC local recebe notificação
```

### IDEIA 5: App Factory — Criação de Aplicativos

**Conceito:** Módulo separado que analisa qualquer projeto do ecossistema e cria uma interface (app) para ele.

**Primeiro app: Interface do Sistema Blender (Marketing Studio)**

O primeiro aplicativo criado pelo App Factory será dedicado ao sistema Blender dentro do Marketing Studio. Esta é a prioridade porque o Blender headless não tem interface — corre em linha de comando pura. Sem um app de controlo, o operador teria de escrever JSON à mão e correr scripts no terminal, o que não é prático para uso diário.

**O que este app faz:**
- Painel visual para criar pedidos de vídeo (seleccionar produto, estilo, duração, resolução)
- Controlo da fila de render (ver pedidos pendentes, em progresso, concluídos)
- Visualização em tempo real do estado do Blender (idle, rendering, erro)
- Selecção de templates de cena (produto_360, cinematico, viral, apresentação)
- Definição de destino do vídeo (onde guardar, para onde publicar)
- Preview de vídeos gerados directamente no app
- Dashboard de custos (tempo de GPU, custo estimado por render, total mensal)
- Biblioteca de vídeos gerados (pesquisar, filtrar por categoria, reutilizar)

**Porquê este app primeiro:**
1. O Marketing Studio é o primeiro módulo construído — precisa de interface antes dos outros
2. Sem app, o sistema Blender é inacessível para uso rápido do dia-a-dia
3. Serve como caso de teste real para o App Factory — se consegue criar este, consegue criar os próximos
4. A interface permite controlar a produção dos 10 vídeos/dia sem tocar em código

**Stack sugerida:** React (web-first, acesso via browser) + WebSocket (estado em tempo real do render) + API do Marketing Studio como backend.

**Segundo app (futuro):** Painel de gestão para o Gadget Hub.
**Terceiro app (futuro):** Interface unificada do Stark Ecosystem (controlo de todos os módulos).

### IDEIA 6: Web Factory — Evolução do Sistema de Sites

**Conceito:** O sistema atual de criação de sites/templates torna-se um módulo independente para criar sites de qualquer nicho. Pode pedir assets visuais ao Marketing Studio e integrar apps do App Factory.

### IDEIA 7: Skills por Módulo

**Conceito:** Cada módulo tem skills próprias que pode executar independentemente. Isto permite que cada módulo evolua as suas capacidades sem depender dos outros.

**Exemplos:**
- Marketing Studio: gerar_roteiro, renderizar_video, postar_conteudo, criar_template, gerar_thumbnail
- App Factory: analisar_projeto, gerar_ui, criar_backend, buildar_app
- Web Factory: criar_site, gerar_template, optimizar_seo
- Gadget Hub: gerir_produtos, analisar_precos, responder_faq, criar_campanha

---

## 3. ARQUITETURA PROPOSTA

### Estrutura de pastas final

```
/github-workspace/                          ← Pasta raiz (cloud tem acesso a tudo)
│
├── /gadget-hub/                            ← PROJETO 1: Loja e-commerce (existente)
│   ├── main.js
│   ├── package.json
│   ├── src/
│   │   ├── agentes/
│   │   │   ├── agente-shopify.js
│   │   │   ├── agente-cj.js
│   │   │   ├── agente-precos.js
│   │   │   ├── agente-estoque.js
│   │   │   ├── agente-automacao.js
│   │   │   └── agente-marketing-client.js  ← NOVO: cliente do Marketing Studio
│   │   ├── ai/                             ← LLM client, router, prompts
│   │   ├── api/                            ← Express + WebSocket
│   │   ├── core/                           ← config, logger (importa de shared)
│   │   └── dashboard/
│   ├── config/
│   ├── data/
│   └── testes/
│
├── /marketing-studio/                      ← PROJETO 2: Produtora de conteúdo (NOVO)
│   ├── main.js
│   ├── package.json
│   ├── src/
│   │   ├── agentes/
│   │   │   ├── agente-video.js             ← Orquestrador de vídeos (absorve Blender)
│   │   │   ├── agente-roteiro.js           ← Geração de roteiros via IA
│   │   │   ├── agente-render.js            ← Controlo do pipeline de render
│   │   │   ├── agente-distribuicao.js      ← Publicação e armazenamento (v2)
│   │   │   └── agente-assets.js            ← Gestão de templates e recursos (v2)
│   │   ├── core/                           ← Config própria (importa base de shared)
│   │   ├── ai/                             ← LLM para roteiros e análise criativa
│   │   ├── api/                            ← API própria: /pedidos, /status, /storage, /health
│   │   └── storage/                        ← Biblioteca de vídeos organizados
│   │       ├── videos/
│   │       │   ├── marketing/
│   │       │   ├── viral/
│   │       │   ├── clientes/
│   │       │   ├── pessoal/
│   │       │   └── templates/
│   │       ├── thumbnails/
│   │       └── assets/
│   ├── blender/                            ← Motor de render (migrado do gadget-hub)
│   │   ├── scripts/
│   │   │   ├── render_produto.py           ← Script principal de render
│   │   │   ├── render_batch.py             ← Processamento em lote
│   │   │   ├── render_viral.py             ← Templates para conteúdo viral
│   │   │   └── utils.py                    ← Funções comuns (câmara, luz, animação)
│   │   ├── templates/                      ← Ficheiros .blend pré-configurados
│   │   │   ├── produto_360.blend
│   │   │   ├── cinematico_basico.blend
│   │   │   ├── viral_tiktok.blend
│   │   │   └── apresentacao.blend
│   │   └── docker/                         ← Container Docker para Blender headless
│   │       ├── Dockerfile
│   │       └── docker-compose.yml
│   ├── queue/                              ← Fila local de pedidos pendentes
│   │   └── .gitkeep
│   └── testes/
│
├── /app-factory/                           ← PROJETO 3: Criação de apps (FUTURO)
│   ├── main.js
│   ├── package.json
│   └── src/
│       ├── analyzer/                       ← Análise de projectos existentes
│       │   └── api-scanner.js              ← Lê endpoints de um módulo e mapeia funcionalidades
│       ├── generator/                      ← Geração de código
│       │   ├── react-generator.js          ← Gerador de componentes React
│       │   └── page-builder.js             ← Montagem de páginas a partir de componentes
│       ├── builder/                        ← Build e deploy
│       │   └── build-manager.js            ← Compilação e empacotamento
│       ├── templates/                      ← Templates de UI
│       │   ├── dashboard/                  ← Layout tipo painel de controlo
│       │   ├── form/                       ← Formulários de input (criar pedidos)
│       │   ├── queue-viewer/               ← Visualização de filas e estados
│       │   └── media-library/              ← Galeria de vídeos/imagens
│       └── apps/                           ← Apps gerados
│           └── blender-control-panel/      ← PRIMEIRO APP: Interface do sistema Blender
│               ├── src/
│               │   ├── App.jsx             ← Componente principal
│               │   ├── pages/
│               │   │   ├── Dashboard.jsx   ← Estado do Blender + custos + métricas
│               │   │   ├── NovoPedido.jsx  ← Formulário: criar pedido de vídeo
│               │   │   ├── Fila.jsx        ← Ver fila de render (pendente/progresso/feito)
│               │   │   ├── Biblioteca.jsx  ← Galeria de vídeos gerados
│               │   │   └── Config.jsx      ← Templates, motor render, resolução
│               │   ├── components/
│               │   │   ├── RenderStatus.jsx    ← Estado em tempo real (WebSocket)
│               │   │   ├── VideoPreview.jsx    ← Preview de vídeos gerados
│               │   │   ├── CostTracker.jsx     ← Custo GPU acumulado
│               │   │   └── TemplateSelector.jsx ← Seleccionar template de cena
│               │   └── api/
│               │       └── studio-client.js    ← Chamadas à API do Marketing Studio
│               ├── public/
│               └── package.json
│
├── /shared/                                ← MÓDULO PARTILHADO (read-only na prática)
│   ├── package.json
│   ├── core/
│   │   ├── agente-base.js                  ← Classe base (TODOS os projectos usam)
│   │   ├── logger.js                       ← Logger estruturado
│   │   ├── database.js                     ← SQLite wrapper
│   │   └── message-bus.js                  ← Sistema de mensagens entre módulos
│   ├── contracts/
│   │   ├── pedido.schema.json              ← Schema de pedidos entre módulos
│   │   ├── resultado.schema.json           ← Schema de respostas
│   │   └── health.schema.json              ← Schema de health check
│   └── utils/
│       ├── validators.js                   ← Validação de schemas
│       └── retry.js                        ← Lógica de retry com backoff
│
├── .env                                    ← Configuração centralizada (ÚNICO ficheiro)
├── package.json                            ← npm workspaces (raiz)
└── README.md
```

### npm Workspaces (package.json raiz)

```json
{
  "name": "stark-ecosystem",
  "private": true,
  "workspaces": [
    "shared",
    "gadget-hub",
    "marketing-studio"
  ],
  "scripts": {
    "start:hub": "cd gadget-hub && node main.js",
    "start:studio": "cd marketing-studio && node main.js",
    "start:all": "npm run start:hub & npm run start:studio",
    "test:hub": "cd gadget-hub && npm test",
    "test:studio": "cd marketing-studio && npm test",
    "test:all": "npm run test:hub && npm run test:studio",
    "health": "curl -s localhost:3001/api/health && curl -s localhost:3002/api/health"
  }
}
```

---

## 4. SISTEMA DE COMUNICAÇÃO ENTRE MÓDULOS

### Protocolo de Pedidos (Message Bus)

```javascript
// Formato de pedido entre módulos
{
  "id": "req_20260409_001",
  "from": "gadget-hub",
  "to": "marketing-studio",
  "task": "criar_video_produto",
  "priority": "normal",              // normal | urgente | baixa
  "payload": {
    "produto": "Fone Bluetooth X5",
    "estilo": "cinematografico",      // cinematografico | viral | produto_360 | apresentacao
    "duracao_segundos": 30,
    "resolucao": "1080x1920",         // vertical para TikTok/Reels
    "motor_render": "eevee",          // eevee (rápido) | cycles (qualidade)
    "canais_destino": ["tiktok", "instagram"],
    "categoria_storage": "marketing"
  },
  "callback": "http://localhost:3001/api/resultado",
  "created_at": "2026-04-09T10:00:00Z",
  "deadline": "2026-04-09T18:00:00Z"
}

// Formato de resposta
{
  "id": "res_20260409_001",
  "request_id": "req_20260409_001",
  "from": "marketing-studio",
  "status": "completed",              // completed | failed | in_progress | queued
  "result": {
    "videos": ["/storage/videos/marketing/fone-x5-tiktok-30s.mp4"],
    "thumbnails": ["/storage/thumbnails/fone-x5-thumb.jpg"],
    "metadata": {
      "duracao_real": 32,
      "resolucao": "1080x1920",
      "motor": "eevee",
      "tempo_render_segundos": 180,
      "tamanho_mb": 24.5
    }
  },
  "render_cost": {
    "tempo_gpu_minutos": 3,
    "custo_estimado_eur": 0.025
  },
  "completed_at": "2026-04-09T10:03:12Z"
}
```

### Como os módulos comunicam (fluxo técnico)

```
1. Gadget Hub cria pedido JSON → escreve em /shared/queue/ ou envia via HTTP
2. Message Bus detecta novo pedido → valida schema → encaminha
3. Marketing Studio recebe → agente-video.js lê pedido → cria pipeline
4. agente-roteiro.js gera roteiro (se necessário) via LLM
5. agente-render.js executa Blender headless com script Python
6. Vídeo renderizado → guardado em /marketing-studio/storage/
7. Resultado JSON enviado de volta via callback HTTP
8. Gadget Hub recebe notificação → actualiza estado → usa vídeo
```

---

## 5. PIPELINE DE RENDER — BLENDER HEADLESS

### Como o Blender corre sem interface

```bash
# Render único de produto
blender -b templates/produto_360.blend -P scripts/render_produto.py \
  -- --produto "Fone X5" --estilo "cinematografico" --output "/storage/videos/marketing/"

# Render em batch (10 vídeos)
blender -b templates/produto_360.blend -P scripts/render_batch.py \
  -- --fila "/queue/batch_20260409.json" --output "/storage/videos/"
```

### Script Python base (render_produto.py) — estrutura

```python
import bpy
import sys
import json

# Ler argumentos passados via linha de comando
argv = sys.argv
args_index = argv.index("--") + 1
args = argv[args_index:]

# Parsear parâmetros
produto_nome = args[args.index("--produto") + 1]
estilo = args[args.index("--estilo") + 1]
output_dir = args[args.index("--output") + 1]

# 1. Limpar cena ou carregar template
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Carregar modelo do produto (ou criar placeholder)
# bpy.ops.import_scene.gltf(filepath=f"modelos/{produto_nome}.glb")

# 3. Configurar câmara + luz baseado no estilo
if estilo == "cinematografico":
    # Câmara com movimento suave, luz dramática
    pass
elif estilo == "viral":
    # Câmara rápida, cores vivas
    pass
elif estilo == "produto_360":
    # Rotação 360° do produto
    pass

# 4. Configurar render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'  # Rápido para marketing
scene.render.filepath = f"{output_dir}/{produto_nome}.mp4"
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920  # Vertical (TikTok/Reels)
scene.frame_start = 1
scene.frame_end = 120  # 5 segundos a 24fps

# 5. Renderizar
bpy.ops.render.render(animation=True)

# 6. Exportar resultado
resultado = {
    "status": "completed",
    "output": f"{output_dir}/{produto_nome}.mp4",
    "frames": 120,
    "motor": "eevee"
}
with open(f"{output_dir}/{produto_nome}_result.json", 'w') as f:
    json.dump(resultado, f)
```

### Script de batch (render_batch.py) — estrutura

```python
import bpy
import json
import sys
import time

# Ler ficheiro de fila
argv = sys.argv
args_index = argv.index("--") + 1
fila_path = argv[args_index + 1]
output_dir = argv[args_index + 3]

with open(fila_path) as f:
    fila = json.load(f)

resultados = []

for i, pedido in enumerate(fila["pedidos"]):
    print(f"\n--- Processando {i+1}/{len(fila['pedidos'])}: {pedido['produto']} ---")
    inicio = time.time()
    
    # Limpar cena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Configurar cena baseado no pedido
    # ... (mesmo fluxo do render_produto.py)
    
    # Renderizar
    nome_ficheiro = f"{pedido['produto'].replace(' ', '_').lower()}"
    bpy.context.scene.render.filepath = f"{output_dir}/{nome_ficheiro}.mp4"
    bpy.ops.render.render(animation=True)
    
    tempo = time.time() - inicio
    resultados.append({
        "produto": pedido["produto"],
        "output": f"{output_dir}/{nome_ficheiro}.mp4",
        "tempo_render_segundos": round(tempo, 1)
    })

# Salvar relatório do batch
with open(f"{output_dir}/batch_report.json", 'w') as f:
    json.dump({"total": len(resultados), "resultados": resultados}, f, indent=2)
```

### Formato do ficheiro de fila (batch)

```json
{
  "batch_id": "batch_20260409_001",
  "created_at": "2026-04-09T08:00:00Z",
  "config_global": {
    "motor": "eevee",
    "resolucao": "1080x1920",
    "fps": 24
  },
  "pedidos": [
    { "produto": "Fone Bluetooth X5", "estilo": "cinematografico", "duracao_frames": 120 },
    { "produto": "Smart Plug WiFi", "estilo": "produto_360", "duracao_frames": 96 },
    { "produto": "LED Strip RGB", "estilo": "viral", "duracao_frames": 72 },
    { "produto": "Carregador Wireless", "estilo": "cinematografico", "duracao_frames": 120 },
    { "produto": "Smartwatch Pro", "estilo": "produto_360", "duracao_frames": 96 },
    { "produto": "Câmara Segurança", "estilo": "cinematografico", "duracao_frames": 120 },
    { "produto": "Fone Gaming RGB", "estilo": "viral", "duracao_frames": 72 },
    { "produto": "Hub USB-C", "estilo": "produto_360", "duracao_frames": 96 },
    { "produto": "Lâmpada Smart", "estilo": "viral", "duracao_frames": 72 },
    { "produto": "Powerbank 20000mAh", "estilo": "cinematografico", "duracao_frames": 120 }
  ]
}
```

---

## 6. INFRAESTRUTURA E CUSTOS

### Orçamento mensal: até €200 (meta: €50–80)

| Componente | Função | Custo estimado | Prioridade |
|------------|--------|---------------|------------|
| GPU cloud (RunPod/Vast.ai) | Render Blender headless | €15–40/mês | Fase 2 |
| VPS leve (Hetzner/OVH) | Servidor Stark (fila + orquestração) | €5–15/mês | Fase 2 |
| Armazenamento (S3/Backblaze B2) | Guardar vídeos + assets | €5–10/mês | Fase 2 |
| API LLM (Claude/GPT) | Roteiros + classificação | €10–20/mês | Fase 1 |
| Domínio + extras | DNS, SSL, imprevistos | €5–10/mês | Fase 3 |
| **TOTAL ESTIMADO** | | **€40–95/mês** | |
| **Margem de segurança** | | **€105–160** | |

### Cálculo de custo de render

**Base:** GPU média na nuvem ≈ €0.50/hora

- 10 vídeos/dia × 5 min render cada = 50 min/dia
- 50 min/dia × 30 dias = 25 horas/mês
- 25 horas × €0.50 = **€12.50/mês** de render

**Optimizações para reduzir custo:**
1. EEVEE em vez de Cycles (10-50x mais rápido, qualidade suficiente para marketing)
2. Resolução 1080p (não 4K — desnecessário para redes sociais)
3. Templates fixos (trocar só o produto, não recriar tudo)
4. Ligar GPU só quando precisa (não 24h)
5. Batch processing (processar 10 vídeos de uma vez, menos overhead)
6. Render parcial (só muda produto/cor, mantém cena)

### Modelo híbrido (PC local + Nuvem)

| Tarefa | Onde corre | Porquê |
|--------|-----------|--------|
| Desenvolvimento de scripts | PC local | Iteração rápida, sem custo |
| Testes de render (1-2 vídeos) | PC local | Validar antes de gastar GPU |
| Render em batch (10 vídeos) | Nuvem (GPU) | Velocidade, não trava PC |
| Renders pesados (Cycles, VFX) | Nuvem (GPU) | PC não aguenta |
| Orquestração (Stark, fila) | PC local ou VPS | Leve, sem GPU |
| Armazenamento final | Cloud (S3/B2) | Persistente, acessível |

---

## 7. ZONAS DE FRACASSO IDENTIFICADAS + CORREÇÕES

### ZONA 1: Duplicação de código entre módulos
**Risco:** Copiar o core (AgenteBase, logger, database) para cada projeto → código diverge → bugs diferentes em cada módulo.
**Probabilidade:** Alta (acontece em quase todo projecto que cresce).

**Correção:**
- Pasta `/shared/` com código base partilhado
- npm workspaces para importação limpa
- Regra: nunca copiar ficheiros do shared — sempre importar

```javascript
// Em marketing-studio/src/agentes/agente-video.js
import { AgenteBase } from '../../../shared/core/agente-base.js';
```

### ZONA 2: Comunicação frágil entre módulos
**Risco:** Módulo crashar e pedidos ficarem perdidos. Ninguém sabe que falhou.
**Probabilidade:** Alta (sistemas distribuídos falham sempre).

**Correção:**
1. Message Bus local (`shared/core/message-bus.js`) com fila persistente em ficheiro
2. Retry automático com backoff exponencial (1s → 2s → 4s → 8s)
3. Dead Letter Queue — pedidos que falharam 3x vão para `/shared/dead-letters/` para revisão manual
4. Health checks — cada módulo expõe `GET /api/health` com status e timestamp
5. Timeout em cada pedido — se não responde em X minutos, marca como falho

### ZONA 3: Dependência circular entre módulos
**Risco:** A pede a B que precisa de A → deadlock.
**Probabilidade:** Média (acontece quando módulos crescem).

**Correção:**
1. Comunicação unidirecional por pedido: A→B, B responde. B nunca pede a A no mesmo fluxo
2. Se B precisa de A, cria NOVO pedido independente com ID diferente
3. Regra absoluta: nenhum módulo importa código de outro. Só comunicação via Message Bus

### ZONA 4: Marketing Studio sem output real no início
**Risco:** Gastar semanas a estruturar e ter zero vídeos produzidos. Motivação cai.
**Probabilidade:** Alta (armadilha clássica de over-engineering).

**Correção:** MVP brutalmente simples:
1. Receber pedido JSON (1 endpoint)
2. Chamar script Python do Blender headless (1 script)
3. Gerar 1 vídeo com template pré-feito (1 template)
4. Guardar em `/storage/videos/` (1 pasta)
5. Retornar path do vídeo (1 resposta)

Tudo o resto (IA para roteiros, distribuição, múltiplos clientes) é v2+. **Primeiro vídeo real > arquitectura perfeita.**

### ZONA 5: Perder funcionalidade durante a migração
**Risco:** Mover AgenteBlender para o Marketing Studio e o Gadget Hub parar de funcionar.
**Probabilidade:** Alta (migração sempre quebra algo).

**Correção — Migração em 3 fases:**
1. **Copiar:** Duplicar AgenteBlender no Marketing Studio. NÃO remover do Gadget Hub
2. **Ponte:** Criar `agente-marketing-client.js` no Gadget Hub que faz pedidos ao Marketing Studio. Testar em paralelo (ambos a funcionar)
3. **Cortar:** Quando TUDO funciona via Marketing Studio, aí sim remover AgenteBlender do Gadget Hub

**Regra:** nunca remover antes de confirmar que o novo funciona.

### ZONA 6: Configs e secrets espalhados
**Risco:** Cada módulo com `.env` próprio, chaves repetidas, inconsistências.
**Probabilidade:** Média.

**Correção:**
- Um único `.env` na raiz do workspace
- Prefixos por módulo: `GADGET_HUB_PORT=3001`, `MARKETING_STUDIO_PORT=3002`
- Chaves globais sem prefixo: `LLM_API_KEY`, `MODO`

### ZONA 7: Testes inexistentes ou insuficientes
**Risco:** Mudanças grandes sem testes → quebrar silenciosamente.
**Probabilidade:** Alta (projecto actual não tem testes automáticos).

**Correção:**
1. Teste unitário por agente: `agente-video.test.js`, `agente-render.test.js`
2. Teste de integração por módulo: simular pedido → processar → verificar resposta
3. Teste end-to-end: pedido Gadget Hub → Marketing Studio → vídeo de volta
4. Script `npm run test:all` que corre tudo

### ZONA 8: SQLite com conflitos entre módulos
**Risco:** Múltiplos módulos a escrever no mesmo ficheiro SQLite → locks, corrupção.
**Probabilidade:** Alta se partilharem DB.

**Correção:** Cada módulo tem o seu próprio SQLite:
- `/gadget-hub/data/gadget-hub.db`
- `/marketing-studio/data/marketing-studio.db`

Dados partilhados vão sempre via Message Bus, nunca via DB directo.

### ZONA 9: Render local a travar o PC
**Risco:** Correr Blender Cycles com cena pesada no PC → sistema fica inutilizável por horas.
**Probabilidade:** Alta (Cycles é extremamente pesado).

**Correção:**
1. Desenvolvimento e testes: EEVEE sempre (10-50x mais rápido)
2. Produção final: nuvem (GPU dedicada, PC livre)
3. Limite de frames para testes locais: max 30 frames em vez de 120
4. Monitor de recursos: se CPU > 90% por 5 minutos, avisar e sugerir nuvem

### ZONA 10: Gastar orçamento sem controlo
**Risco:** GPU na nuvem a correr sem necessidade, custos acumulam.
**Probabilidade:** Média (fácil esquecer de desligar).

**Correção:**
1. GPU só liga quando há fila de pedidos (não fica idle)
2. Auto-shutdown: se não há pedidos há 15 minutos, desliga
3. Limite diário de custo: max €5/dia (configurable)
4. Log de custos: cada render regista tempo_gpu e custo_estimado
5. Relatório semanal automático de gastos

### ZONA 11: Blender headless falhar silenciosamente
**Risco:** Script Python crashar dentro do Blender e ninguém saber. Vídeo não é gerado.
**Probabilidade:** Alta (erros Python dentro do Blender não são fáceis de capturar).

**Correção:**
1. Wrapper Node.js que executa Blender via `child_process.spawn()`
2. Capturar stdout + stderr do Blender
3. Timeout por render: se não termina em X minutos, matar processo
4. Verificar que ficheiro de output existe após render
5. Se falhar, logar erro completo + mover pedido para Dead Letter Queue

---

## 8. PLANO DE EXECUÇÃO (FASEADO)

### FASE 0 — Preparação do Shared Core (1-2 dias)

- [ ] Criar `/shared/` com `agente-base.js`, `logger.js`, `database.js` (copiados e adaptados do gadget-hub)
- [ ] Criar `message-bus.js` — fila persistente em ficheiro JSON com retry
- [ ] Criar schemas em `/shared/contracts/` (pedido, resultado, health)
- [ ] Criar `validators.js` e `retry.js` em `/shared/utils/`
- [ ] Configurar `package.json` raiz com npm workspaces
- [ ] Mover `.env` para raiz com prefixos por módulo
- [ ] Actualizar `gadget-hub/src/core/config.js` para ler `.env` da raiz
- [ ] Testar: Gadget Hub continua a funcionar normalmente com shared imports

### FASE 1 — Marketing Studio MVP (3-5 dias)

- [ ] Criar estrutura de pastas do `/marketing-studio/`
- [ ] Copiar sub-módulo Blender (`src/agentes/blender/`) para `/marketing-studio/blender/`
- [ ] Criar `agente-video.js` — orquestra o pipeline completo
- [ ] Criar `agente-render.js` — wrapper que executa Blender headless via child_process
- [ ] Criar script Python `render_produto.py` — render básico com template
- [ ] Criar script Python `render_batch.py` — processar fila de 10 vídeos
- [ ] Criar 1 template Blender básico (`produto_360.blend`)
- [ ] Criar API mínima: `POST /api/pedidos`, `GET /api/status`, `GET /api/health`
- [ ] Implementar `/storage/` com organização por categorias
- [ ] Testar: enviar pedido JSON → Marketing Studio gera vídeo → retorna resultado
- [ ] **Critério de sucesso: 1 vídeo gerado automaticamente de ponta a ponta**

### FASE 2 — Integração com Gadget Hub (2-3 dias)

- [ ] Criar `agente-marketing-client.js` no Gadget Hub
- [ ] Adaptar pipeline em `main.js`: onde chamava AgenteBlender → faz pedido ao Marketing Studio
- [ ] Testar comunicação completa: Gadget Hub → Message Bus → Marketing Studio → vídeo → resposta
- [ ] Verificar que toda funcionalidade anterior do Gadget Hub continua a funcionar
- [ ] Correr AgenteBlender original e Marketing Studio em paralelo — confirmar que resultados são iguais

### FASE 3 — Limpeza + Cloud Setup (2-3 dias)

- [ ] Remover AgenteBlender do Gadget Hub (agora vive no Marketing Studio)
- [ ] Simplificar AgenteMarketing do Gadget Hub (fica gestor de campanhas + cliente)
- [ ] Actualizar comandos REPL (cinematic, paletas → proxy para Marketing Studio)
- [ ] Configurar Docker para Blender headless na nuvem
- [ ] Testar render numa GPU cloud (RunPod ou similar)
- [ ] Implementar auto-shutdown e limites de custo
- [ ] Rodar testes completos de todos os módulos

### FASE 4 — Produção e Batch (3-5 dias)

- [ ] Implementar sistema de fila completo (`/queue/`)
- [ ] Criar mais templates Blender (cinematico, viral_tiktok, apresentacao)
- [ ] Implementar batch processing: fila de 10 pedidos → 10 vídeos
- [ ] Adicionar `agente-roteiro.js` — IA gera roteiros a partir de descrição
- [ ] Criar dashboard de monitorização (quantos vídeos, custos, tempo)
- [ ] Testar produção de 10 vídeos/dia durante 3 dias consecutivos
- [ ] **Critério de sucesso: 10 vídeos de qualidade gerados num dia sem intervenção manual**

### FASE 5 — Expansão Marketing Studio (ongoing)

- [ ] Adicionar `agente-distribuicao.js` — publica vídeos automaticamente (redes sociais)
- [ ] Adicionar `agente-assets.js` — gestão de templates, imagens, recursos visuais
- [ ] Implementar suporte a múltiplos clientes (não só Gadget Hub)
- [ ] Criar mais estilos de vídeo (motion graphics, comparação, unboxing)
- [ ] Sistema de repost automático (agendar republicação de vídeos existentes)
- [ ] Integração com thumbnails automáticas

### FASE 6 — App Factory + Blender Control Panel (5-8 dias)

**Prioridade:** O primeiro app criado é a interface do sistema Blender (Marketing Studio).

- [ ] Estruturar `/app-factory/` seguindo mesmo padrão (shared imports, package.json, etc.)
- [ ] Criar `api-scanner.js` — lê endpoints da API do Marketing Studio automaticamente
- [ ] Criar templates base de UI (dashboard, formulários, fila, galeria)
- [ ] Implementar `react-generator.js` — gera componentes React a partir dos templates
- [ ] **PRIMEIRO APP: Blender Control Panel** (`/apps/blender-control-panel/`)
  - [ ] Dashboard.jsx — estado do Blender em tempo real (idle/rendering/erro), custos, métricas
  - [ ] NovoPedido.jsx — formulário visual para criar pedidos (produto, estilo, duração, template, destino)
  - [ ] Fila.jsx — visualização da fila de render (pendentes, em progresso, concluídos, falhados)
  - [ ] Biblioteca.jsx — galeria de vídeos gerados com filtros (categoria, data, produto)
  - [ ] Config.jsx — configuração de templates, motor de render, resolução, limites de custo
  - [ ] RenderStatus.jsx — componente WebSocket que mostra progresso de render em tempo real
  - [ ] VideoPreview.jsx — reproduzir vídeos directamente no browser
  - [ ] CostTracker.jsx — gráfico de custo GPU acumulado (diário/semanal/mensal)
  - [ ] studio-client.js — módulo de chamadas à API do Marketing Studio
- [ ] Testar: criar pedido de vídeo via interface → Marketing Studio processa → ver resultado no app
- [ ] **Critério de sucesso: conseguir gerar os 10 vídeos/dia usando apenas o app, sem terminal**

**Próximos apps (após validar o primeiro):**
- [ ] Segundo app: painel de gestão do Gadget Hub (produtos, preços, campanhas)
- [ ] Terceiro app: interface unificada do Stark Ecosystem (controlo de todos os módulos)

### FASE 7 — Segurança e Regras (após estabilizar)

- [ ] Validação de todos os pedidos entre módulos (JSON Schema)
- [ ] Rate limiting entre módulos (max pedidos por minuto)
- [ ] Logs centralizados de toda comunicação inter-módulos
- [ ] Permissões: quem pode pedir o quê a quem (ACL)
- [ ] Backup automático de dados, vídeos e configurações
- [ ] Alertas automáticos (custo > X, falhas > Y, disco > Z%)

---

## 9. O QUE MANTER, MOVER, ADAPTAR, REMOVER

### MANTER no Gadget Hub (não mexer)
- AgenteShopify — gestão da loja
- AgenteCJ — importação de produtos CJ Dropshipping
- AgentePrecos — cálculo dinâmico de preços
- AgenteEstoque — controlo de stock e alertas
- AgenteAutomacao — FAQs, webhooks, emails, hashtags
- AI Router — comandos em linguagem natural
- API REST + WebSocket
- Dashboard

### MOVER para Marketing Studio
- AgenteBlender inteiro (`src/agentes/blender/`) → base do agente-video + agente-render
- Templates de cena Blender → `/marketing-studio/blender/templates/`
- Scripts Python do Blender → `/marketing-studio/blender/scripts/`
- Docker config do Blender → `/marketing-studio/blender/docker/`
- Funcionalidades cinematográficas (cinematic, paletas, batch) → Marketing Studio

### ADAPTAR no Gadget Hub
- AgenteMarketing → simplificar para gestor de campanhas + cliente do Marketing Studio
- Pipeline em main.js → onde referencia Blender direto, faz pedido via Message Bus
- Comandos REPL (cinematic, paletas, render) → proxy para Marketing Studio
- Config → importar de shared + ler .env da raiz

### REMOVER do Gadget Hub (após migração na Fase 3)
- AgenteBlender (ficheiros, não funcionalidade — agora vive no Marketing Studio)
- Referências diretas a scripts Blender
- Docker configs do Blender

### MOVER para Shared
- `agente-base.js` → `/shared/core/`
- `logger.js` → `/shared/core/`
- `database.js` → `/shared/core/`

---

## 10. REGRAS DE OURO DO ECOSSISTEMA

1. **Cada módulo funciona sozinho.** Desligar o Gadget Hub não afecta o Marketing Studio.
2. **Comunicação só via Message Bus.** Zero imports directos entre projectos.
3. **Shared é read-only.** Mudanças no shared são decisões de arquitectura, não fixes rápidos.
4. **MVP antes de perfeição.** Primeiro vídeo real > arquitectura perfeita.
5. **Testa módulo a módulo.** Nunca testar apenas o sistema completo.
6. **Um `.env`, múltiplos prefixos.** Config centralizada, acesso controlado.
7. **Logs em todo lado.** Toda comunicação entre módulos é logada com timestamp e custo.
8. **GPU só quando precisa.** Nunca idle. Auto-shutdown após 15 minutos sem pedidos.
9. **EEVEE primeiro, Cycles depois.** Velocidade > qualidade perfeita (para marketing).
10. **10 vídeos bons > 100 ruins.** Qualidade e consistência antes de escala.

---

## 11. VISÃO FINAL DO ECOSSISTEMA

```
┌───────────────────────────────────────────────────────────┐
│                    STARK ECOSYSTEM                         │
│                                                            │
│  ┌──────────────┐    pedido    ┌────────────────────┐     │
│  │  GADGET HUB  │────────────→│  MARKETING STUDIO  │     │
│  │  (loja)      │←────────────│  (vídeos/conteúdo) │     │
│  │              │   resultado  │                    │     │
│  │  Port: 3001  │             │  Port: 3002        │     │
│  └──────────────┘             └─────────┬──────────┘     │
│         │                               │                 │
│         │    ┌────────────────┐          │                 │
│         └───→│  APP FACTORY   │←─────────┘                │
│              │  (interfaces)  │                            │
│              │  Port: 3003    │                            │
│              └────────────────┘                            │
│                      │                                     │
│              ┌───────────────┐                             │
│              │    SHARED     │                             │
│              │  (core, bus,  │                             │
│              │   contracts)  │                             │
│              └───────────────┘                             │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  INFRAESTRUTURA                                      │  │
│  │  PC Local: orquestração + dev + testes              │  │
│  │  GPU Cloud: render Blender headless (pay-per-use)   │  │
│  │  Storage Cloud: vídeos + assets (persistente)       │  │
│  │  Orçamento: €50-80/mês (max €200)                   │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## 12. MÉTRICAS DE SUCESSO POR FASE

| Fase | Métrica | Critério de sucesso |
|------|---------|-------------------|
| 0 | Shared funciona | Gadget Hub arranca com imports do shared sem erros |
| 1 | MVP funciona | 1 vídeo gerado automaticamente de ponta a ponta |
| 2 | Integração funciona | Gadget Hub faz pedido → Marketing Studio entrega vídeo |
| 3 | Cloud funciona | 1 vídeo renderizado na nuvem com custo < €0.10 |
| 4 | Produção funciona | 10 vídeos/dia durante 3 dias seguidos sem falhas |
| 5 | Expansão funciona | Vídeos publicados automaticamente em pelo menos 1 rede social |
| 6 | Blender Control Panel funciona | 10 vídeos/dia gerados usando apenas o app (zero terminal) |
| 7 | Segurança funciona | Zero pedidos perdidos durante 1 semana de operação |

---

---

## 13. ASSET LOADER — IMPORTAÇÃO AUTOMÁTICA DE MODELOS 3D

### Conceito

Módulo dentro do Marketing Studio que busca, importa e normaliza modelos 3D de fontes externas (Sketchfab, CGTrader, TurboSquid). Elimina o trabalho manual de procurar, descarregar e corrigir modelos — o sistema faz tudo automaticamente.

### Porquê isto é essencial

Ninguém cria modelos 3D do zero para marketing de produtos. Profissionais usam modelos prontos + adaptam. O Asset Loader automatiza esse fluxo inteiro.

### Regras de licença (OBRIGATÓRIO)

Só aceitar modelos com estas licenças:
- **CC0** (domínio público) — uso livre total, sem restrições
- **CC-BY** (Creative Commons Attribution) — uso comercial permitido, dar crédito ao autor

Rejeitar automaticamente: CC-BY-NC (sem uso comercial), CC-BY-ND (sem modificação), Editorial, Standard paga.

### Pipeline do Asset Loader

```
Busca (query + filtro licença)
        ↓
Download (modelo .glb/.fbx/.obj)
        ↓
Normalização automática
        ↓
Catalogação (metadata + preview)
        ↓
Pronto para uso nos templates
```

### Normalização automática (script Python obrigatório)

Modelos da comunidade vêm quase sempre com problemas. O normalizador corrige tudo antes de usar:

```python
import bpy

def normalizar_modelo(obj):
    """Corrige problemas comuns em modelos importados"""
    
    # 1. Corrigir rotação (muitos vêm com rotação errada)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(rotation=True)
    
    # 2. Corrigir escala (modelos vêm com 100m de altura, etc.)
    # Normalizar para ~1.5m de altura máxima
    dims = obj.dimensions
    max_dim = max(dims)
    if max_dim > 3.0 or max_dim < 0.1:
        target = 1.5
        scale_factor = target / max_dim
        obj.scale *= scale_factor
        bpy.ops.object.transform_apply(scale=True)
    
    # 3. Centralizar na origem
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    
    # 4. Corrigir materiais transparentes
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        if mat and mat.blend_method == 'BLEND':
            mat.blend_method = 'CLIP'  # Evita transparência indesejada
    
    # 5. Limpar objectos vazios (empties) desnecessários
    for child_obj in bpy.data.objects:
        if child_obj.type == 'EMPTY' and len(child_obj.children) == 0:
            bpy.data.objects.remove(child_obj, do_unlink=True)

def importar_e_normalizar(filepath):
    """Importa modelo externo e aplica normalização"""
    ext = filepath.split('.')[-1].lower()
    
    if ext in ('glb', 'gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == 'fbx':
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == 'obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    
    # Normalizar todos os objectos importados
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            normalizar_modelo(obj)
```

### Metadata obrigatório por modelo

```json
{
  "id": "asset_001",
  "nome": "Fone Bluetooth Modelo A",
  "fonte": "sketchfab",
  "url_original": "https://sketchfab.com/...",
  "autor": "username",
  "licenca": "CC-BY",
  "formato": "glb",
  "normalizado": true,
  "categorias": ["electronica", "audio"],
  "data_download": "2026-04-11"
}
```

### Estrutura de pastas

```
/marketing-studio/assets/
├── modelos/
│   ├── electronica/
│   ├── casa/
│   ├── fitness/
│   └── geral/
├── metadata/          ← JSON por modelo (licença, autor, etc.)
└── previews/          ← Thumbnails gerados automaticamente
```

### Integração com o pipeline de render

```
Pedido: "vídeo do Fone X5"
        ↓
Asset Loader: busca modelo "fone" → normaliza → entrega path
        ↓
Template Blender: carrega modelo normalizado → aplica estilo → renderiza
```

---

## 14. PIPELINE 2D — PRODUÇÃO DE VÍDEOS SEM 3D

### Conceito

Nem todo vídeo precisa de render 3D. Vídeos virais (cortes, reels, shorts) são na maioria edição 2D — cortes rápidos, zoom, texto, música. Este pipeline é **muito mais rápido e barato** que o 3D.

### Porquê separar 3D de 2D

| Aspecto | Vídeo 3D (Blender) | Vídeo 2D (FFmpeg/programático) |
|---------|-------------------|-------------------------------|
| Tempo | 2-20 min/vídeo | 30s-2 min/vídeo |
| Custo GPU | €0.02-0.10/vídeo | Quase zero (CPU local) |
| Uso ideal | Produto, branding | Viral, shorts, reels |
| Escala | 10-30/dia | 50-200/dia |

### Distribuição diária recomendada (dos 10 vídeos/dia)

- **2 vídeos 3D** (Blender) — alto impacto, produto, branding
- **8 vídeos 2D** (FFmpeg) — virais, cortes, reels, testes

### Estrutura de um vídeo 2D viral

```
[HOOK]  0-2s   → Texto grande + impacto visual (decide se a pessoa fica)
[CORPO] 2-8s   → Cortes rápidos + zoom dinâmico + informação
[CTA]   8-15s  → Engajamento ("segue para mais", loop)
```

### Motor principal: FFmpeg (gratuito, rápido, scriptável)

```bash
# Exemplo: criar vídeo com texto sobreposto + música
ffmpeg -i clip_base.mp4 \
  -vf "drawtext=text='VOCE SABIA?':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=100" \
  -i musica.mp3 -shortest \
  -c:v libx264 -preset fast \
  output_viral.mp4
```

**Operações automatizáveis:**
- Cortes automáticos (dividir vídeo longo em clips curtos)
- Zoom dinâmico (scale + crop por keyframe)
- Texto animado (legendas, hooks, CTAs)
- Overlay de música (sincronizar beat com cortes)
- Resize automático (horizontal → vertical para Shorts/Reels)
- Concatenação (juntar múltiplos clips)
- Geração de thumbnails

### Integração no Marketing Studio

O `agente-video.js` decide qual pipeline usar baseado no pedido:

```javascript
async processarPedido(pedido) {
    if (pedido.tipo === '3d' || pedido.estilo === 'cinematografico') {
        return this.pipeline3D(pedido);  // Blender headless
    } else {
        return this.pipeline2D(pedido);  // FFmpeg rápido
    }
}
```

---

## 15. BACKEND ENGINE — SHOPIFY AUTOMATIZADO COM PYTHON

### Conceito

Controlar a loja Shopify inteiramente via código Python usando a API oficial. Cadastrar produtos em massa, sincronizar preços com câmbio, controlar estoque automaticamente.

### Três funções core

#### 1. Cadastro automático de produtos

```python
import shopify
import time

# Configurar sessão
shopify.ShopifyResource.set_site("https://SUA-LOJA.myshopify.com/admin/api/2024-01")
shopify.ShopifyResource.set_headers({'X-Shopify-Access-Token': 'TOKEN'})

def cadastrar_produto(dados):
    """Cria produto na Shopify a partir de dados do fornecedor"""
    produto = shopify.Product()
    produto.title = dados['nome']
    produto.body_html = dados['descricao']
    produto.vendor = dados.get('marca', 'Gadget Hub')
    produto.product_type = dados['categoria']
    produto.tags = dados.get('tags', '')
    
    variante = shopify.Variant({
        'price': str(dados['preco']),
        'compare_at_price': str(dados.get('preco_original', '')),
        'inventory_quantity': dados.get('stock', 0),
        'sku': dados.get('sku', '')
    })
    produto.variants = [variante]
    
    if dados.get('imagem_url'):
        produto.images = [shopify.Image({'src': dados['imagem_url']})]
    
    sucesso = produto.save()
    return {'id': produto.id, 'sucesso': sucesso}

def cadastrar_em_massa(lista_produtos):
    """Cadastra lista inteira de produtos"""
    resultados = []
    for dados in lista_produtos:
        resultado = cadastrar_produto(dados)
        resultados.append(resultado)
        time.sleep(0.5)  # Respeitar rate limit da API
    return resultados
```

#### 2. Actualização automática de preços (baseado em câmbio)

```python
import requests

def obter_taxa_cambio(moeda_origem='USD', moeda_destino='EUR'):
    resp = requests.get(f"https://api.exchangerate-api.com/v4/latest/{moeda_origem}")
    return resp.json()['rates'][moeda_destino]

def actualizar_precos(margem=0.35):
    taxa = obter_taxa_cambio('USD', 'EUR')
    produtos = shopify.Product.find()
    
    for produto in produtos:
        for variante in produto.variants:
            preco_base_usd = float(variante.price)
            novo_preco = round(preco_base_usd * taxa * (1 + margem), 2)
            variante.price = str(novo_preco)
        produto.save()
        time.sleep(0.5)
```

#### 3. Sincronização de estoque

```python
def sincronizar_estoque(dados_fornecedor):
    for item in dados_fornecedor:
        produtos = shopify.Product.find(title=item['nome'])
        if produtos:
            produto = produtos[0]
            for variante in produto.variants:
                variante.inventory_quantity = item['stock']
            produto.save()
```

### Protecções obrigatórias

- **Rate limiting:** max 2 requests/segundo à API Shopify
- **Validação:** nunca publicar produto sem título, preço e pelo menos 1 imagem
- **Backup:** exportar CSV antes de actualização em massa
- **Dry-run:** opção de simular sem aplicar
- **Rollback:** guardar preços anteriores para reverter se necessário

### Como executar Python a partir do Node.js

```javascript
// gadget-hub/src/agentes/agente-shopify.js
import { execSync } from 'child_process';

function actualizarPrecos() {
    const resultado = execSync('python3 scripts/actualizar_precos.py', {
        encoding: 'utf-8',
        timeout: 60000
    });
    return JSON.parse(resultado);
}
```

---

## 16. CUSTOM APP ENGINE — APPS PYTHON + N8N COMO PONTE

### Conceito

Apps externos em Python (Flask/Django) para funcionalidades que a Shopify não tem. O n8n actua como ponte de automação entre todos os sistemas.

### Arquitectura

```
Shopify (loja) → webhook → n8n (automação) → HTTP → App Python (Flask) → Resposta
```

### Fluxos automatizados via n8n

| Trigger | Acção |
|---------|-------|
| Novo produto criado na Shopify | → Python gera descrição com IA → actualiza produto |
| Novo pedido recebido | → Notifica + envia para CJ |
| Produto sem stock | → Desactiva na loja + alerta |
| Novo produto importado | → Marketing Studio cria vídeo automaticamente |
| Preço do dólar muda >2% | → Backend Engine recalcula todos os preços |

### Fase de implementação

- **v1:** App Flask simples com 1-2 endpoints (recomendação, health)
- **v2:** Conectar via n8n com webhooks da Shopify
- **v3:** Mais funcionalidades (pricing dinâmico, analytics, IA)

---

## 17. ESTRATÉGIA DE CONTEÚDO POR NICHO

### Mapeamento nicho → tipo de produção

| Nicho | % 3D | % 2D | Estilo dominante |
|-------|------|------|-----------------|
| Produtos/E-commerce | 60% | 40% | Cinematográfico, produto_360 |
| Carros | 20% | 80% | Cortes rápidos, zoom, música energética |
| Curiosidades | 10% | 90% | Texto grande, ritmo acelerado |
| Marketing digital | 0% | 100% | Storytelling, legendas, dicas |
| Tecnologia | 40% | 60% | Reviews, comparações |
| Entretenimento/Viral | 10% | 90% | Loop, impacto visual |

### Template de conteúdo por nicho

```json
{
  "nicho": "produtos_ecommerce",
  "regras": {
    "hook_max_segundos": 2,
    "duracao_ideal": "15-30s",
    "formato": "1080x1920",
    "musica": "ambiente_premium",
    "estilo_visual": "fundo_escuro_luz_lateral"
  },
  "templates_3d": ["produto_360", "cinematico_basico"],
  "templates_2d": ["zoom_produto", "antes_depois", "comparacao"],
  "exemplos_hook": [
    "Este gadget custa menos de 20 euros...",
    "Nunca mais vais usar fios...",
    "O que 15 euros te compram em 2026..."
  ]
}
```

### Regras universais que funcionam em qualquer nicho

1. Cortar ANTES de ficar chato (média 1-3s por cena)
2. Zoom leve a cada corte (sensação de movimento)
3. Música dita o ritmo — cortes seguem o beat
4. Texto grande e directo (legível em mobile)
5. Primeiros 2 segundos decidem tudo

### Estratégia de crescimento por conta

- **Frequência mínima:** 5-10 vídeos/dia por conta
- **Dias 1-7:** quase zero tração (normal)
- **Dias 7-30:** primeiros vídeos com alcance
- **Dias 30-60:** padrão identificado, crescimento real
- **NUNCA** misturar nichos na mesma conta

---

## 18. WEB FACTORY — CONFIGURAÇÃO DE SITES DETALHADA

### Knowledge base de configuração de loja

| Módulo | Função | Prioridade |
|--------|--------|-----------|
| Branding | Logo (max 300px), texto alt | Alta |
| Color System | Até 21 esquemas, gradientes CSS | Alta |
| Tipografia | Fontes sistema (recomendado) vs custom, escala 100-150% | Alta |
| Animações | Fade-in scroll, hover (elevação vertical/3D) | Média |
| Carrinho | Deslizante (recomendado) / Página / Pop-up | Crítica |
| Moeda | Código visível (EUR, USD) | Média |
| CSS Custom | Biblioteca de estilos reutilizáveis | Média |
| Pesquisa | Preditiva com preço e fabricante | Média |

### Regras de conversão

1. **Carrinho deslizante** — SEMPRE (cliente não sai da página)
2. **Máximo 3 cores** na paleta principal
3. **Fontes do sistema** quando possível (carregamento rápido)
4. **Animações subtis** — nunca exagerar
5. **CTA visível** — cor contrastante, sempre acessível
6. **Mobile-first** — 70%+ do tráfego é mobile
7. **Imagens optimizadas** — sem 4K desnecessário

---

*Última actualização: 2026-04-11 — Versão 3.4*
*Adições V3.4: Asset Loader (sec.13), Pipeline 2D (sec.14), Backend Engine Shopify (sec.15), Custom App + n8n (sec.16), Estratégia de Nicho (sec.17), Web Factory detalhado (sec.18)*
*Próxima revisão: após conclusão da Fase 0*
