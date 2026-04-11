# 🧠 CIS — Content Intelligence System

Sistema de inteligência de conteúdo viral com IA. Pesquisa, analisa, cria, produz e otimiza conteúdo baseado em dados reais.

## Arquitetura

```
cis/
├── core/
│   ├── config.py              # Configuração + slots de integração
│   └── orchestrator.py        # Cérebro: classifica → roteia → executa
├── api/
│   └── claude_client.py       # Wrapper API Claude (sync + structured)
├── modules/
│   ├── intelligence/
│   │   ├── analyzer.py        # Analisa padrões de conteúdo viral
│   │   └── dna_extractor.py   # Extrai fórmula replicável ("DNA viral")
│   ├── creation/
│   │   ├── ideator.py         # Gera ideias baseadas em padrões comprovados
│   │   ├── scriptwriter.py    # Escreve roteiro completo
│   │   └── refiner.py         # Refina qualidade e impacto
│   └── optimization/
│       ├── validator.py       # Valida antes de entregar
│       └── seo_optimizer.py   # Título, descrição, hashtags, tags
├── integrations/
│   ├── higgsfield.py          # Higgsfield AI (imagem + vídeo)
│   ├── video_producer.py      # Remotion + Video Toolkit + Higgsfield
│   └── manager.py             # Roteador central de todas as integrações
├── skills/
│   ├── manager.py             # Carrega e indexa skills
│   ├── video/SKILL.md         # Remotion + Video Toolkit + AI Video Gen
│   ├── content/SKILL.md       # Repurposing + Research Writer + Twitter Opt
│   ├── image/SKILL.md         # Gemini + Higgsfield + Canvas Design
│   ├── seo/SKILL.md           # claude-seo + devmarketing + content-creator
│   └── library/SKILL.md       # Antigravity (1340+) + claude-skills (220+)
├── memory/
│   ├── schema.sql             # SQLite: histórico + DNA viral + estilos
│   └── store.py               # Interface de memória persistente
├── bot/
│   └── telegram_bot.py        # Interface Telegram
├── setup.sh                   # Script de instalação
├── requirements.txt
└── main.py
```

## Modos de Operação

| Modo | Trigger | Pipeline |
|------|---------|----------|
| **RESEARCH** | "pesquisar", "analisar" | analyzer → dna_extractor |
| **CREATE** | "criar", "fazer", "gerar" | ideator → scriptwriter → refiner |
| **OPTIMIZE** | "otimizar", "melhorar" | validator → seo_optimizer |
| **FULL** | "completo", "tudo" | research → create → optimize |
| **PRODUCE** | "produzir", "vídeo", "imagem" | integration_manager (todas as ferramentas) |

## Skills da Comunidade Integradas

| Skill | Fonte | Capacidade |
|-------|-------|------------|
| **Remotion** | remotion-dev/skills | Vídeo programático React |
| **Video Toolkit** | digitalsamba/claude-code-video-toolkit | Voiceover, música, SFX |
| **AI Video Generator** | mcpmarket.com | Sora 2 / Veo 3.1 |
| **Content Repurposing** | MindStudio | YouTube → multiplataforma |
| **Content Research Writer** | ComposioHQ | Escrita com pesquisa |
| **Twitter Optimizer** | ComposioHQ | Algoritmo open-source X |
| **claude-image-gen** | guinacio | Imagens via Gemini |
| **Canvas Design** | ComposioHQ | Posters, infográficos |
| **claude-seo** | AgriciDaniel | SEO técnico completo |
| **devmarketing** | jonathimer | 33 skills de marketing |
| **Antigravity** | sickn33 | 1.340+ skills diversas |
| **claude-skills** | alirezarezvani | 220+ skills + 332 scripts |

## Setup

```bash
chmod +x setup.sh && ./setup.sh
```

## Uso

```bash
# Telegram bot
python main.py

# Ou direto no código
python -c "
import asyncio
from core.orchestrator import orchestrator
result = asyncio.run(orchestrator.execute('Crie um vídeo viral sobre IA para TikTok'))
print(result)
"
```

## Variáveis de Ambiente

```
ANTHROPIC_API_KEY=     # Obrigatório
TELEGRAM_BOT_TOKEN=    # Para o bot
HF_API_KEY=            # Higgsfield
HF_API_SECRET=         # Higgsfield
GEMINI_API_KEY=        # Google Gemini (opcional)
```
