"""
Configurações centrais do Cerebro Centram.
Carrega do .env e valida com Pydantic.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Configurações carregadas automaticamente do .env"""

    # ── LLM ──
    llm_provider: LLMProvider = LLMProvider.ANTHROPIC

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # ── Upsampler.com (Imagens) ──
    upsampler_api_key: Optional[str] = None

    # ── n8n Cloud (Workflows) ──
    n8n_base_url: Optional[str] = None
    n8n_api_key: Optional[str] = None

    # ── Shopify ──
    shopify_api_key: Optional[str] = None
    shopify_store_url: Optional[str] = None

    # ── GitHub ──
    github_token: Optional[str] = None

    # ── Paths ──
    output_dir: Path = Path("./output")
    templates_dir: Path = Path("./templates")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def validate_provider(self) -> None:
        """Verifica se a API key do provider escolhido está configurada."""
        if self.llm_provider == LLMProvider.ANTHROPIC and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY não configurada. "
                "Adicione no .env ou use LLM_PROVIDER=ollama para rodar localmente."
            )
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Adicione no .env ou use LLM_PROVIDER=ollama para rodar localmente."
            )


def get_settings() -> Settings:
    """Factory para obter settings validadas."""
    settings = Settings()
    return settings
