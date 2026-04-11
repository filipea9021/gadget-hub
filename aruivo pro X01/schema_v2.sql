-- CIS — Schema v2 (Fase 2: Inteligência Real)
-- Executa após schema.sql (estende as tabelas existentes)

-- Conteúdo viral coletado pelo scraper
CREATE TABLE IF NOT EXISTS scraped_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    external_id TEXT,
    niche TEXT,
    title TEXT,
    description TEXT,
    tags TEXT,              -- JSON array
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    published_at TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed INTEGER DEFAULT 0,   -- 0=pendente, 1=já analisado pelo DNA extractor
    raw_json TEXT,
    UNIQUE(platform, external_id)
);

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_scraped_niche ON scraped_content(niche, platform);
CREATE INDEX IF NOT EXISTS idx_scraped_views ON scraped_content(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_scraped_analyzed ON scraped_content(analyzed);

-- Extensão do viral_dna com métricas de confiança
CREATE TABLE IF NOT EXISTS viral_dna_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    niche TEXT NOT NULL,
    platform TEXT NOT NULL,
    pattern_json TEXT NOT NULL,
    source TEXT DEFAULT '',
    confidence_score REAL DEFAULT 0.5,   -- 0.0 a 1.0 (evolui com feedback)
    sample_count INTEGER DEFAULT 1,       -- quantas amostras embasaram esse DNA
    wins INTEGER DEFAULT 0,              -- vezes que conteúdo com esse DNA performou bem
    losses INTEGER DEFAULT 0,            -- vezes que performou mal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dna_niche ON viral_dna_v2(niche, platform);
CREATE INDEX IF NOT EXISTS idx_dna_confidence ON viral_dna_v2(confidence_score DESC);

-- Performance real de conteúdo gerado pelo CIS (fechamento do loop)
CREATE TABLE IF NOT EXISTS performance_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_history_id INTEGER,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    completion_rate REAL,         -- % de viewers que assistiram até o fim (0.0-1.0)
    platform TEXT,
    notes TEXT,
    performance_tier TEXT         -- 'viral'|'good'|'average'|'poor' (calculado automaticamente)
);

-- Cache de quota da API (evita reprocessar dados frescos)
CREATE TABLE IF NOT EXISTS api_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,   -- ex: "youtube:investimento:BR:20260406"
    response_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at);
