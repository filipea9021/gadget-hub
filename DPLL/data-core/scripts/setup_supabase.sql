-- ============================================================
-- DATA CORE AGENT — Setup completo do Supabase
-- Executar no SQL Editor do Supabase (supabase.com → projeto → SQL Editor)
-- ============================================================

-- 1. TABELA: memory_logs
CREATE TABLE IF NOT EXISTS memory_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    type TEXT NOT NULL CHECK (type IN (
        'action_log', 'decision_log', 'learning',
        'error_log', 'config_snapshot'
    )),
    category TEXT,
    severity TEXT DEFAULT 'info' CHECK (severity IN (
        'debug', 'info', 'warning', 'error', 'critical'
    )),

    title TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',

    origin_skill TEXT NOT NULL,
    related_ids UUID[],
    session_id TEXT,

    tags TEXT[] DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_logs(type);
CREATE INDEX IF NOT EXISTS idx_memory_origin ON memory_logs(origin_skill);
CREATE INDEX IF NOT EXISTS idx_memory_created ON memory_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_tags ON memory_logs USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memory_metadata ON memory_logs USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_logs(category);


-- 2. TABELA: media_files
CREATE TABLE IF NOT EXISTS media_files (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    original_name TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    public_url TEXT,

    file_type TEXT NOT NULL CHECK (file_type IN (
        'image', 'video', 'document', 'other'
    )),
    mime_type TEXT,
    file_extension TEXT,
    file_size_bytes BIGINT,
    file_hash TEXT,

    width INTEGER,
    height INTEGER,
    duration_seconds FLOAT,

    bucket TEXT NOT NULL,
    folder TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    category TEXT,

    origin_skill TEXT NOT NULL,
    purpose TEXT,
    campaign_id TEXT,
    description TEXT,

    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'archived', 'temp', 'deleted', 'uploading'
    )),
    used_in JSONB DEFAULT '[]',
    usage_count INTEGER DEFAULT 0,

    performance_data JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_media_type ON media_files(file_type);
CREATE INDEX IF NOT EXISTS idx_media_origin ON media_files(origin_skill);
CREATE INDEX IF NOT EXISTS idx_media_status ON media_files(status);
CREATE INDEX IF NOT EXISTS idx_media_folder ON media_files(bucket, folder);
CREATE INDEX IF NOT EXISTS idx_media_tags ON media_files USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_media_hash ON media_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_media_created ON media_files(created_at DESC);

-- Indice unico parcial para prevenir duplicatas (exclui deletados)
CREATE UNIQUE INDEX IF NOT EXISTS idx_media_unique_hash
    ON media_files(file_hash)
    WHERE status NOT IN ('deleted');


-- 3. TABELA: system_data
CREATE TABLE IF NOT EXISTS system_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    data_type TEXT NOT NULL DEFAULT 'general',
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,

    value JSONB NOT NULL,
    description TEXT,

    version INTEGER DEFAULT 1,

    UNIQUE(namespace, key)
);

CREATE INDEX IF NOT EXISTS idx_data_namespace ON system_data(namespace);
CREATE INDEX IF NOT EXISTS idx_data_type ON system_data(data_type);
CREATE INDEX IF NOT EXISTS idx_data_updated ON system_data(updated_at DESC);


-- ============================================================
-- VERIFICACAO — Confirmar que tudo foi criado
-- ============================================================
SELECT 'memory_logs' AS tabela, COUNT(*) AS registros FROM memory_logs
UNION ALL
SELECT 'media_files', COUNT(*) FROM media_files
UNION ALL
SELECT 'system_data', COUNT(*) FROM system_data;
