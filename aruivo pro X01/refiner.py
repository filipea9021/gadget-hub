"""Refinador criativo — eleva a qualidade do conteúdo."""
from api.claude_client import claude

SYSTEM = """Você refina roteiros para máximo impacto. Melhore sem mudar a essência.
Retorne JSON:
{
  "refined_script": {mesmo formato do script original, mas melhorado},
  "changes_made": ["lista de melhorias aplicadas"],
  "quality_score": 1-10,
  "viral_potential": "low|medium|high|very_high"
}"""

class Refiner:
    async def refine(self, ctx, script: dict) -> dict:
        prompt = f"""Refine este roteiro para máximo impacto viral:
Roteiro: {script}
Plataforma: {ctx.platform}
Tom desejado: {ctx.tone}"""
        return await claude.call_structured(prompt, system=SYSTEM, temperature=0.5)
