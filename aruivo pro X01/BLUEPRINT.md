# CONTENT INTELLIGENCE SYSTEM (CIS) — Blueprint v2.0

## 1. VISÃO GERAL

Sistema de IA que gera conteúdo viral baseado em **dados reais**, não geração aleatória.
Arquitetura modular com agentes especializados coordenados por um orquestrador central.

**Princípio central:** Nenhum conteúdo é inventado do zero — tudo é derivado de padrões comprovados, recombinados de forma original.

---

## 2. ARQUITETURA

```
┌─────────────────────────────────────────────────┐
│                   TELEGRAM BOT                   │
│              (Interface do Usuário)               │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                  ORCHESTRATOR                     │
│  - Interpreta prompt                             │
│  - Decide pipeline (quais módulos rodar)         │
│  - Gerencia estado da execução                   │
│  - Valida saídas entre etapas                    │
└──────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
  INTELLIGENCE  CREATION  PRODUCTION  OPTIMIZATION
   MODULES      MODULES    MODULES     MODULES
```

### 2.1 Pipeline de Execução

Cada requisição passa por um **pipeline dinâmico** — o orquestrador decide quais etapas são necessárias:

| Etapa | Módulo | Entrada | Saída |
|-------|--------|---------|-------|
| 1 | `Scraper` | Prompt + nicho | Referências coletadas |
| 2 | `Analyzer` | Referências | Análise estrutural |
| 3 | `DNA Extractor` | Análise | Padrões virais (hooks, estrutura, CTAs) |
| 4 | `Idea Generator` | DNA + Prompt | 3-5 ideias ranqueadas |
| 5 | `Creative Booster` | Ideia escolhida | Ideia expandida com ângulos únicos |
| 6 | `Script Writer` | Ideia expandida | Roteiro completo |
| 7 | `Validator` | Roteiro | Score de qualidade + ajustes |
| 8 | `Optimizer` | Roteiro validado | Versão otimizada para plataforma |

---

## 3. COMPONENTES DETALHADOS

### 3.1 Orchestrator (`core/orchestrator.py`)

```python
# Responsabilidades:
# 1. Parsear o prompt do usuário em dados estruturados
# 2. Decidir qual pipeline executar
# 3. Passar contexto entre módulos
# 4. Controlar retry em caso de falha
# 5. Salvar resultado na memória

# Input: prompt do usuário (string)
# Output: conteúdo finalizado + metadados
```

**Tipos de pipeline:**
- `full` — Pipeline completo (pesquisa → roteiro → otimização)
- `quick` — Só geração (pula pesquisa, usa memória)
- `research_only` — Só pesquisa e análise
- `optimize` — Recebe roteiro pronto e otimiza

### 3.2 Intelligence Modules

**Scraper** (`modules/intelligence/scraper.py`)
- Busca conteúdo viral em plataformas (YouTube, TikTok, Instagram)
- Coleta: títulos, descrições, métricas, comentários
- Filtra por nicho, idioma, período
- Rate limiting e cache para não sobrecarregar APIs

**Analyzer** (`modules/intelligence/analyzer.py`)
- Analisa estrutura do conteúdo (intro, desenvolvimento, CTA)
- Identifica padrões de engajamento
- Classifica tipo de conteúdo (educativo, entretenimento, polêmico)
- Mede densidade de hooks por minuto

**DNA Extractor** (`modules/intelligence/dna_extractor.py`)
- Extrai o "DNA viral" — os elementos que fazem funcionar
- Categorias: hook type, narrative arc, emotional triggers, CTA style
- Gera um `ViralDNA` object reutilizável

```python
@dataclass
class ViralDNA:
    hook_type: str          # "question", "shock", "curiosity_gap", "bold_claim"
    narrative_arc: str      # "problem_solution", "story", "list", "debate"
    emotional_triggers: list # ["curiosity", "fear", "aspiration"]
    cta_style: str          # "soft", "urgent", "community"
    pacing: str             # "fast", "slow_build", "rollercoaster"
    content_density: float  # 0-1, quão denso de informação
    retention_hooks: list   # Momentos que prendem atenção
```

### 3.3 Creation Modules

**Idea Generator** (`modules/creation/idea_generator.py`)
- Recebe DNA + prompt
- Gera 3-5 ideias com título, ângulo e justificativa
- Rankeia por potencial viral estimado
- Usa Claude com prompt engineering especializado

**Creative Booster** (`modules/creation/creative_booster.py`)
- Pega a ideia escolhida e expande
- Adiciona ângulos inesperados, analogias, dados
- Garante originalidade (não é cópia da referência)
- Aplica técnicas criativas: inversão, exagero, conexão improvável

**Script Writer** (`modules/creation/script_writer.py`)
- Gera roteiro completo com timestamps
- Formata para a plataforma alvo (Reels, YouTube, TikTok)
- Inclui: narração, indicações visuais, texto na tela
- Respeita duração alvo

```python
@dataclass
class Script:
    title: str
    hook: str                   # Primeiros 3 segundos
    sections: list[Section]     # Corpo do conteúdo
    cta: str                    # Call to action
    platform: str               # "youtube_short", "reels", "tiktok"
    target_duration: int        # Segundos
    visual_notes: list[str]     # Indicações para edição
    text_overlays: list[str]    # Textos na tela
```

### 3.4 Optimization Modules

**Validator** (`modules/optimization/validator.py`)
- Checa: hook forte? Estrutura coerente? CTA presente?
- Score de 0-100 com breakdown por categoria
- Se score < 70, devolve pro Script Writer com feedback

**Optimizer** (`modules/optimization/optimizer.py`)
- Otimiza para a plataforma específica
- Gera: título, descrição, hashtags, horário sugerido
- Adapta linguagem pro público alvo

---

## 4. SISTEMA DE MEMÓRIA

### 4.1 Estrutura (`data/memory.json`)

```json
{
  "niches": {
    "finance": {
      "viral_dnas": [...],
      "best_hooks": [...],
      "avg_performance": {}
    }
  },
  "history": [
    {
      "id": "uuid",
      "timestamp": "2026-04-06T...",
      "prompt": "...",
      "pipeline": "full",
      "output": {},
      "quality_score": 85,
      "platform": "reels"
    }
  ],
  "styles": {
    "preferred_tone": "casual",
    "avoided_words": [],
    "brand_voice": {}
  }
}
```

### 4.2 Evolução planejada
- **v1:** JSON local (agora)
- **v2:** SQLite com busca por similaridade
- **v3:** PostgreSQL + embeddings para busca semântica

---

## 5. INTEGRAÇÃO TELEGRAM

### 5.1 Comandos

| Comando | Ação |
|---------|------|
| `/criar [prompt]` | Pipeline completo |
| `/rapido [prompt]` | Pipeline rápido (sem pesquisa) |
| `/pesquisar [nicho]` | Só pesquisa e análise |
| `/otimizar` | Otimiza último roteiro |
| `/historico` | Lista últimas criações |
| `/config` | Configura preferências |
| `/status` | Status do sistema |

### 5.2 Fluxo de conversa
```
Usuário: /criar vídeo sobre investir com pouco dinheiro
Bot: 🔍 Pesquisando referências virais sobre investimento...
Bot: 📊 Encontrei 12 referências. Analisando padrões...
Bot: 💡 Gerei 3 ideias. Qual você prefere?
     1. "O erro de R$50 que te custa R$50.000"
     2. "Comecei com R$10 e isso aconteceu"
     3. "3 investimentos que bancos não querem que você conheça"
Usuário: 1
Bot: ✍️ Escrevendo roteiro...
Bot: ✅ Roteiro pronto! Score: 87/100
     [Roteiro completo aqui]
     /otimizar para ajustar | /refazer para nova versão
```

---

## 6. TECH STACK

| Componente | Tecnologia | Motivo |
|-----------|------------|--------|
| Backend | Python 3.11+ | Ecossistema de IA |
| IA | Claude API (Sonnet) | Qualidade + custo |
| Bot | python-telegram-bot | Maduro e estável |
| Memória v1 | JSON | Simplicidade inicial |
| Config | Pydantic | Validação de dados |
| HTTP | httpx | Async nativo |
| Testes | pytest | Standard |
| Deploy | VPS (Ubuntu) | Controle total |

---

## 7. ESTRUTURA DO PROJETO

```
cis/
├── core/
│   ├── __init__.py
│   ├── orchestrator.py      # Orquestrador central
│   ├── pipeline.py          # Definição dos pipelines
│   └── models.py            # Dataclasses compartilhados
│
├── modules/
│   ├── intelligence/
│   │   ├── __init__.py
│   │   ├── scraper.py       # Coleta de referências
│   │   ├── analyzer.py      # Análise de conteúdo
│   │   └── dna_extractor.py # Extração de DNA viral
│   │
│   ├── creation/
│   │   ├── __init__.py
│   │   ├── idea_generator.py
│   │   ├── creative_booster.py
│   │   └── script_writer.py
│   │
│   └── optimization/
│       ├── __init__.py
│       ├── validator.py
│       └── optimizer.py
│
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py      # Handler principal
│   ├── handlers.py          # Comandos
│   └── formatters.py        # Formatação de mensagens
│
├── data/
│   └── memory.json
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configurações centrais
│   └── prompts.py           # Todos os prompts do Claude
│
├── utils/
│   ├── __init__.py
│   ├── claude_client.py     # Wrapper da API Claude
│   └── logger.py            # Logging centralizado
│
├── tests/
│   └── ...
│
├── main.py                  # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 8. REGRAS DO SISTEMA

1. **Nunca copiar** — Todo conteúdo é recombinação original
2. **Sem pular etapas** — Pipeline é sequencial e validado
3. **Qualidade mínima** — Score < 70 = reprocessar
4. **Memória ativa** — Cada geração alimenta o sistema
5. **Transparência** — Usuário sabe o que está acontecendo em cada etapa
6. **Fail gracefully** — Se um módulo falha, o sistema avisa e sugere alternativa

---

## 9. ROADMAP

### Fase 1 — MVP (Agora)
- [ ] Orchestrator funcional
- [ ] Claude client wrapper
- [ ] Idea Generator + Script Writer
- [ ] Validator básico
- [ ] Telegram bot com /criar e /rapido
- [ ] Memória JSON

### Fase 2 — Inteligência
- [ ] Scraper real (YouTube API, web scraping)
- [ ] Analyzer com Claude
- [ ] DNA Extractor
- [ ] Pipeline completo funcionando

### Fase 3 — Produção
- [ ] Geração de assets (thumbnails, texto na tela)
- [ ] Integração com ferramentas de edição
- [ ] Multi-plataforma (YouTube, TikTok, Reels)

### Fase 4 — Escala
- [ ] SQLite/PostgreSQL
- [ ] Multi-conta
- [ ] Dashboard web
- [ ] Sistema de performance learning
- [ ] SaaS
