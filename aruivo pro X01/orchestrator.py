"""
CIS — Orchestrator (v2)
Cérebro do sistema. Interpreta o pedido, decide o pipeline, coordena módulos.
Fase 2: usa scraper real + DNA evoluído quando disponíveis.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from api.claude_client import claude


class PipelineMode(Enum):
    RESEARCH = "research"
    CREATE = "create"
    OPTIMIZE = "optimize"
    FULL = "full"
    PRODUCE = "produce"
    LEARN = "learn"   # Fase 2: roda ciclo de aprendizado explicitamente


@dataclass
class TaskContext:
    original_prompt: str = ""
    mode: PipelineMode = PipelineMode.CREATE
    niche: str = ""
    platform: str = ""
    content_type: str = ""
    tone: str = ""
    references: list = field(default_factory=list)
    language: str = "pt-BR"
    extra: dict = field(default_factory=dict)


CLASSIFY_SYSTEM = """Você é o classificador do CIS (Content Intelligence System).
Dado o prompt do usuário, extraia um JSON com:
{
  "mode": "research" | "create" | "optimize" | "full" | "produce" | "learn",
  "niche": "nicho identificado ou vazio",
  "platform": "youtube" | "tiktok" | "instagram" | "x" | "",
  "content_type": "short" | "long" | "carousel" | "thread" | "",
  "tone": "tom identificado ou vazio",
  "references": ["urls ou termos mencionados"],
  "language": "pt-BR ou idioma detectado"
}
Regras:
- Pesquisar/analisar → research
- Criar do zero → create
- Melhorar algo pronto → optimize
- Ciclo completo → full
- Gerar imagem/vídeo/áudio → produce
- Aprender/evoluir/scraper/buscar dados → learn
"""


class Orchestrator:

    async def classify(self, user_prompt: str) -> TaskContext:
        data = await claude.call_structured(
            prompt=f"Prompt do usuário:\n{user_prompt}",
            system=CLASSIFY_SYSTEM,
        )
        ctx = TaskContext(original_prompt=user_prompt)
        ctx.mode = PipelineMode(data.get("mode", "create"))
        ctx.niche = data.get("niche", "")
        ctx.platform = data.get("platform", "")
        ctx.content_type = data.get("content_type", "")
        ctx.tone = data.get("tone", "")
        ctx.references = data.get("references", [])
        ctx.language = data.get("language", "pt-BR")
        return ctx

    async def execute(self, user_prompt: str) -> dict:
        ctx = await self.classify(user_prompt)
        result = {"context": ctx, "outputs": {}}

        runners = {
            PipelineMode.RESEARCH: self._run_research,
            PipelineMode.CREATE: self._run_creation,
            PipelineMode.OPTIMIZE: self._run_optimization,
            PipelineMode.PRODUCE: self._run_production,
            PipelineMode.LEARN: self._run_learning,
        }

        if ctx.mode == PipelineMode.FULL:
            # Pipeline completo: scrape → analisa → cria → otimiza
            research = await self._run_research(ctx)
            ctx.extra["research"] = research
            creation = await self._run_creation(ctx)
            optimization = await self._run_optimization(ctx, content=creation)
            result["outputs"] = {
                "research": research,
                "creation": creation,
                "optimization": optimization,
            }
        elif ctx.mode in runners:
            result["outputs"] = await runners[ctx.mode](ctx)

        return result

    # ------------------------------------------------------------------
    # Pipelines
    # ------------------------------------------------------------------

    async def _run_research(self, ctx: TaskContext) -> dict:
        """Fase 2: tenta scraper real primeiro, usa Claude como fallback."""
        scraped_data = []

        # Tenta scraper real se YouTube API key disponível
        try:
            from youtube_scraper import youtube_scraper
            from scraper_cache import cache_get, cache_set, cache_key_for_scrape, save_scraped

            if youtube_scraper.is_configured() and ctx.niche:
                cache_key = cache_key_for_scrape("youtube", ctx.niche, ctx.language)
                cached = cache_get(cache_key)

                if cached:
                    scraped_data = cached.get("items", [])
                else:
                    # Busca dados frescos
                    items = await youtube_scraper.search_viral(
                        niche=ctx.niche,
                        language=ctx.language,
                        days_back=30,
                        max_results=20,
                    )
                    if items:
                        cache_set(cache_key, {"items": items})
                        save_scraped(items)
                        scraped_data = items

        except Exception as e:
            print(f"[Orchestrator] scraper error (fallback to Claude): {e}")

        # Passa dados reais para o analyzer se disponíveis
        from modules.intelligence.analyzer import ContentAnalyzer
        from modules.intelligence.dna_extractor import DNAExtractor

        if scraped_data:
            ctx.extra["scraped_samples"] = scraped_data[:10]

        analysis = await ContentAnalyzer().analyze(ctx)
        dna = await DNAExtractor().extract(ctx, analysis)

        # Verifica se há DNA evoluído no banco (melhor que o gerado agora)
        try:
            from memory.store import get_best_dnas_v2, has_real_dna
            if has_real_dna(ctx.niche):
                evolved_dnas = get_best_dnas_v2(ctx.niche, ctx.platform, limit=2)
                if evolved_dnas:
                    dna["evolved_patterns"] = evolved_dnas
                    dna["_source"] = "real_data + scraper"
        except Exception:
            pass

        return {
            "analysis": analysis,
            "viral_dna": dna,
            "data_source": "youtube_api" if scraped_data else "claude_knowledge",
            "samples_used": len(scraped_data),
        }

    async def _run_creation(self, ctx: TaskContext) -> dict:
        from modules.creation.ideator import Ideator
        from modules.creation.scriptwriter import ScriptWriter
        from modules.creation.refiner import Refiner

        # Injeta DNA evoluído no contexto se disponível
        if ctx.niche and not ctx.extra.get("research"):
            try:
                from memory.store import get_best_dnas_v2, has_real_dna
                if has_real_dna(ctx.niche):
                    ctx.extra["evolved_dnas"] = get_best_dnas_v2(
                        ctx.niche, ctx.platform, limit=2
                    )
            except Exception:
                pass

        ideas = await Ideator().generate(ctx)
        script = await ScriptWriter().write(ctx, ideas)
        final = await Refiner().refine(ctx, script)
        return {"ideas": ideas, "script": script, "final": final}

    async def _run_optimization(self, ctx: TaskContext, content=None) -> dict:
        from modules.optimization.validator import Validator
        from modules.optimization.seo_optimizer import SEOOptimizer
        validation = await Validator().validate(ctx, content)
        seo = await SEOOptimizer().optimize(ctx, content)
        return {"validation": validation, "seo": seo}

    async def _run_production(self, ctx: TaskContext) -> dict:
        from integrations.manager import IntegrationManager
        return await IntegrationManager().produce(ctx)

    async def _run_learning(self, ctx: TaskContext) -> dict:
        """Fase 2: roda ciclo de aprendizado autônomo."""
        report = {"steps": []}

        # 1. Scrape YouTube para o nicho
        try:
            from youtube_scraper import youtube_scraper
            from scraper_cache import save_scraped

            if youtube_scraper.is_configured():
                niche = ctx.niche or "geral"

                # Busca virais por search
                items = await youtube_scraper.search_viral(
                    niche=niche, language=ctx.language, days_back=30
                )
                # Busca top populares
                popular = await youtube_scraper.get_most_popular(
                    niche=niche, language=ctx.language
                )

                all_items = items + popular
                saved = save_scraped(all_items)
                report["steps"].append({
                    "step": "scraping",
                    "status": "ok",
                    "new_items": saved,
                    "total_found": len(all_items),
                })
            else:
                report["steps"].append({
                    "step": "scraping",
                    "status": "skipped",
                    "reason": "YOUTUBE_API_KEY não configurada",
                })
        except Exception as e:
            report["steps"].append({"step": "scraping", "status": "error", "error": str(e)})

        # 2. Extrai DNA do conteúdo novo
        try:
            from dna_evolver import dna_evolver
            result = await dna_evolver.run_cycle(niche=ctx.niche)
            report["steps"].append({"step": "dna_extraction", **result})
        except Exception as e:
            report["steps"].append({"step": "dna_extraction", "status": "error", "error": str(e)})

        # 3. Estatísticas do banco
        try:
            from memory.store import get_scraping_stats
            report["database_stats"] = get_scraping_stats()
        except Exception:
            pass

        return report


orchestrator = Orchestrator()
