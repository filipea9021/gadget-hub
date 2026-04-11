# 🧠 Cerebro Centram

Sistema autônomo de skills com IA para operar uma startup de forma automatizada.

## Setup Rápido

```bash
# 1. Instalar dependências
pip install -e ".[dev]"

# 2. Configurar ambiente
cp .env.example .env
# Edite .env com sua API key (ou use Ollama para rodar local sem custo)

# 3. Verificar status
python core/cli.py status
```

## Uso

### Modo Interativo (recomendado para começar)
```bash
python core/cli.py interactive
```

### Modo Direto
```bash
python core/cli.py generate \
  --name "minha-landing" \
  --desc "Landing page para app de gestão de tarefas com IA" \
  --feature "Hero com animação" \
  --feature "Seção de pricing" \
  --feature "FAQ interativo" \
  --type landing_page
```

### Ver Status
```bash
python core/cli.py status
```

## Providers de LLM

| Provider | Config no .env | Custo | Qualidade |
|----------|---------------|-------|-----------|
| Anthropic (Claude) | `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` | Pago | Excelente |
| OpenAI (GPT-4) | `LLM_PROVIDER=openai` + `OPENAI_API_KEY` | Pago | Muito boa |
| Ollama (local) | `LLM_PROVIDER=ollama` | Grátis | Boa (depende do modelo) |

### Usar Ollama (grátis)
```bash
# Instalar Ollama: https://ollama.ai
ollama pull llama3.1
# No .env: LLM_PROVIDER=ollama
```

## Estrutura do Projeto

```
cerebro-centram/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configurações centrais
├── core/
│   ├── __init__.py
│   ├── cli.py               # Interface de linha de comando
│   ├── llm.py               # Abstração para LLMs (Claude/GPT/Ollama)
│   └── models.py            # Modelos de dados compartilhados
├── skills/
│   └── dev/
│       ├── __init__.py
│       ├── agent.py          # Skill Dev — agente de desenvolvimento
│       └── prompts.py        # System prompts e templates
├── templates/
│   └── landing_page.json     # Template padrão para landing pages
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Roadmap

- [x] **Fase 1a** — Skill Dev (geração de código)
- [ ] **Fase 1b** — Cérebro Central (orquestrador com LangGraph)
- [ ] **Fase 1c** — Deploy automático (GitHub + Vercel)
- [ ] **Fase 2** — Skills Marketing + Design
- [ ] **Fase 3** — Skills SEO + Produto + Dashboard
- [ ] **Fase 4** — Benchmarking + Ciclo inteligente

## Próximos Passos

1. Configurar API key (Anthropic, OpenAI ou Ollama)
2. Testar geração de uma landing page simples
3. Implementar o Cérebro Central com LangGraph
4. Adicionar deploy automático via GitHub API + Vercel
