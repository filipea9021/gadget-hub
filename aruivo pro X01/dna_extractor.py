"""Extrator de DNA viral — identifica a fórmula por trás do sucesso."""
from api.claude_client import claude

SYSTEM = """Você extrai o "DNA viral" de conteúdos de sucesso.
Retorne JSON:
{
  "hook_formula": "fórmula do gancho (ex: pergunta + choque + curiosidade)",
  "structure_template": "template da estrutura narrativa",
  "retention_tactics": ["táticas de retenção identificadas"],
  "virality_score_factors": ["fatores que contribuem para viralização"],
  "replicable_pattern": "padrão replicável em formato passo-a-passo"
}"""

class DNAExtractor:
    async def extract(self, ctx, analysis: dict) -> dict:
        prompt = f"""Baseado nesta análise, extraia o DNA viral:
Análise: {analysis}
Nicho: {ctx.niche}
Plataforma: {ctx.platform}"""
        return await claude.call_structured(prompt, system=SYSTEM)
