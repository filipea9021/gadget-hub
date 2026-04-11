"""
CIS — Video Producer
Conecta o pipeline de produção com as ferramentas de vídeo.
Rota entre Remotion (animação), Higgsfield (cinematográfico), e Video Toolkit (áudio).
"""

from api.claude_client import claude
from typing import Optional


ROUTE_SYSTEM = """Você é o diretor de produção de vídeo do CIS.
Dado o roteiro e contexto, decida a melhor abordagem de produção.
Retorne JSON:
{
  "video_engine": "remotion" | "higgsfield" | "both",
  "audio_plan": {
    "voiceover": true|false,
    "voiceover_provider": "qwen3-tts" | "elevenlabs" | "none",
    "music": true|false,
    "music_style": "estilo descritivo ou none",
    "sfx": true|false
  },
  "format": {
    "resolution": "1080x1920" | "1920x1080" | "1080x1080",
    "fps": 30,
    "duration_seconds": numero,
    "platform": "tiktok" | "youtube" | "instagram" | "linkedin"
  },
  "scenes": [
    {
      "scene_number": 1,
      "type": "hook" | "body" | "cta",
      "visual_approach": "descrição do visual",
      "text_overlay": "texto na tela ou none",
      "transition": "tipo de transição"
    }
  ],
  "reasoning": "por que esta abordagem"
}

Regras:
- Animação/explainer/dados → remotion
- Cinematográfico/realista/produto → higgsfield
- Combinar quando precisar de ambos
- Voiceover sempre que tiver narração no roteiro
- Música quase sempre (a não ser que o silêncio seja intencional)
"""


class VideoProducer:
    async def plan_production(self, ctx, script: dict) -> dict:
        """Cria plano de produção baseado no roteiro."""
        prompt = f"""Planeje a produção de vídeo:
Roteiro: {script}
Plataforma: {ctx.platform or 'tiktok'}
Nicho: {ctx.niche}
Tom: {ctx.tone}
Tipo: {ctx.content_type}"""
        return await claude.call_structured(prompt, system=ROUTE_SYSTEM)

    async def produce_remotion(self, plan: dict, script: dict) -> dict:
        """Gera código Remotion para o vídeo."""
        prompt = f"""Gere o código React/Remotion completo para este vídeo:
Plano: {plan}
Roteiro: {script}

O código deve:
1. Importar de 'remotion' (useCurrentFrame, interpolate, Sequence, etc.)
2. Respeitar safe zones da plataforma
3. Usar fontes mínimas de 28px
4. Incluir animações suaves
5. Ser um componente exportável

Retorne JSON:
{{"code": "código React completo", "composition_config": {{"width": X, "height": Y, "fps": 30, "durationInFrames": N}}}}"""
        return await claude.call_structured(prompt, temperature=0.7)

    async def produce_higgsfield(self, plan: dict, script: dict) -> dict:
        """Produz via Higgsfield (imagem → vídeo)."""
        try:
            from integrations.higgsfield import higgsfield
            if not higgsfield:
                return {"status": "sdk_not_installed"}
        except ImportError:
            return {"status": "sdk_not_installed"}

        results = []
        for scene in plan.get("scenes", []):
            # Gera imagem base
            img = await higgsfield.generate_image(
                prompt=scene.get("visual_approach", ""),
                aspect_ratio="9:16" if "1920" in str(plan.get("format", {}).get("resolution", "")) else "16:9",
            )
            if img.get("url"):
                # Gera vídeo a partir da imagem
                vid = await higgsfield.generate_video(
                    image_url=img["url"],
                    prompt=scene.get("visual_approach", ""),
                )
                results.append({"scene": scene["scene_number"], "image": img, "video": vid})

        return {"scenes": results}

    async def plan_audio(self, plan: dict) -> dict:
        """Retorna comandos de áudio para o Video Toolkit."""
        audio = plan.get("audio_plan", {})
        commands = []

        if audio.get("voiceover"):
            provider = audio.get("voiceover_provider", "qwen3-tts")
            if provider == "qwen3-tts":
                commands.append({
                    "tool": "voiceover",
                    "command": "python tools/voiceover.py --provider qwen3 --scene-dir public/audio/scenes --json",
                })
            elif provider == "elevenlabs":
                commands.append({
                    "tool": "voiceover",
                    "command": "python tools/voiceover.py --script script.md --output voiceover.mp3",
                })

        if audio.get("music"):
            style = audio.get("music_style", "upbeat corporate")
            commands.append({
                "tool": "music",
                "command": f'python tools/music_gen.py --prompt "{style}" --duration 60 --output music.mp3',
            })

        if audio.get("sfx"):
            commands.append({
                "tool": "sfx",
                "command": "python tools/sfx.py --preset whoosh --output sfx.mp3",
            })

        return {"audio_commands": commands}


video_producer = VideoProducer()
