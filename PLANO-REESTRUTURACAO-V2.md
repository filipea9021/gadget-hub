# PLANO DE REESTRUTURAÇÃO — GADGET HUB v2.0

**Data:** 2026-04-08  
**Objetivo:** Unificar os 3 sistemas (Agentes Node.js + Skills + Cérebro Centram) num motor único e coeso, com o sistema de agentes Node.js como core.

---

## 1. ESTRUTURA ATUAL vs NOVA

### Hoje (fragmentado)
```
gadget-hub/
├── agentes/          ← Motor principal (Node.js) — funciona isolado
├── sistema/          ← Skills legacy (JS) — duplica lógica dos agentes
├── cerebro-centram/  ← IA em Python — não conversa com os agentes
├── shopify-theme/    ← Customizações Liquid — soltas
├── automation/       ← Vazio/configs
├── workflows/        ← JSONs de n8n — sem conexão ao código
├── DPLL/             ← Docs técnicos avulsos
├── docs/             ← Documentação boa mas espalhada
├── aruivo pro X01/   ← Pipeline de vídeo (fora do escopo agora)
├── index.html        ← Protótipos HTML (referência visual)
├── produto.html
├── checkout.html
└── ... (arquivos soltos)
```

### Nova Estrutura (unificada)
```
gadget-hub/
│
├── src/                          ← TODO O CÓDIGO VIVE AQUI
│   ├── core/                     ← Núcleo do sistema
│   │   ├── agente-base.js        ← Classe base (atualizada)
│   │   ├── manager.js            ← Orquestrador de agentes (refatorado)
│   │   ├── database.js           ← SQLite (sem mudança)
│   │   ├── notificador.js        ← Notificações (expandido)
│   │   ├── config.js             ← ★ NOVO: Config centralizada (.env → objeto)
│   │   └── logger.js             ← ★ NOVO: Logger estruturado
│   │
│   ├── agentes/                  ← Agentes especializados
│   │   ├── agente-cj.js          ← CJ Dropshipping (+ lógica do skill1)
│   │   ├── agente-shopify.js     ← Shopify (+ webhooks do skill4)
│   │   ├── agente-estoque.js     ← Estoque (sem mudança significativa)
│   │   ├── agente-precos.js      ← Preços (sem mudança significativa)
│   │   ├── agente-marketing.js   ← Marketing (+ copy do skill3)
│   │   └── agente-automacao.js   ← ★ NOVO: Chatbot + FAQs + Webhooks (do skill4)
│   │
│   ├── ai/                       ← ★ NOVO: Módulo de IA (Cérebro migrado)
│   │   ├── llm-client.js         ← Cliente LLM em Node (Claude/GPT/Ollama)
│   │   ├── router.js             ← Roteamento inteligente de comandos
│   │   └── prompts.js            ← Templates de prompts para cada agente
│   │
│   ├── api/                      ← ★ NOVO: API REST unificada
│   │   ├── server.js             ← Express server (dashboard + API)
│   │   ├── routes/
│   │   │   ├── agentes.js        ← CRUD + controle de agentes
│   │   │   ├── produtos.js       ← Consulta/gestão de produtos
│   │   │   ├── brain.js          ← Endpoint do Cérebro (comandos IA)
│   │   │   └── webhooks.js       ← Receber webhooks (Shopify, CJ)
│   │   └── middleware/
│   │       ├── auth.js           ← Autenticação básica
│   │       └── rate-limit.js     ← Rate limiting
│   │
│   └── dashboard/                ← Frontend do painel
│       └── public/
│           └── index.html        ← Dashboard SPA
│
├── config/                       ← Configurações
│   ├── .env.example              ← Template de variáveis
│   ├── agents.config.js          ← Intervalos, limites, regras por agente
│   └── shopify.config.js         ← Dados da loja Shopify
│
├── data/                         ← Dados persistentes (gitignored)
│   ├── gadgethub.db              ← SQLite
│   └── relatorios/               ← Relatórios exportados
│
├── workflows/                    ← Workflows n8n (mantidos)
│   └── *.json
│
├── shopify-theme/                ← Customizações Liquid (mantidas)
│   ├── sections/
│   └── snippets/
│
├── docs/                         ← Documentação consolidada
│   ├── arquitetura.md            ← ★ NOVO: Diagrama de arquitetura
│   ├── api-reference.md          ← ★ NOVO: Referência da API
│   ├── guia-operacao.md          ← Manual de operação
│   └── analises/                 ← Análises de mercado/concorrência
│
├── archive/                      ← ★ NOVO: Código legado preservado
│   ├── sistema/                  ← Skills originais (referência)
│   ├── cerebro-centram/          ← Cérebro Python (referência)
│   ├── prototipos-html/          ← index.html, produto.html, checkout.html
│   └── primeiro-site/            ← Site original
│
├── main.js                       ← Entry point único
├── package.json                  ← Dependências atualizadas
├── .env                          ← Variáveis de ambiente (gitignored)
├── .gitignore
└── README.md                     ← Atualizado
```

---

## 2. O QUE MUDA EM CADA PEÇA

### 2.1 — Core: Config Centralizada (`src/core/config.js`)
**Problema atual:** Variáveis de ambiente espalhadas em cada arquivo.  
**Solução:** Um módulo `config.js` que:
- Carrega `.env` com `dotenv`
- Valida variáveis obrigatórias no boot
- Exporta objeto tipado com todas as configs
- Detecta modo (dev/demo/produção) automaticamente

```js
// Exemplo de uso em qualquer arquivo:
import config from '../core/config.js';
config.shopify.domain  // 'gadget-hub-72955.myshopify.com'
config.cj.apiKey       // process.env.CJ_API_KEY ou null (modo demo)
config.mode            // 'demo' | 'semi' | 'autonomo'
```

### 2.2 — Absorção dos Skills nos Agentes

| Skill Original | Lógica | Destino | Status |
|---|---|---|---|
| skill1 (Produtos) | `pesquisarProdutos()`, `validarProdutos()`, `calcularScore()` | `agente-cj.js` | ⚡ Já duplicado — remover skill1 |
| skill2 (Site) | `gerarPaginasProdutos()` — placeholder sem lógica real | Descartado | 🗑️ Era placeholder |
| skill3 (Marketing) | `gerarCopy()`, `gerarHashtags()`, templates de gatilhos | `agente-marketing.js` | ⚡ Já duplicado — adicionar hashtags |
| skill4 (Automação) | FAQs, `processarWebhook()`, `enviarEmail()` | Novo `agente-automacao.js` | 🆕 Migrar |

**Novo agente-automacao.js** concentra:
- Respostas automáticas (FAQs de entrega, devolução, pagamento, MBWay)
- Processamento de webhooks Shopify (pedido criado/enviado/entregue/carrinho abandonado)
- Emails transacionais (confirmação, envio, abandono)
- Chatbot rules-based para atendimento básico

### 2.3 — Módulo de IA (`src/ai/`) — Cérebro em Node.js

**Problema atual:** Cérebro é Python, agentes são Node.js. A comunicação é por subprocess (lenta e frágil).  
**Solução:** Reimplementar a lógica do Cérebro em Node.js puro.

O que migramos do Python:
- **LLM Client** → `llm-client.js`: Chamadas à API do Claude/GPT direto em Node (fetch)
- **Router** → `router.js`: Recebe comando em linguagem natural → decide qual agente(s) executar
- **Prompts** → `prompts.js`: Templates de prompt para cada tipo de decisão

O que NÃO migramos (não é necessário agora):
- LangGraph (excesso de complexidade para a fase atual)
- FastAPI (substituído pelo Express já existente)
- JSBridge (eliminado — tudo é Node agora)

**Fluxo com IA:**
```
Comando: "Importar smart plugs baratos e lançar campanha TikTok"
         │
    ┌────▼─────┐
    │  Router   │ → LLM analisa → {agentes: ['cj', 'marketing'], sequência: true}
    └────┬─────┘
         │
    ┌────▼─────┐
    │ AgenteCJ  │ → pesquisa + valida → produtos encontrados
    └────┬─────┘
         │ (resultado passa como contexto)
    ┌────▼──────────┐
    │ AgenteMarketing│ → gera campanha TikTok para os produtos
    └───────────────┘
```

### 2.4 — API Unificada (`src/api/`)

Substituir o dashboard isolado por uma API completa:

| Endpoint | Método | Descrição |
|---|---|---|
| `/api/status` | GET | Status geral do sistema |
| `/api/agentes` | GET | Lista todos os agentes e estado |
| `/api/agentes/:id/executar` | POST | Executar agente manualmente |
| `/api/agentes/iniciar` | POST | Iniciar execução contínua |
| `/api/agentes/parar` | POST | Parar execução |
| `/api/produtos` | GET | Listar produtos (filtros) |
| `/api/produtos/:id` | GET | Detalhes do produto |
| `/api/brain` | POST | Enviar comando ao Cérebro IA |
| `/api/webhooks/shopify` | POST | Receber webhooks Shopify |
| `/api/webhooks/cj` | POST | Receber webhooks CJ |
| `/api/logs` | GET | Logs do sistema |
| `/api/metricas` | GET | Métricas e KPIs |

WebSocket mantido para updates em tempo real no dashboard.

### 2.5 — Entry Point (`main.js`)

Simplificado para:
```js
import { Config } from './src/core/config.js';
import { Manager } from './src/core/manager.js';
import { startAPI } from './src/api/server.js';

// 1. Carregar config
const config = Config.load();

// 2. Inicializar manager com todos os agentes
const manager = new Manager(config);
await manager.inicializar();

// 3. Subir API + Dashboard
startAPI(manager, config);

// 4. Modo de execução
if (config.mode === 'autonomo') manager.iniciarTodos();
```

---

## 3. ORDEM DE EXECUÇÃO (FASES)

### Fase A — Estrutura Base (fazer primeiro)
1. Criar nova árvore de pastas (`src/`, `config/`, `archive/`)
2. Mover arquivos existentes para os novos locais
3. Criar `config.js` centralizado + `.env.example`
4. Criar `logger.js` padronizado
5. Atualizar imports em todos os arquivos
6. Testar boot do sistema (sem erros de import)

### Fase B — Absorção dos Skills
1. Adicionar lógica de hashtags do skill3 ao `agente-marketing.js`
2. Criar `agente-automacao.js` com lógica do skill4 (FAQs + webhooks)
3. Registrar novo agente no manager
4. Mover `sistema/` para `archive/`
5. Testar comunicação entre agentes

### Fase C — Módulo de IA
1. Criar `llm-client.js` (fetch para Claude API)
2. Criar `router.js` (routing de comandos naturais → agentes)
3. Criar `prompts.js` (templates por tipo de operação)
4. Integrar router no manager (comando → agente(s))
5. Mover `cerebro-centram/` para `archive/`

### Fase D — API Unificada
1. Refatorar `dashboard/server.js` → `src/api/server.js`
2. Criar rotas separadas (agentes, produtos, brain, webhooks)
3. Adicionar endpoint `/api/brain` conectado ao módulo IA
4. Manter WebSocket para dashboard em tempo real
5. Frontend do dashboard (mínimo funcional)

### Fase E — Validação
1. Boot completo em modo demo (sem API keys)
2. Boot completo em modo semi (REPL funcional)
3. Testar cada endpoint da API
4. Testar comunicação inter-agentes (CJ → Shopify → Estoque)
5. Testar comando via Cérebro IA
6. Documentar nova arquitetura

---

## 4. DEPENDÊNCIAS A ADICIONAR

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "node-fetch": "^3.3.2",
    "sqlite3": "^5.1.6",
    "sqlite": "^4.2.1",
    "ws": "^8.16.0",
    "dotenv": "^16.4.0"
  }
}
```
*Nota: `dotenv` é a única dependência nova. O módulo de IA usa fetch nativo do Node 18+.*

---

## 5. VARIÁVEIS DE AMBIENTE (`.env.example`)

```bash
# === MODO DE OPERAÇÃO ===
MODO=semi                    # manual | semi | autonomo

# === SHOPIFY ===
SHOPIFY_SHOP_DOMAIN=gadget-hub-72955.myshopify.com
SHOPIFY_ACCESS_TOKEN=
SHOPIFY_API_VERSION=2024-01

# === CJ DROPSHIPPING ===
CJ_API_KEY=
CJ_EMAIL=
CJ_API_SECRET=

# === IA (opcional — funciona sem) ===
AI_PROVIDER=anthropic        # anthropic | openai | ollama
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# === NOTIFICAÇÕES (opcional) ===
WEBHOOK_URL=
NOTIFICATION_EMAIL=

# === SERVIDOR ===
PORT=3001
LOG_LEVEL=info
```

---

## 6. O QUE NÃO MUDA

- **Shopify Theme** (`shopify-theme/`) — continua no lugar, é deploy separado
- **Workflows n8n** (`workflows/`) — continuam como estão, configuração externa
- **Dados** (`data/`) — SQLite e relatórios mantidos
- **Lógica interna dos agentes** — o código dos 5 agentes existentes não é reescrito, apenas reorganizado e com imports atualizados

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Mitigação |
|---|---|
| Quebrar imports ao mover arquivos | Fase A termina com teste de boot obrigatório |
| Perder lógica dos skills | Tudo vai para `archive/` antes de ser removido |
| Módulo IA não funcionar sem API key | Modo fallback: routing por keywords (como o orquestrador fazia) |
| Dashboard parar de funcionar | Migração incremental — só desliga o antigo quando o novo funciona |
