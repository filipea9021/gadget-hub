# CIS — Fase 2: Inteligência Real + Aprendizado Autônomo

> Planeado em: 2026-04-06
> Pesquisa baseada em: YouTube Data API v3, TikTokApi unofficial, padrões virais 2025

---

## O que muda na Fase 2

Na Fase 1, o `analyzer.py` e o `dna_extractor.py` trabalham com o conhecimento interno do Claude — ele sabe o que tende a funcionar, mas não vê dados reais. Na Fase 2, o CIS passa a **consumir o mundo real**:

- Busca conteúdo viral de verdade (YouTube, TikTok)
- Extrai padrões desses dados reais
- Salva os padrões no banco de DNA
- Usa o histórico próprio para evoluir (o que gerou, como foi, o que melhorou)

O sistema deixa de depender só do Claude e começa a **aprender com a realidade**.

---

## 1. Scraper Real

### 1.1 YouTube (fonte primária — gratuita e confiável)

**API:** YouTube Data API v3 (Google)
**Custo:** Gratuito — 10.000 unidades/dia
**Custo por operação:** search = 100 unidades | read = 1 unidade | logo: ~100 buscas/dia

**O que coletar:**
```
- title, description, tags
- viewCount, likeCount, commentCount
- duration, publishedAt
- channelId, channelTitle
- categoryId, defaultLanguage
```

**Endpoint principal:**
```python
# Vídeos mais vistos por nicho
youtube.videos().list(
    part="snippet,statistics,contentDetails",
    chart="mostPopular",
    regionCode="BR",          # ou US, PT, etc.
    videoCategoryId="27",     # 27=Education, 22=People, 24=Entertainment...
    maxResults=50
)

# Busca por nicho + ordenado por viewCount
youtube.search().list(
    part="snippet",
    q="{nicho} viral",
    order="viewCount",
    publishedAfter="30 dias atrás",
    type="video",
    videoDuration="short",    # para Shorts
    maxResults=25
)
```

**Arquivo:** `modules/intelligence/scrapers/youtube_scraper.py`
**Env var a adicionar:** `YOUTUBE_API_KEY`

### 1.2 TikTok (fonte secundária — dados ricos, instável)

**Biblioteca:** `TikTokApi` (unofficial, PyPI: `TikTokApi`)
**Instalação:** `pip install TikTokApi`
**Risco:** Anti-bot do TikTok pode bloquear. Usar com cautela + delays.

**O que coletar:**
```
- title/description, hashtags usadas
- diggCount (likes), playCount, shareCount, commentCount
- duração, authorStats
- createTime
```

**Arquivo:** `modules/intelligence/scrapers/tiktok_scraper.py`

### 1.3 Estratégia de quota e fallback

```
Tentativa 1: YouTube API (grátis, confiável)
Tentativa 2: TikTokApi (instável, mas rico)
Fallback: Claude analisa com base no nicho (comportamento atual da Fase 1)
```

**Cache obrigatório:** Resultados são guardados no SQLite por 24h para não desperdiçar quota.

---

## 2. Novo Schema SQLite (extensão do schema.sql atual)

```sql
-- Conteúdo viral coletado pelo scraper
CREATE TABLE IF NOT EXISTS scraped_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,          -- 'youtube', 'tiktok', 'instagram'
    external_id TEXT UNIQUE,         -- id do vídeo na plataforma
    niche TEXT,
    title TEXT,
    description TEXT,
    tags TEXT,                       -- JSON array
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    duration_seconds INTEGER,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT                    -- dados completos para re-análise
);

-- DNA viral por nicho/plataforma com score de confiança
ALTER TABLE viral_dna ADD COLUMN confidence_score REAL DEFAULT 0.5;
ALTER TABLE viral_dna ADD COLUMN sample_count INTEGER DEFAULT 1;
ALTER TABLE viral_dna ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Performance real de conteúdo gerado pelo CIS
CREATE TABLE IF NOT EXISTS performance_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_history_id INTEGER REFERENCES content_history(id),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    completion_rate REAL,            -- % de pessoas que assistiram até o fim
    platform TEXT,
    notes TEXT
);
```

---

## 3. Loop de Aprendizado Autônomo

Este é o coração da Fase 2. O CIS não apenas gera — ele **aprende com o que funciona**.

### 3.1 Ciclo completo

```
[Scraper]
    ↓ coleta conteúdo viral real
[Analyzer + DNA Extractor]
    ↓ extrai padrões com dados reais
[DNA Store (SQLite)]
    ↓ acumula padrões por nicho/plataforma
[Ideator + ScriptWriter]
    ↓ usa DNA real ao invés de só intuição do Claude
[Conteúdo gerado]
    ↓ usuário publica e reporta resultado via Telegram
[Performance Feedback]
    ↓ alimenta a tabela performance_feedback
[DNA Evoluidor]
    ↓ DNAs que geraram conteúdo de alta performance ganham peso maior
[Loop reinicia com DNA mais refinado]
```

### 3.2 DNA Evoluidor (`modules/intelligence/dna_evolver.py`)

```python
# Lógica de evolução:
# 1. Busca todos os conteúdos gerados que têm feedback de performance
# 2. Para os que performaram bem (views altos, completion_rate > 60%):
#    - Identifica qual DNA foi usado
#    - Aumenta confidence_score desse DNA
#    - Extrai novos padrões do conteúdo que funcionou
# 3. Para os que performaram mal:
#    - Diminui confidence_score do DNA
# 4. Salva novos DNAs com os padrões extraídos dos top performers
```

### 3.3 Scraping agendado (autônomo)

Usando o scheduler do Cowork (`schedule skill`), o CIS pode rodar sozinho:

```
A cada 24h: youtube_scraper coleta top 50 por nicho ativo
A cada 7 dias: dna_evolver roda e refina os padrões
A cada geração: DNA mais relevante é priorizado no Ideator
```

### 3.4 Feedback via Telegram (novo comando)

```
/resultado [views] [likes] [compartilhamentos]
```

Bot associa automaticamente ao último conteúdo gerado e alimenta `performance_feedback`.

---

## 4. Melhorias no Ideator e ScriptWriter

### Ideator melhorado
Quando tem DNA real disponível no banco, usa **os padrões reais** ao invés de pedir pro Claude imaginar:

```python
# Antes (Fase 1):
DNA viral disponível: {research.get('viral_dna', 'nenhum')}

# Depois (Fase 2):
# Busca DNAs do nicho com confidence_score > 0.7
real_dnas = store.get_top_dnas(niche=ctx.niche, platform=ctx.platform, limit=5)
DNA comprovado por dados reais: {real_dnas}
```

### ScriptWriter melhorado
Usa dados concretos da pesquisa (títulos virais reais, hooks reais) como exemplos no prompt, aumentando muito a qualidade.

---

## 5. Dados que o CIS aprende sobre o mundo

Com a Fase 2 rodando, o banco de dados vai acumular:

| O que aprende | Como aprende |
|---------------|-------------|
| Quais hooks funcionam por nicho | Analisando títulos de vídeos com +1M views |
| Melhor duração por plataforma | Estatísticas reais de scraping |
| Padrões de CTA eficazes | Análise de descrições de top performers |
| Horário de publicação ideal | `publishedAt` dos conteúdos virais |
| Vocabulário do nicho | Tags e descrições mais frequentes |
| O que o CIS próprio gera melhor | Feedback de performance do usuário |

---

## 6. Fatos importantes aprendidos na pesquisa

> Fonte: dados reais de 2025 que agora alimentarão o DNA base do sistema

- **Atenção média:** 8.25 segundos — caiu de 12s em 2024. O hook é tudo.
- **71% dos viewers decidem em 3 segundos** se vão continuar assistindo.
- **Hooks fortes = 73% mais completion + 4.2x mais shares**
- **Shorts de 50-60 segundos** têm em média 4.1M views (melhor que <40s ou >90s)
- **Conteúdo autêntico performa 60% melhor** que conteúdo muito produzido
- **Emoções de alta excitação** (espanto, raiva, empolgação) = 80% mais compartilhável
- YouTube descontinuou o Trending em julho de 2025 → usar `chart=mostPopular` por categoria

---

## 7. Arquivos novos a criar

```
modules/
└── intelligence/
    ├── scrapers/
    │   ├── __init__.py
    │   ├── youtube_scraper.py       # YouTube Data API v3
    │   ├── tiktok_scraper.py        # TikTokApi unofficial
    │   └── scraper_cache.py         # Cache 24h no SQLite
    └── dna_evolver.py               # Evolui os DNAs com base em performance

memory/
└── schema_v2.sql                    # Extensão do schema atual
```

---

## 8. Ordem de implementação (prioridade)

1. `youtube_scraper.py` — base de tudo, gratuito e confiável
2. `schema_v2.sql` — extensão do banco com as novas tabelas
3. `dna_evolver.py` — núcleo do aprendizado autônomo
4. Comando `/resultado` no bot — fecha o loop de feedback
5. `tiktok_scraper.py` — depois que o YouTube estiver estável
6. Agendamento automático do scraper (daily)
7. Integração do DNA real no Ideator e ScriptWriter

---

## 9. Variáveis de ambiente a adicionar

```
YOUTUBE_API_KEY=     # Google Cloud Console → YouTube Data API v3
```

---

*O objetivo desta fase é que cada semana que passa, o CIS seja um pouco mais inteligente que na semana anterior — não porque o código mudou, mas porque ele aprendeu com dados reais.*
