"""
CIS — Scraper Cache (Fase 2)
Cache de 24h no SQLite para não desperdiçar quota das APIs.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

from memory.store import DB_PATH


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expires(hours: int = 24) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


# ------------------------------------------------------------------
# Cache de chamadas à API
# ------------------------------------------------------------------

def cache_get(key: str) -> Optional[dict]:
    """Retorna dados do cache se ainda válidos. None se expirado/inexistente."""
    with _conn() as c:
        row = c.execute(
            "SELECT response_json, expires_at FROM api_cache WHERE cache_key = ?",
            (key,)
        ).fetchone()

    if not row:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return None  # Expirado

    return json.loads(row["response_json"])


def cache_set(key: str, data: dict, hours: int = 24) -> None:
    """Salva dados no cache com TTL."""
    with _conn() as c:
        c.execute(
            """INSERT INTO api_cache (cache_key, response_json, expires_at)
               VALUES (?, ?, ?)
               ON CONFLICT(cache_key) DO UPDATE SET
                 response_json = excluded.response_json,
                 expires_at = excluded.expires_at,
                 created_at = CURRENT_TIMESTAMP""",
            (key, json.dumps(data, ensure_ascii=False), _expires(hours))
        )


def cache_key_for_scrape(platform: str, niche: str, language: str) -> str:
    """Gera chave de cache para uma busca específica."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{platform}:{niche.lower()}:{language}:{today}"


# ------------------------------------------------------------------
# Armazenamento de conteúdo raspado
# ------------------------------------------------------------------

def save_scraped(items: list[dict]) -> int:
    """Salva lista de ScrapedContent no banco. Retorna quantos foram inseridos."""
    if not items:
        return 0

    inserted = 0
    with _conn() as c:
        for item in items:
            try:
                c.execute(
                    """INSERT OR IGNORE INTO scraped_content
                       (platform, external_id, niche, title, description, tags,
                        view_count, like_count, comment_count, share_count,
                        duration_seconds, published_at, raw_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        item.get("platform", ""),
                        item.get("external_id", ""),
                        item.get("niche", ""),
                        item.get("title", ""),
                        item.get("description", ""),
                        item.get("tags", "[]"),
                        item.get("view_count", 0),
                        item.get("like_count", 0),
                        item.get("comment_count", 0),
                        item.get("share_count", 0),
                        item.get("duration_seconds", 0),
                        item.get("published_at", ""),
                        item.get("raw_json", "{}"),
                    )
                )
                if c.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"[scraper_cache] save error: {e}")

    return inserted


def get_unanalyzed(niche: str = "", limit: int = 50) -> list[dict]:
    """Busca conteúdos ainda não processados pelo DNA Extractor."""
    with _conn() as c:
        if niche:
            rows = c.execute(
                """SELECT * FROM scraped_content
                   WHERE analyzed = 0 AND niche = ?
                   ORDER BY view_count DESC LIMIT ?""",
                (niche, limit)
            ).fetchall()
        else:
            rows = c.execute(
                """SELECT * FROM scraped_content
                   WHERE analyzed = 0
                   ORDER BY view_count DESC LIMIT ?""",
                (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


def mark_analyzed(ids: list[int]) -> None:
    """Marca conteúdos como já analisados."""
    if not ids:
        return
    placeholders = ",".join("?" * len(ids))
    with _conn() as c:
        c.execute(
            f"UPDATE scraped_content SET analyzed = 1 WHERE id IN ({placeholders})",
            ids
        )


def get_top_scraped(niche: str, platform: str = "", limit: int = 10) -> list[dict]:
    """Retorna os conteúdos com mais views de um nicho (para inspirar o Ideator)."""
    with _conn() as c:
        if platform:
            rows = c.execute(
                """SELECT title, description, tags, view_count, like_count
                   FROM scraped_content
                   WHERE niche = ? AND platform = ?
                   ORDER BY view_count DESC LIMIT ?""",
                (niche, platform, limit)
            ).fetchall()
        else:
            rows = c.execute(
                """SELECT title, description, tags, view_count, like_count
                   FROM scraped_content
                   WHERE niche = ?
                   ORDER BY view_count DESC LIMIT ?""",
                (niche, limit)
            ).fetchall()
    return [dict(r) for r in rows]


def cleanup_expired_cache() -> None:
    """Remove entradas expiradas do cache."""
    with _conn() as c:
        c.execute(
            "DELETE FROM api_cache WHERE expires_at < ?",
            (_now(),)
        )
