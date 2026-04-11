"""Otimizador SEO — título, descrição, hashtags, thumbnail text."""
from api.claude_client import claude

SYSTEM = """Otimize o conteúdo para máxima descoberta. Retorne JSON:
{
  "titles": ["3 opções de título otimizado"],
  "description": "descrição otimizada",
  "hashtags": ["hashtags relevantes"],
  "tags": ["tags para a plataforma"],
  "thumbnail_text": "texto sugerido para thumbnail",
  "best_posting_time": "melhor horário sugerido",
  "platform_tips": ["dicas específicas da plataforma"]
}"""

class SEOOptimizer:
    async def optimize(self, ctx, content: dict = None) -> dict:
        prompt = f"""Otimize para publicação:
Conteúdo: {content}
Plataforma: {ctx.platform or 'youtube'}
Nicho: {ctx.niche}
Idioma: {ctx.language}"""
        return await claude.call_structured(prompt, system=SYSTEM)
