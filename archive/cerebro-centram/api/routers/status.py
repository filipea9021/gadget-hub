"""
Router de Status e Health Check.

Endpoints para monitoramento do sistema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check simples — retorna se a API está online."""
    return {
        "status": "online",
        "servico": "Cérebro Centram API",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/status")
async def system_status(request: Request) -> dict[str, Any]:
    """
    Status completo do sistema.

    Retorna todas as skills, contagem de operações,
    provider LLM ativo, e detalhes de cada skill.
    """
    cerebro = request.app.state.cerebro
    status = cerebro.get_status()

    # Adiciona info da API
    status["api"] = {
        "versao": "0.1.0",
        "endpoints": {
            "brain": "POST /api/brain",
            "skills": "POST /api/skills/{skill_name}",
            "listar_skills": "GET /api/skills",
            "status": "GET /api/status",
            "health": "GET /api/health",
            "docs": "GET /docs",
        },
    }

    return status
