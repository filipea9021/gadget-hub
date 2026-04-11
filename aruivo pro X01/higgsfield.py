"""
CIS — Integração com Higgsfield AI
Gera imagens, vídeos, áudio via cloud.higgsfield.ai
SDK: pip install higgsfield-client
Env: HF_API_KEY + HF_API_SECRET (ou HF_KEY="key:secret")
"""

import os
import asyncio
from typing import Optional

try:
    import higgsfield_client
    HAS_SDK = True
except ImportError:
    HAS_SDK = False


class HiggsFieldClient:
    """Wrapper async do Higgsfield para o CIS."""

    # Modelos disponíveis (atualizar conforme catálogo)
    MODELS = {
        "image": "bytedance/seedream/v4/text-to-image",
        "video": "higgsfield/image-to-video",
        # Adicionar conforme necessário:
        # "lipsync": "higgsfield/lipsync",
        # "upscale": "higgsfield/video-upscale",
    }

    def __init__(self):
        if not HAS_SDK:
            raise ImportError("SDK não instalado. Rode: pip install higgsfield-client")

    async def generate_image(
        self,
        prompt: str,
        resolution: str = "2K",
        aspect_ratio: str = "16:9",
    ) -> dict:
        """Gera imagem a partir de texto."""
        result = await higgsfield_client.subscribe_async(
            self.MODELS["image"],
            arguments={
                "prompt": prompt,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "camera_fixed": False,
            },
        )
        return {
            "type": "image",
            "url": result["images"][0]["url"] if result.get("images") else None,
            "raw": result,
        }

    async def generate_video(
        self,
        image_url: str,
        prompt: str = "",
        preset: Optional[str] = None,
    ) -> dict:
        """Gera vídeo a partir de imagem (image-to-video)."""
        args = {"image_url": image_url}
        if prompt:
            args["prompt"] = prompt
        if preset:
            args["preset"] = preset

        result = await higgsfield_client.subscribe_async(
            self.MODELS["video"],
            arguments=args,
        )
        return {
            "type": "video",
            "url": result.get("video_url") or result.get("url"),
            "raw": result,
        }

    async def submit_and_poll(self, model: str, arguments: dict) -> dict:
        """Chamada genérica com polling — para qualquer modelo do catálogo."""
        controller = await higgsfield_client.submit_async(model, arguments=arguments)
        async for status in controller.poll_request_status():
            if isinstance(status, higgsfield_client.Completed):
                break
            elif isinstance(status, (higgsfield_client.Failed, higgsfield_client.NSFW, higgsfield_client.Cancelled)):
                return {"status": "failed", "error": str(type(status).__name__)}
        result = await controller.get()
        return {"status": "completed", "result": result}


# Singleton
higgsfield = HiggsFieldClient() if HAS_SDK else None
