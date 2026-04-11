"""
CIS — Store (v2)
Interface SQLite: histórico, DNA viral, scraping, feedback de performance.
"""

import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory", "cis_memory.db")


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    """Inicializa schema v1 e v2."""
    schema_dir = os.path.dirname(os.path.abspath(__file__))

    # Schema v1 (original)
    schema_v1 = os.path.join(schema_dir, "memory", "schema.sql")
    if not os.path.exists(schema_v1):
        schema_v1 = os.path.join(schema_dir, "schema.sql")

    # Schema v2 (Fase 2 — tabelas novas)
    schema_v2 = os.path.join(schema_dir, "schema_v2.sql")

    with _conn() as c:
        for schema_path in [schema_v1, schema_v2]:
            if os.path.exists(schema_path):
                with open(schema_path) as f:
                    c.executescript(f.read())


# ------------------------------------------------------------------
# Histórico de conteúdo gerado
# ------------------------------------------------------------------

def save_content(prompt, mode, niche, platform, output, score=None, notes=None) -> int:
    """Salva geração no histórico. Retorna o ID inserido."""
    with _conn() as c:
        cursor = c.execute(
            """INSERT INTO content_history
               (prompt, mode, niche, platform, output_json, quality_score, notes)
               VALUES (?,?,?,?,?,?,?)""",
            (prompt, mode, niche, platform,
             json.dumps(output, ensure_ascii=False), score, notes)
        )
        return cursor.lastrowid


def get_history(limit=10) -> list[dict]:
    """Retorna os últimos conteúdos gerados."""
    with _conn() as c:
        return [
            dict(r) for r in c.execute(
                "SELECT * FROM content_history ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        ]


def get_last_content_id() -> int | None:
    """Retorna o ID do último conteúdo gerado."""
    with _conn() as c:
        row = c.execute(
            "SELECT id FROM content_history ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        return row["id"] if row else None


# ------------------------------------------------------------------
# DNA Viral (v1 — mantido por compatibilidade)
# ------------------------------------------------------------------

def save_dna(niche, platform, pattern, source=""):
    with _conn() as c:
        c.execute(
            "INSERT INTO viral_dna (niche, platform, pattern_json, source) VALUES (?,?,?,?)",
            (niche, platform, json.dumps(pattern, ensure_ascii=False), source)
        )


# ------------------------------------------------------------------
# DNA Viral v2 — com confidence (Fase 2)
# ------------------------------------------------------------------

def get_best_dnas_v2(niche: str, platform: str = "", limit: int = 3) -> list[dict]:
    """Retorna DNAs mais confiáveis. Chama dna_evolver internamente."""
    from dna_evolver import get_best_dnas
    return get_best_dnas(niche=niche, platform=platform, limit=limit)


def has_real_dna(niche: str) -> bool:
    """Verifica se já existe DNA real (scraped) para um nicho."""
    with _conn() as c:
        row = c.execute(
            "SELECT COUNT(*) as cnt FROM viral_dna_v2 WHERE niche = ?",
            (niche,)
        ).fetchone()
        return (row["cnt"] if row else 0) > 0


# ------------------------------------------------------------------
# Scraping stats
# ------------------------------------------------------------------

def get_scraping_stats() -> dict:
    """Retorna estatísticas do banco de dados."""
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) as n FROM scraped_content").fetchone()["n"]
        analyzed = c.execute(
            "SELECT COUNT(*) as n FROM scraped_content WHERE analyzed = 1"
        ).fetchone()["n"]
        niches = c.execute(
            "SELECT niche, COUNT(*) as cnt FROM scraped_content GROUP BY niche ORDER BY cnt DESC"
        ).fetchall()
        dna_count = c.execute("SELECT COUNT(*) as n FROM viral_dna_v2").fetchone()["n"]
        feedback_count = c.execute("SELECT COUNT(*) as n FROM performance_feedback").fetchone()["n"]

    return {
        "scraped_total": total,
        "scraped_analyzed": analyzed,
        "scraped_pending": total - analyzed,
        "dna_patterns": dna_count,
        "performance_feedbacks": feedback_count,
        "niches": {r["niche"]: r["cnt"] for r in niches},
    }
