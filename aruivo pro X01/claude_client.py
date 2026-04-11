"""
CIS - Cliente centralizado para API do Claude
Todas as chamadas ao Claude passam por aqui.
"""

import json
import httpx
from typing import Optional
from core.config import config


class ClaudeClient:
    def __init__(self):
        self.api_key = config.claude.api_key
        self.model = config.claude.model
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    async def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Chamada simples ao Claude. Retorna texto."""
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or config.claude.max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self.base_url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        return self._extract_text(data)

    async def call_structured(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
    ) -> dict:
        """Chamada ao Claude esperando JSON de volta."""
        system_full = (system + "\n\n" if system else "")
        system_full += "Responda APENAS com JSON válido. Sem markdown, sem explicações."
        
        text = await self.call(prompt, system=system_full, temperature=temperature)
        # Limpa possíveis fences de markdown
        text = text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(text)

    def _extract_text(self, data: dict) -> str:
        blocks = data.get("content", [])
        return "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")


claude = ClaudeClient()
