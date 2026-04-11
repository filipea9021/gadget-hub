CREATE TABLE IF NOT EXISTS content_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT, mode TEXT, niche TEXT, platform TEXT, output_json TEXT, quality_score REAL, notes TEXT
);
CREATE TABLE IF NOT EXISTS viral_dna (
    id INTEGER PRIMARY KEY AUTOINCREMENT, niche TEXT, platform TEXT, pattern_json TEXT, source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS style_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, tone TEXT, vocabulary_notes TEXT, structure_notes TEXT, examples TEXT
);