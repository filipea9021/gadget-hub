"""
CIS — Integration Manager (v2)
Gerencia todas as integrações: Higgsfield, Remotion, Video Toolkit,
Image Gen, Content Repurposing, SEO, e bibliotecas da comunidade.
"""

from api.claude_client import claude


PRODUCTION_SYSTEM = """Você é o gerente de produção do CIS. Dado o contexto, planeje o que produzir.
Retorne JSON:
{
  "tasks": [
    {
      "type": "image" | "video" | "audio" | "text_content" | "seo",
      "tool": "higgsfield" | "remotion" | "video_toolkit" | "gemini_image" | "canvas_design" | "content_writer" | "twitter_optimizer" | "seo_audit" | "repurposer",
      "prompt": "descrição do que produzir",
      "platform": "plataforma alvo",
      "priority": 1-5
    }
  ],
  "strategy": "explicação da estratégia",
  "pipeline_order": ["ordem de execução dos tasks por tipo"]
}

Ferramentas disponíveis:
- higgsfield: imagem text-to-image, image-to-video (cinematográfico)
- remotion: vídeo programático (animação, explainer, motion graphics)
- video_toolkit: voiceover (Qwen3-TTS/ElevenLabs), música (ACE-Step), SFX
- gemini_image: geração de imagem via Google Gemini
- canvas_design: design estático (posters, infográficos, PNG/PDF)
- content_writer: escrita com pesquisa e citações
- twitter_optimizer: otimização para algoritmo do X/Twitter
- seo_audit: SEO técnico (schema, sitemap, meta, keywords)
- repurposer: transformar 1 conteúdo em múltiplas plataformas
"""


class IntegrationManager:
    async def produce(self, ctx) -> dict:
        """Pipeline principal de produção. Planeja e executa."""
        plan = await claude.call_structured(
            prompt=f"""Planeje a produção para:
Pedido: {ctx.original_prompt}
Nicho: {ctx.niche}
Plataforma: {ctx.platform}
Tipo: {ctx.content_type}
Tom: {ctx.tone}
Pesquisa prévia: {ctx.extra.get('research', 'nenhuma')}""",
            system=PRODUCTION_SYSTEM,
        )

        results = {"plan": plan, "outputs": []}
        tasks = sorted(plan.get("tasks", []), key=lambda t: t.get("priority", 5))

        for task in tasks:
            tool = task.get("tool", "")
            try:
                if tool == "higgsfield":
                    out = await self._run_higgsfield(task)
                elif tool == "remotion":
                    out = await self._run_remotion(task, ctx)
                elif tool == "video_toolkit":
                    out = await self._run_video_toolkit(task)
                elif tool in ("gemini_image", "canvas_design"):
                    out = await self._run_image_gen(task)
                elif tool == "content_writer":
                    out = await self._run_content_writer(task, ctx)
                elif tool == "twitter_optimizer":
                    out = await self._run_twitter_optimizer(task, ctx)
                elif tool == "seo_audit":
                    out = await self._run_seo(task, ctx)
                elif tool == "repurposer":
                    out = await self._run_repurposer(task, ctx)
                else:
                    out = {"status": "unknown_tool", "tool": tool}
            except Exception as e:
                out = {"status": "error", "tool": tool, "error": str(e)}

            results["outputs"].append({"task": task, "result": out})

        return results

    async def _run_higgsfield(self, task: dict) -> dict:
        try:
            from integrations.higgsfield import higgsfield
            if not higgsfield:
                return {"status": "sdk_not_installed", "install": "pip install higgsfield-client"}
        except ImportError:
            return {"status": "sdk_not_installed", "install": "pip install higgsfield-client"}

        if task["type"] == "image":
            return await higgsfield.generate_image(prompt=task["prompt"])
        elif task["type"] == "video":
            # Precisa de imagem como input — busca nos outputs anteriores
            return {"status": "needs_image_input", "message": "Gere imagem primeiro via higgsfield image"}
        return {"status": "unsupported_type"}

    async def _run_remotion(self, task: dict, ctx) -> dict:
        from integrations.video_producer import video_producer
        plan = await video_producer.plan_production(ctx, {"prompt": task["prompt"]})
        code = await video_producer.produce_remotion(plan, {"prompt": task["prompt"]})
        return {"status": "remotion_code_generated", "plan": plan, "code": code}

    async def _run_video_toolkit(self, task: dict) -> dict:
        from integrations.video_producer import video_producer
        plan = {"audio_plan": {
            "voiceover": "voice" in task.get("prompt", "").lower() or task["type"] == "audio",
            "voiceover_provider": "qwen3-tts",
            "music": "music" in task.get("prompt", "").lower() or "música" in task.get("prompt", "").lower(),
            "music_style": task.get("prompt", "upbeat"),
            "sfx": "sfx" in task.get("prompt", "").lower(),
        }}
        return await video_producer.plan_audio(plan)

    async def _run_image_gen(self, task: dict) -> dict:
        """Rota para geração de imagem (Gemini ou Canvas Design)."""
        prompt = f"""Gere especificações detalhadas para esta imagem:
Pedido: {task['prompt']}
Plataforma: {task.get('platform', 'instagram')}

Retorne JSON:
{{"image_prompt": "prompt otimizado para geração", "style": "estilo visual", "aspect_ratio": "ratio", "resolution": "WxH", "text_overlay": "texto se houver"}}"""
        specs = await claude.call_structured(prompt, temperature=0.6)
        return {"status": "specs_generated", "tool": task["tool"], "specs": specs}

    async def _run_content_writer(self, task: dict, ctx) -> dict:
        """Content Research Writer — escrita com pesquisa."""
        prompt = f"""Escreva conteúdo de alta qualidade sobre:
Tema: {task['prompt']}
Plataforma: {task.get('platform', ctx.platform)}
Tom: {ctx.tone}
Idioma: {ctx.language}

Inclua: pesquisa, dados, hooks fortes, CTA.
Retorne JSON:
{{"content": "conteúdo completo", "sources": ["fontes usadas"], "hooks": ["ganchos alternativos"], "word_count": N}}"""
        return await claude.call_structured(prompt, temperature=0.7)

    async def _run_twitter_optimizer(self, task: dict, ctx) -> dict:
        """Twitter/X Algorithm Optimizer."""
        prompt = f"""Otimize este conteúdo para máximo alcance no X/Twitter:
Conteúdo: {task['prompt']}
Nicho: {ctx.niche}

Baseado no algoritmo open-source do Twitter, retorne JSON:
{{
  "optimized_tweet": "tweet otimizado",
  "thread_version": ["tweet 1", "tweet 2", "..."],
  "best_posting_time": "horário ideal",
  "engagement_prediction": "low|medium|high|viral",
  "algorithm_tips": ["dicas específicas do algoritmo"],
  "hashtags": ["hashtags otimizadas"]
}}"""
        return await claude.call_structured(prompt, temperature=0.5)

    async def _run_seo(self, task: dict, ctx) -> dict:
        """SEO técnico completo."""
        prompt = f"""Faça uma auditoria SEO e otimize:
Conteúdo: {task['prompt']}
Plataforma: {task.get('platform', ctx.platform)}
Nicho: {ctx.niche}

Retorne JSON:
{{
  "title_options": ["3 títulos SEO"],
  "meta_description": "description otimizada",
  "keywords": {{"primary": ["main"], "secondary": ["secondary"], "long_tail": ["long tail"]}},
  "schema_markup": "JSON-LD sugerido",
  "internal_linking_suggestions": ["sugestões"],
  "technical_issues": ["problemas encontrados"],
  "score": 1-100
}}"""
        return await claude.call_structured(prompt, temperature=0.3)

    async def _run_repurposer(self, task: dict, ctx) -> dict:
        """Content Repurposer — 1 conteúdo → múltiplas plataformas."""
        prompt = f"""Transforme este conteúdo para múltiplas plataformas:
Conteúdo original: {task['prompt']}
Idioma: {ctx.language}

Retorne JSON:
{{
  "linkedin": {{"post": "texto", "hashtags": ["tags"], "format": "text|carousel|document"}},
  "instagram": {{"caption": "texto", "hashtags": ["tags"], "visual_suggestion": "descrição do visual", "format": "post|carousel|reel"}},
  "twitter": {{"tweet": "texto", "thread": ["tweets se for thread"], "hashtags": ["tags"]}},
  "tiktok": {{"script": "roteiro curto", "hook": "gancho dos 3 primeiros segundos", "hashtags": ["tags"]}},
  "youtube": {{"title": "título", "description": "descrição", "tags": ["tags"]}}
}}"""
        return await claude.call_structured(prompt, temperature=0.6)


integration_manager = IntegrationManager()
