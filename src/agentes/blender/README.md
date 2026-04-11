# Agente Blender — Renders 3D & Animações

Motor de renderização 3D automatizado para produtos do catálogo Gadget Hub.

## Arquitetura

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Agente CJ   │────▶│ Agente Blender  │────▶│ Agente Shopify   │
│ (encontra     │     │ (Node.js)       │     │ (atualiza imagens│
│  produtos)    │     │ gerencia jobs   │     │  no produto)     │
└──────────────┘     └────────┬────────┘     └──────────────────┘
                              │
                              │ HTTP POST /api/jobs
                              ▼
                     ┌─────────────────┐
                     │ Blender Server  │
                     │ (Docker/Cloud)  │
                     │ FastAPI + Blender│
                     │ headless        │
                     └────────┬────────┘
                              │
                              │ blender --background --python
                              ▼
                     ┌─────────────────┐
                     │ render_engine.py│
                     │ • Gera modelo   │
                     │ • Materiais PBR │
                     │ • Iluminação    │
                     │ • Camera setup  │
                     │ • Render/Export │
                     └─────────────────┘
```

## Pipeline por Produto

1. **CJ encontra produto** → emite `novos_produtos_validados`
2. **Agente Blender** seleciona template por categoria (ex: `audio_wearable` para fones)
3. **Cria job** com tipos de render relevantes (hero, multi-angle, turntable, exploded)
4. **Submete ao servidor** Blender via API REST
5. **Servidor executa** Blender headless com o `render_engine.py`
6. **Resultados** voltam: PNGs (renders) + MP4s (animações)
7. **Agente notifica Shopify** → atualiza imagens do produto
8. **Notifica Marketing** → renders disponíveis para campanhas

## Tipos de Render

| Tipo | Output | Descrição |
|------|--------|-----------|
| **Hero Shot** | 1 PNG (1920x1920) | Foto principal, ângulo 3/4, iluminação studio |
| **Multi-Angle** | 4 PNGs (1200x1200) | Frente, lado, trás, topo — fundo transparente |
| **Turntable 360°** | 1 MP4 (1080x1080, 4s) | Rotação completa do produto |
| **Exploded View** | 1 MP4 (1920x1080, 3s) | Peças se separam mostrando componentes |
| **Lifestyle** | 1 PNG (1920x1080) | Produto em contexto real com HDRI |

## Templates de Cena

23 templates pré-configurados cobrindo todas as categorias:
`electronics_small`, `audio_wearable`, `audio_speaker`, `lighting_strip`, `wearable_watch`, `smarthome_plug`, `gaming_controller`, `gaming_mouse`, `phone_case`, e mais.

Cada template define: materiais, iluminação, câmera e quais renders são relevantes.

## Uso

### Modo Demo (sem servidor)
Funciona automaticamente quando o servidor Blender não está disponível.
Simula jobs e retorna metadados realistas.

### Modo Produção

```bash
# 1. Subir servidor Blender
cd agentes/blender/docker
docker-compose up -d

# 2. Iniciar sistema de agentes
cd ../../
MODO=semi node main.js

# 3. Comandos manuais
> render({id: 'PROD001', nome: 'Smart Plug WiFi', sku: 'SP001', categoria: 'smart_plug'}, ['hero', 'multiAngle'])
> renderCompleto({id: 'PROD002', nome: 'Fone Bluetooth', sku: 'FB001', categoria: 'fone'})
> renderStatus()
> templates()
```

### Variáveis de Ambiente

```bash
BLENDER_SERVER_URL=http://localhost:8585   # URL do servidor
BLENDER_API_KEY=                           # Chave de API (opcional)
```

## Estrutura de Arquivos

```
blender/
├── agente-blender.js          ← Agente Node.js (gestão de jobs)
├── scripts/
│   └── render_engine.py       ← Motor Blender (geometria, materiais, render)
├── templates/
│   └── scene-configs.json     ← Configuração por categoria de produto
├── docker/
│   ├── Dockerfile             ← Imagem Docker com Blender 4.1
│   ├── docker-compose.yml     ← Orquestração do container
│   └── server.py              ← API FastAPI do servidor de render
├── output/                    ← Renders gerados (por SKU)
└── README.md
```

## Materiais PBR Disponíveis

O `render_engine.py` inclui materiais profissionais:
`plastic_glossy`, `plastic_matte`, `metal_brushed`, `glass_screen`, `rubber_soft`, `led_emissive`, `fabric_mesh`

## Modelos Procedurais

10 geradores de modelos 3D procedurais:
Eletrônicos, earbuds, speakers, fitas LED, smartwatches, smart plugs, controles, mouses, capinhas, e genérico.

Para modelos mais detalhados, colocar arquivos `.blend` ou `.obj` na pasta `templates/models/`.

---

## Motor Cinematográfico (`cinematic_engine.py`)

Sistema de vídeos premium com efeitos avançados — reutilizável como "fábrica de conteúdo".

### Conceito

1 template = N vídeos. Troca o objeto, a cor e o estilo de câmera → novo conteúdo.

### Efeitos Disponíveis

| Efeito | Descrição |
|--------|-----------|
| **Energy Core** | Esfera emissiva pulsante no centro do objeto — glow volumétrico |
| **Partículas: Sparks** | Faíscas saindo do centro com física Newton |
| **Partículas: Dust** | Poeira flutuante no ambiente (movimento browniano) |
| **Partículas: Fragments** | Fragmentos maiores saindo durante explosão |
| **Camadas Internas** | Wireframe tech + emissão + metal interno visíveis na desmontagem |
| **Desmontagem Procedural** | Explosão sequencial camada por camada com rotação |
| **Motion Blur** | Desfoque de movimento cinematográfico |
| **Iluminação Dual-Tone** | Luz fria (azul) de um lado, quente (laranja) do outro — look sci-fi |

### Paletas de Cor

| Paleta | Look |
|--------|------|
| `tech_blue` | Azul elétrico — o clássico sci-fi |
| `energy_orange` | Laranja energia — quente e dinâmico |
| `cyber_purple` | Roxo cyber — futurista e misterioso |
| `matrix_green` | Verde matrix — digital e hacker |
| `fire_red` | Vermelho fogo — intenso e poderoso |
| `ice_white` | Branco gelo — clean e premium |

### Estilos de Câmera

| Estilo | Movimento |
|--------|-----------|
| `orbit_zoom` | Órbita suave com zoom lento (clássico) |
| `push_in` | Avanço dramático em linha reta |
| `reveal` | Começa de perto (blur), afasta revelando o objeto |

### Objetos Base

| Tipo | Uso |
|------|-----|
| `sphere` | Tech/sci-fi/conteúdo viral |
| `cube` | Minimalista/branding |
| `torus` | Futurista/abstrato |
| `product` | Usa o gerador de produtos do render_engine |

### Comandos (modo semi-autônomo)

```bash
# Vídeo cinematográfico de um produto (com desmontagem)
> cinematic({id: 'P1', nome: 'Fone BT', sku: 'FB01', categoria: 'fone'}, {palette: 'cyber_purple'})

# Conteúdo abstrato para redes sociais
> cinematicContent('sphere', {palette: 'tech_blue', cameraStyle: 'push_in'})

# Batch automático — 6 vídeos com combinações variadas
> cinematicBatch()

# Batch manual
> cinematicBatch([
    {objectType: 'sphere', palette: 'tech_blue', cameraStyle: 'orbit_zoom'},
    {objectType: 'cube', palette: 'fire_red', cameraStyle: 'push_in'},
    {objectType: 'torus', palette: 'cyber_purple', cameraStyle: 'reveal'}
  ])

# Ver paletas disponíveis
> paletas()
```

### Output por Job Cinematográfico

Cada job gera:
- 1 **vídeo MP4** (4-6 segundos, 1920x1080)
- 1 **thumbnail PNG** (frame do meio)
- 4 **keyframes PNG** (frames-chave da animação)

### Estrutura Atualizada

```
blender/
├── agente-blender.js              ← Agente (jobs normais + cinematográficos)
├── scripts/
│   ├── render_engine.py           ← Motor base (produtos, materiais, cenas)
│   └── cinematic_engine.py        ← Motor cinematográfico (efeitos avançados)
├── templates/
│   └── scene-configs.json         ← Config por categoria
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── server.py                  ← API do servidor
├── output/                        ← Renders e vídeos gerados
└── README.md
```
