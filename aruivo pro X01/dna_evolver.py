"""
CIS — DNA Evolver (Fase 2)
Núcleo do aprendizado autônomo.

Ciclo:
  1. Pega conteúdos virais reais do scraper (não analisados ainda)
  2. Extrai padrões com Claude (DNA real baseado em dados reais)
  3. Salva DNAs com confidence_score inicial
  4. Quando performance_feedback chega, ajusta confidence_score
  5. DNAs com alto confidence são priorizados no Ideator

Resultado: com o tempo, o CIS sabe o que funciona no mundo real,
não só o que o Claude imagina que funciona.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from api.claude_client import claude
from memory.store import DB_PATH
from scraper_cache import get_unanalyzed, mark_analyzed, get_top_scraped


# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

EXTRACT_DNA_SYSTEM = """Você é um extrator de padrões virais. Analise estes títulos e descrições
de conteúdo real com milhões de views e extraia o DNA viral deles.

Retorne JSON:
{
  "hook_formula": "fórmula do gancho mais frequente (ex: número + promessa + urgência)",
  "structure_template": "estrutura narrativa dominante",
  "emotional_triggers": ["emoções que dominam o conteúdo"],
  "retention_tactics": ["táticas identificadas para manter atenção"],
  "virality_score_factors": ["o que mais contribui para os altos números"],
  "vocabulary_patterns": ["palavras/frases recorrentes nos títulos"],
  "cta_patterns": ["padrões de call-to-action"],
  "replicable_pattern": "passo a passo replicável em bullet points",
  "avg_duration_sweet_spot": "duração ideal com base nos dados",
  "confidence_basis": "quantas amostras embasam este DNA e qual a qualidade delas"
}"""

EVOLVE_DNA_SYSTEM = """Você é um sistema de melhoria contínua. Dado um DNA viral existente
e o resultado de performance real de um conteúdo que usou este DNA, atualize e melhore o DNA.

Retorne JSON com o DNA atualizado (mesmo formato), melhorando com base no que funcionou ou não."""


# ------------------------------------------------------------------
# Acesso ao banco
# ------------------------------------------------------------------

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def save_dna_v2(
    niche: str,
    platform: str,
    pattern: dict,
    source: str = "scraper",
    confidence: float = 0.5,
    sample_count: int = 1,
) -> int:
    """Salva um DNA na tabela viral_dna_v2. Retorna o ID."""
    with _conn() as c:
        cursor = c.execute(
            """INSERT INTO viral_dna_v2
               (niche, platform, pattern_json, source, confidence_score, sample_count)
               VALUES (?,?,?,?,?,?)""",
            (niche, platform, json.dumps(pattern, ensure_ascii=False),
             source, confidence, sample_count)
        )
        return cursor.lastrowid


def get_best_dnas(niche: str, platform: str = "", limit: int = 3) -> list[dict]:
    """Retorna os DNAs mais confiáveis para um nicho/plataforma."""
    with _conn() as c:
        if platform:
            rows = c.execute(
                """SELECT pattern_json, confidence_score, sample_count, wins
                   FROM viral_dna_v2
                   WHERE niche = ? AND platform = ?
                   ORDER BY confidence_score DESC, wins DESC
                   LIMIT ?""",
                (niche, platform, limit)
            ).fetchall()
        else:
            rows = c.execute(
                """SELECT pattern_json, confidence_score, sample_count, wins
                   FROM viral_dna_v2
                   WHERE niche = ?
                   ORDER BY confidence_score DESC, wins DESC
                   LIMIT ?""",
                (niche, limit)
            ).fetchall()

    result = []
    for r in rows:
        try:
            dna = json.loads(r["pattern_json"])
            dna["_confidence"] = r["confidence_score"]
            dna["_samples"] = r["sample_count"]
            dna["_wins"] = r["wins"]
            result.append(dna)
        except Exception:
            pass
    return result


def save_performance_feedback(
    content_history_id: int,
    views: int,
    likes: int,
    comments: int,
    shares: int,
    platform: str,
    completion_rate: Optional[float] = None,
    notes: str = "",
) -> str:
    """Salva feedback de performance e calcula tier automaticamente."""
    # Define tier baseado em views + engagement
    engagement = likes + comments * 2 + shares * 3
    if views >= 1_000_000 or (views >= 100_000 and engagement > views * 0.05):
        tier = "viral"
    elif views >= 100_000 or (views >= 10_000 and engagement > views * 0.03):
        tier = "good"
    elif views >= 10_000:
        tier = "average"
    else:
        tier = "poor"

    with _conn() as c:
        c.execute(
            """INSERT INTO performance_feedback
               (content_history_id, views, likes, comments, shares,
                completion_rate, platform, notes, performance_tier)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (content_history_id, views, likes, comments, shares,
             completion_rate, platform, notes, tier)
        )

    return tier


def adjust_dna_confidence(niche: str, platform: str, tier: str) -> None:
    """Ajusta confidence_score dos DNAs do nicho/plataforma com base no resultado."""
    # Busca DNA mais recente que foi usado (heurística: mais recente do nicho)
    delta = {"viral": +0.15, "good": +0.08, "average": +0.00, "poor": -0.10}.get(tier, 0)
    if delta == 0:
        return

    with _conn() as c:
        if tier in ("viral", "good"):
            c.execute(
                """UPDATE viral_dna_v2
                   SET confidence_score = MIN(1.0, confidence_score + ?),
                       wins = wins + 1,
                       last_updated = CURRENT_TIMESTAMP
                   WHERE niche = ? AND (platform = ? OR platform = '')
                   ORDER BY last_updated DESC
                   LIMIT 1""",
                (delta, niche, platform)
            )
        else:
            c.execute(
                """UPDATE viral_dna_v2
                   SET confidence_score = MAX(0.1, confidence_score + ?),
                       losses = losses + 1,
                       last_updated = CURRENT_TIMESTAMP
                   WHERE niche = ? AND (platform = ? OR platform = '')
                   ORDER BY last_updated DESC
                   LIMIT 1""",
                (delta, niche, platform)
            )


# ------------------------------------------------------------------
# Ciclo principal de evolução
# ------------------------------------------------------------------

class DNAEvolver:
    """Processa conteúdo scraped → extrai DNA → salva com confiança inicial."""

    async def run_cycle(self, niche: str = "", batch_size: int = 30) -> dict:
        """
        Roda um ciclo completo de extração de DNA.
        Busca conteúdo não analisado, extrai padrões, salva.
        """
        items = get_unanalyzed(niche=niche, limit=batch_size)
        if not items:
            return {"status": "no_new_data", "dnas_created": 0}

        # Agrupa por nicho
        by_niche: dict[str, list] = {}
        for item in items:
            n = item.get("niche", "geral")
            by_niche.setdefault(n, []).append(item)

        total_dnas = 0
        for current_niche, niche_items in by_niche.items():
            # Prepara resumo dos conteúdos virais para o Claude analisar
            sample_text = self._format_samples(niche_items[:20])

            try:
                dna = await claude.call_structured(
                    prompt=f"""Analise estes {len(niche_items)} conteúdos virais reais do nicho "{current_niche}":

{sample_text}

Média de views: {sum(i['view_count'] for i in niche_items) // len(niche_items):,}
Top views: {max(i['view_count'] for i in niche_items):,}""",
                    system=EXTRACT_DNA_SYSTEM,
                    temperature=0.3,
                )

                # Confidence inicial: proporcional ao número de amostras
                initial_confidence = min(0.9, 0.4 + (len(niche_items) / 50) * 0.5)

                # Detecta plataforma dominante
                platforms = [i.get("platform", "") for i in niche_items]
                dominant_platform = max(set(platforms), key=platforms.count)

                save_dna_v2(
                    niche=current_niche,
                    platform=dominant_platform,
                    pattern=dna,
                    source="youtube_scraper",
                    confidence=initial_confidence,
                    sample_count=len(niche_items),
                )
                total_dnas += 1

            except Exception as e:
                print(f"[DNAEvolver] extraction error for {current_niche}: {e}")

        # Marca todos como analisados
        ids = [item["id"] for item in items]
        mark_analyzed(ids)

        return {
            "status": "ok",
            "items_processed": len(items),
            "dnas_created": total_dnas,
            "niches": list(by_niche.keys()),
        }

    async def evolve_from_feedback(
        self,
        content_history_id: int,
        views: int,
        likes: int,
        comments: int,
        shares: int,
        platform: str,
        niche: str,
        completion_rate: Optional[float] = None,
        notes: str = "",
    ) -> dict:
        """
        Recebe feedback de performance real e ajusta os DNAs.
        Chamado quando o usuário reporta /resultado.
        """
        tier = save_performance_feedback(
            content_history_id, views, likes, comments,
            shares, platform, completion_rate, notes
        )

        # Ajusta confiança dos DNAs do nicho
        adjust_dna_confidence(niche, platform, tier)

        # Se viral → tenta extrair DNA refinado do conteúdo que funcionou
        if tier in ("viral", "good"):
            top_content = get_top_scraped(niche=niche, platform=platform, limit=5)
            if top_content:
                await self._refine_dna_from_winners(niche, platform, top_content)

        return {
            "tier": tier,
            "adjustment": {"viral": "+15%", "good": "+8%", "average": "0%", "poor": "-10%"}.get(tier),
            "message": self._tier_message(tier),
        }

    async def _refine_dna_from_winners(
        self, niche: str, platform: str, winners: list[dict]
    ) -> None:
        """Extrai DNA refinado dos top performers para criar um DNA de alta confiança."""
        sample_text = self._format_samples(winners)
        try:
            refined_dna = await claude.call_structured(
                prompt=f"""Estes são os conteúdos com MELHOR performance real do nicho "{niche}":

{sample_text}

Extraia o DNA ultra-refinado destes top performers.""",
                system=EXTRACT_DNA_SYSTEM,
                temperature=0.2,
            )
            save_dna_v2(
                niche=niche,
                platform=platform,
                pattern=refined_dna,
                source="performance_winners",
                confidence=0.85,  # Alta confiança por vir de winners reais
                sample_count=len(winners),
            )
        except Exception as e:
            print(f"[DNAEvolver] refine error: {e}")

    @staticmethod
    def _format_samples(items: list[dict]) -> str:
        lines = []
        for i, item in enumerate(items[:15], 1):
            lines.append(
                f"{i}. [{item.get('view_count', 0):,} views] {item.get('title', '')}\n"
                f"   Tags: {item.get('tags', '[]')[:100]}"
            )
        return "\n".join(lines)

    @staticmethod
    def _tier_message(tier: str) -> str:
        return {
            "viral": "🚀 Viral! DNA deste nicho fortalecido. O sistema aprendeu com este sucesso.",
            "good": "✅ Bom resultado! Padrões reforçados para próximas gerações.",
            "average": "📊 Resultado médio registrado. Padrão mantido.",
            "poor": "📉 Resultado fraco registrado. DNA ajustado para evitar este padrão.",
        }.get(tier, "Resultado registrado.")


dna_evolver = DNAEvolver()
