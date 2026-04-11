"""Módulo de análise de conteúdo viral."""
from api.claude_client import claude

SYSTEM = """Você é um analista de conteúdo viral. Dado o contexto, analise padrões de sucesso.
Retorne JSON:
{
  "hooks": ["ganchos eficazes identificados"],
  "structures": ["estruturas narrativas encontradas"],
  "emotional_triggers": ["gatilhos emocionais usados"],
  "pacing": "ritmo do conteúdo",
  "cta_patterns": ["padrões de call-to-action"],
  "engagement_drivers": ["o que gera engajamento"],
  "summary": "resumo da análise"
}"""

class ContentAnalyzer:
    async def analyze(self, ctx) -> dict:
        prompt = f"""Analise padrões virais para:
Nicho: {ctx.niche or 'geral'}
Plataforma: {ctx.platform or 'qualquer'}
Tipo: {ctx.content_type or 'qualquer'}
Contexto: {ctx.original_prompt}
Referências: {ctx.references}"""
        return await claude.call_structured(prompt, system=SYSTEM)
