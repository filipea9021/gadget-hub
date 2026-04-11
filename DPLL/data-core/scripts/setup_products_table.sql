-- ══════════════════════════════════════════════════════════
-- TABELA: products — Produtos do pipeline automático
-- Executa no Supabase SQL Editor (supabase.co → SQL Editor)
-- ══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Dados básicos do produto
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    margin DECIMAL(5,2),
    currency TEXT DEFAULT 'EUR',

    -- Fornecedor
    supplier TEXT DEFAULT '',
    supplier_url TEXT DEFAULT '',
    supplier_price DECIMAL(10,2),

    -- Imagens
    image_url TEXT DEFAULT '',
    image_storage_path TEXT DEFAULT '',
    gallery_urls JSONB DEFAULT '[]'::jsonb,

    -- Categorização
    category TEXT DEFAULT 'geral',
    tags JSONB DEFAULT '[]'::jsonb,
    niche TEXT DEFAULT '',

    -- Status do pipeline
    pipeline_status TEXT DEFAULT 'novo'
        CHECK (pipeline_status IN ('novo', 'imagem_processada', 'descricao_gerada', 'pronto', 'publicado', 'arquivado')),

    -- Scores e análise
    trend_score INTEGER DEFAULT 0 CHECK (trend_score >= 0 AND trend_score <= 100),
    competition_score INTEGER DEFAULT 0 CHECK (competition_score >= 0 AND competition_score <= 100),
    viability_score INTEGER DEFAULT 0 CHECK (viability_score >= 0 AND competition_score <= 100),

    -- Conteúdo gerado
    generated_title TEXT DEFAULT '',
    generated_description TEXT DEFAULT '',
    ad_copy JSONB DEFAULT '{}'::jsonb,
    seo_keywords JSONB DEFAULT '[]'::jsonb,

    -- Publicação
    published_at TIMESTAMPTZ,
    shopify_id TEXT DEFAULT '',
    store_url TEXT DEFAULT '',

    -- Metadados
    origin_skill TEXT DEFAULT 'manual',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_products_status ON products(pipeline_status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_niche ON products(niche);
CREATE INDEX IF NOT EXISTS idx_products_created ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_score ON products(trend_score DESC);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_products_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_products_updated ON products;
CREATE TRIGGER trigger_products_updated
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_timestamp();

-- Calcular margem automaticamente
CREATE OR REPLACE FUNCTION calculate_margin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price IS NOT NULL AND NEW.cost IS NOT NULL AND NEW.cost > 0 THEN
        NEW.margin = ROUND(((NEW.price - NEW.cost) / NEW.price * 100)::numeric, 2);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calc_margin ON products;
CREATE TRIGGER trigger_calc_margin
    BEFORE INSERT OR UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION calculate_margin();

-- Habilitar RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "products_full_access" ON products
    FOR ALL USING (true) WITH CHECK (true);

-- ══════════════════════════════════════════════════════════
-- VIEW: Dashboard rápido de produtos
-- ══════════════════════════════════════════════════════════

CREATE OR REPLACE VIEW products_dashboard AS
SELECT
    pipeline_status,
    COUNT(*) as total,
    ROUND(AVG(trend_score), 0) as avg_trend,
    ROUND(AVG(margin), 1) as avg_margin,
    ROUND(AVG(price), 2) as avg_price
FROM products
GROUP BY pipeline_status
ORDER BY
    CASE pipeline_status
        WHEN 'novo' THEN 1
        WHEN 'imagem_processada' THEN 2
        WHEN 'descricao_gerada' THEN 3
        WHEN 'pronto' THEN 4
        WHEN 'publicado' THEN 5
        WHEN 'arquivado' THEN 6
    END;
