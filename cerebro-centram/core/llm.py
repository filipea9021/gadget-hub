"""
Camada de abstração para LLMs.
Suporta Anthropic (Claude), OpenAI e Ollama de forma unificada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config.settings import LLMProvider, Settings


@dataclass
class LLMResponse:
    """Resposta padronizada de qualquer LLM."""
    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMClient:
    """
    Cliente unificado que abstrai a comunicação com diferentes LLMs.
    Permite trocar de provider mudando apenas a config.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.llm_provider
        self._client = None

    def _get_anthropic_client(self):
        import anthropic
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        return self._client

    def _get_openai_client(self):
        import openai
        if self._client is None:
            self._client = openai.OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def _get_ollama_client(self):
        import ollama
        if self._client is None:
            self._client = ollama.Client(host=self.settings.ollama_base_url)
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """
        Gera uma resposta do LLM escolhido.

        Args:
            system_prompt: Instrução de sistema (papel do agente)
            user_message: Mensagem do usuário/tarefa
            max_tokens: Limite de tokens na resposta
            temperature: Criatividade (0.0 = determinístico, 1.0 = criativo)
        """
        if self.provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(system_prompt, user_message, max_tokens, temperature)
        elif self.provider == LLMProvider.OPENAI:
            return await self._generate_openai(system_prompt, user_message, max_tokens, temperature)
        elif self.provider == LLMProvider.OLLAMA:
            return await self._generate_ollama(system_prompt, user_message, max_tokens, temperature)
        else:
            raise ValueError(f"Provider não suportado: {self.provider}")

    async def _generate_anthropic(
        self, system_prompt: str, user_message: str, max_tokens: int, temperature: float
    ) -> LLMResponse:
        client = self._get_anthropic_client()
        response = client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return LLMResponse(
            content=response.content[0].text,
            model=self.settings.anthropic_model,
            provider="anthropic",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    async def _generate_openai(
        self, system_prompt: str, user_message: str, max_tokens: int, temperature: float
    ) -> LLMResponse:
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=self.settings.openai_model,
            provider="openai",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    async def _generate_ollama(
        self, system_prompt: str, user_message: str, max_tokens: int, temperature: float
    ) -> LLMResponse:
        client = self._get_ollama_client()
        response = client.chat(
            model=self.settings.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        return LLMResponse(
            content=response["message"]["content"],
            model=self.settings.ollama_model,
            provider="ollama",
        )
