"""Gerador de ideias baseado em padrões virais."""
from api.claude_client import claude

SYSTEM = """Você gera ideias de conteúdo viral. Cada ideia deve ser original mas baseada em padrões comprovados.
Retorne JSON:
{
  "ideas": [
    {
      "title": "título da ideia",
      "hook": "gancho principal",
      "angle": "ângulo único",
      "why_viral": "por que tem potencial viral",
      "difficulty": "easy|medium|hard"
    }
  ]
}
Gere 3-5 ideias ordenadas por potencial viral."""

class Ideator:
    async def generate(self, ctx) -> dict:
        research = ctx.extra.get("research", {})
        prompt = f"""Gere ideias de conteúdo viral:
Pedido: {ctx.original_prompt}
Nicho: {ctx.niche or 'geral'}
Plataforma: {ctx.platform or 'qualquer'}
Tipo: {ctx.content_type or 'qualquer'}
Tom: {ctx.tone or 'qualquer'}
DNA viral disponível: {research.get('viral_dna', 'nenhum')}"""
        return await claude.call_structured(prompt, system=SYSTEM)
