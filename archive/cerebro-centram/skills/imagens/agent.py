"""
Skill Imagens — Processamento de imagens com IA via upsampler.com.
Upscale, geração, edição e criação de assets visuais.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx
from rich.console import Console

from config.settings import Settings

console = Console()


class ImagensSkill:
    """
    Skill de processamento de imagens usando upsampler.com.

    Capacidades:
    - Upscale (melhorar resolução de imagens)
    - Geração de imagens de produtos com IA
    - Edição (remover fundo, ajustar, recortar)
    - Criação de assets para marketing (banners, thumbnails)
    """

    name = "imagens"
    description = "Processamento de imagens com IA via upsampler.com"
    API_BASE = "https://upsampler.com"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = getattr(settings, "upsampler_api_key", "")

    async def upscale(self, image_url: str, scale: int = 2) -> dict:
        """
        Faz upscale de uma imagem (melhora resolução).

        Args:
            image_url: URL da imagem original
            scale: Fator de escala (2x, 4x)
        """
        console.print(f"[dim]🖼️ Upscale {scale}x via upsampler.com...[/dim]")
        return await self._call_api("upscale", {
            "image_url": image_url,
            "scale": scale,
        })

    async def remove_background(self, image_url: str) -> dict:
        """Remove o fundo de uma imagem de produto."""
        console.print(f"[dim]🖼️ Removendo fundo via upsampler.com...[/dim]")
        return await self._call_api("remove-bg", {
            "image_url": image_url,
        })

    async def generate_product_image(
        self, product_name: str, style: str = "professional product photo"
    ) -> dict:
        """
        Gera uma imagem de produto com IA.

        Args:
            product_name: Nome/descrição do produto
            style: Estilo desejado
        """
        console.print(f"[dim]🖼️ Gerando imagem para '{product_name}'...[/dim]")
        return await self._call_api("generate", {
            "prompt": f"{style} of {product_name}, white background, high quality, 4k",
            "style": style,
        })

    async def create_banner(
        self,
        text: str,
        product_image_url: Optional[str] = None,
        size: str = "1200x628",
    ) -> dict:
        """
        Cria um banner para redes sociais ou anúncios.

        Args:
            text: Texto do banner
            product_image_url: URL da imagem do produto (opcional)
            size: Tamanho do banner (1200x628 para Facebook, 1080x1080 para Instagram)
        """
        console.print(f"[dim]🖼️ Criando banner {size}...[/dim]")
        payload = {
            "text": text,
            "size": size,
        }
        if product_image_url:
            payload["product_image"] = product_image_url
        return await self._call_api("banner", payload)

    async def batch_process(self, image_urls: list[str], operation: str = "upscale") -> dict:
        """
        Processa múltiplas imagens em lote.

        Args:
            image_urls: Lista de URLs de imagens
            operation: Operação a aplicar (upscale, remove-bg)
        """
        console.print(f"[dim]🖼️ Processamento em lote: {len(image_urls)} imagens ({operation})...[/dim]")
        results = []
        for i, url in enumerate(image_urls):
            console.print(f"[dim]  ({i+1}/{len(image_urls)}) Processando...[/dim]")
            if operation == "upscale":
                result = await self.upscale(url)
            elif operation == "remove-bg":
                result = await self.remove_background(url)
            else:
                result = {"status": "erro", "mensagem": f"Operação '{operation}' não suportada"}
            results.append(result)

        succeeded = sum(1 for r in results if r.get("status") == "sucesso")
        return {
            "status": "sucesso" if succeeded == len(results) else "parcial",
            "skill": "imagens",
            "dados": {"results": results, "total": len(results), "succeeded": succeeded},
            "mensagem": f"Processadas {succeeded}/{len(results)} imagens",
        }

    async def _call_api(self, endpoint: str, payload: dict) -> dict:
        """Chama a API do upsampler.com."""
        if not self.api_key:
            # Sem API key, retorna instrução para configurar
            return {
                "status": "pendente",
                "skill": "imagens",
                "dados": {
                    "endpoint": endpoint,
                    "payload": payload,
                    "setup": "Configure UPSAMPLER_API_KEY no .env ou use via n8n workflow",
                },
                "mensagem": (
                    f"Operação '{endpoint}' preparada. "
                    "Configure UPSAMPLER_API_KEY no .env para execução direta, "
                    "ou use o workflow n8n que já inclui a integração com upsampler.com."
                ),
            }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.API_BASE}/api/v1/{endpoint}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                return {
                    "status": "sucesso",
                    "skill": "imagens",
                    "dados": response.json(),
                    "mensagem": f"Operação '{endpoint}' concluída",
                }
        except httpx.HTTPError as e:
            return {
                "status": "erro",
                "skill": "imagens",
                "dados": None,
                "mensagem": f"Erro na API upsampler: {str(e)}",
            }
