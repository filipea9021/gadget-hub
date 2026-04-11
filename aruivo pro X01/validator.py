"""Validador de qualidade — garante que o conteúdo atende aos padrões."""
from api.claude_client import claude

SYSTEM = """Valide a qualidade do conteúdo. Retorne JSON:
{
  "approved": true|false,
  "score": 1-10,
  "checks": {
    "hook_strength": 1-10,
    "structure": 1-10,
    "originality": 1-10,
    "engagement_potential": 1-10,
    "cta_effectiveness": 1-10
  },
  "issues": ["problemas encontrados"],
  "suggestions": ["sugestões de melhoria"]
}"""

class Validator:
    async def validate(self, ctx, content: dict = None) -> dict:
        prompt = f"""Valide este conteúdo:
Conteúdo: {content}
Plataforma: {ctx.platform}
Nicho: {ctx.niche}"""
        return await claude.call_structured(prompt, system=SYSTEM, temperature=0.2)
