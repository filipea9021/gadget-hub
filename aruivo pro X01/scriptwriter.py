"""Escritor de roteiros completos."""
from api.claude_client import claude

SYSTEM = """Você escreve roteiros de conteúdo viral. O roteiro deve ser completo e pronto para produção.
Retorne JSON:
{
  "title": "título do conteúdo",
  "hook": "primeiros 3 segundos / primeira frase",
  "sections": [
    {"timestamp": "0:00-0:03", "type": "hook|body|cta", "narration": "texto", "visual_notes": "o que aparece na tela"}
  ],
  "cta": "call to action final",
  "estimated_duration": "duração estimada",
  "tone_notes": "notas sobre tom e entrega"
}"""

class ScriptWriter:
    async def write(self, ctx, ideas: dict) -> dict:
        best_idea = ideas.get("ideas", [{}])[0]
        prompt = f"""Escreva um roteiro completo para:
Ideia: {best_idea}
Plataforma: {ctx.platform or 'qualquer'}
Tipo: {ctx.content_type or 'short'}
Tom: {ctx.tone or 'engajante'}
Idioma: {ctx.language}"""
        return await claude.call_structured(prompt, system=SYSTEM, temperature=0.8)
