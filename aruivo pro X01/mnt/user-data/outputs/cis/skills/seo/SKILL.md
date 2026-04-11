---
name: cis-seo-marketing
description: SEO técnico e marketing digital para o CIS. Integra claude-seo (SEO técnico completo), devmarketing-skills (33 skills de marketing), e alirezarezvani/claude-skills content-creator. Trigger quando o pipeline precisar otimizar para buscas, criar estratégia de distribuição, planejar growth, otimizar descrições, tags, hashtags, ou qualquer tarefa de SEO e marketing digital. Também trigger para "SEO", "ranking", "keywords", "distribuição", "growth", "marketing", "hashtags", "tags", "descrição", "algoritmo".
---

# CIS SEO & Marketing Skill

Skill de otimização para busca e distribuição de conteúdo.

## Ferramentas Integradas

### 1. claude-seo (AgriciDaniel/claude-seo)
- **O que faz**: Workflow completo de SEO técnico
- **Capacidades**:
  - Auditoria SEO técnica
  - Implementação hreflang
  - Geração de sitemap
  - Schema markup (JSON-LD)
  - SEO programático
  - Geo-targeting
  - Análise de concorrência
- **Quando usar**: Otimização de páginas, blogs, landing pages

### 2. devmarketing-skills (jonathimer/devmarketing-skills)
- **O que faz**: 33 skills de marketing para desenvolvedores e creators
- **Capacidades**:
  - Estratégia HackerNews
  - Criação de tutoriais técnicos
  - Docs-as-marketing
  - Engajamento Reddit
  - Onboarding de desenvolvedores
  - Growth hacking
  - Community building
- **Quando usar**: Distribuição de conteúdo em comunidades técnicas

### 3. content-creator (alirezarezvani/claude-skills)
- **O que faz**: Criação de conteúdo otimizado para SEO
- **Capacidades**:
  - Blog posts SEO-friendly
  - Keyword research integrado
  - Meta descriptions otimizadas
  - Internal linking strategy
  - Content clustering
- **Quando usar**: Conteúdo escrito que precisa rankear

## Pipeline de SEO por Plataforma

```
Conteúdo criado
    ↓
Otimização SEO:
├── YouTube:
│   ├── Título: keyword no início, <60 chars, power words
│   ├── Descrição: 200+ palavras, links, timestamps, keywords
│   ├── Tags: mix de broad + long-tail
│   └── Thumbnail text: 3-5 palavras de impacto
├── Blog/Site:
│   ├── H1, H2, H3 otimizados
│   ├── Meta description < 160 chars
│   ├── Schema markup
│   ├── Internal links
│   └── Alt text das imagens
├── Instagram:
│   ├── Hashtags: 20-30, mix de volume
│   ├── Caption com keyword natural
│   └── Alt text
├── TikTok:
│   ├── Hashtags: 3-5 trending + nicho
│   ├── Caption curta com keyword
│   └── Sounds trending
└── X/Twitter:
    ├── Keywords naturais no tweet
    ├── Hashtags: 1-2 max
    └── Timing otimizado por algoritmo
    ↓
Estratégia de distribuição:
├── Posting schedule otimizado
├── Cross-posting plan
├── Community seeding (Reddit, HN, Discord)
└── Engagement follow-up plan
```

## Uso no CIS

Chamado automaticamente pelo `modules/optimization/seo_optimizer.py`.
Também disponível standalone via orchestrator `mode=optimize`.
