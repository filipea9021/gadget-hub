"""
Router de Skills — endpoint direto para cada skill.

Permite chamar skills específicas por nome, sem passar pelo
roteamento LLM do Cérebro Central. Útil para o n8n e integrações
que já sabem qual skill precisam.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()


class SkillRequest(BaseModel):
    """Payload para executar uma skill."""

    comando: str = Field(
        default="",
        description="Comando ou descrição do que a skill deve fazer",
    )
    action: Optional[str] = Field(
        default=None,
        description="Ação específica (ex: 'upscale', 'remove_bg', 'criar_produto')",
    )
    dados: Optional[dict[str, Any]] = Field(
        default=None,
        description="Dados de entrada (produto, imagem, etc.)",
    )
    contexto: Optional[dict[str, Any]] = Field(
        default=None,
        description="Contexto de uma etapa anterior do pipeline",
    )


class SkillResponse(BaseModel):
    """Resposta padronizada de qualquer skill."""

    status: str
    skill: str
    dados: Optional[dict[str, Any]] = None
    mensagem: Optional[str] = None


@router.post("/skills/{skill_name}", response_model=SkillResponse)
async def execute_skill(
    skill_name: str, request: Request, body: SkillRequest
) -> SkillResponse:
    """
    Executa uma skill específica pelo nome.

    Skills disponíveis:
    - **dev** — Gerar código/projetos
    - **pesquisa_produtos** — Pesquisar produtos trending
    - **criacao_site** — Criar landing pages
    - **marketing** — Campanhas de marketing
    - **automacao** — Automação geral
    - **shopify** — Publicar produtos na loja
    - **content_generator** — Gerar conteúdo com LLM
    - **imagens** — Processar imagens (upsampler.com)
    - **n8n** — Disparar workflows n8n
    - **data_core** — Memória, media e dados (Supabase)
    """
    cerebro = request.app.state.cerebro
    skill_info = cerebro.registry.get(skill_name)

    if not skill_info:
        available = [s.name for s in cerebro.registry.list_active()]
        raise HTTPException(
            status_code=404,
            detail={
                "erro": f"Skill '{skill_name}' não encontrada",
                "skills_disponiveis": available,
            },
        )

    # Monta o comando combinando ação + comando + dados
    command = body.comando
    if body.action and not command:
        command = body.action
    if not command:
        command = f"Executar {skill_name}"

    # Contexto = dados + contexto extra
    context = body.contexto or {}
    if body.dados:
        context.update(body.dados)

    # Executa
    from core.registry import SkillRuntime

    try:
        if skill_info.runtime == SkillRuntime.PYTHON:
            result = await cerebro._execute_python_skill(
                skill_info, command, context or None
            )
        else:
            result = cerebro._execute_js_skill(
                skill_info, command, context or None
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"erro": f"Erro ao executar skill '{skill_name}'", "detalhe": str(e)},
        )

    return SkillResponse(
        status=result.get("status", "erro"),
        skill=skill_name,
        dados=result.get("dados"),
        mensagem=result.get("mensagem"),
    )


@router.get("/skills", response_model=list[dict[str, Any]])
async def list_skills(request: Request) -> list[dict[str, Any]]:
    """Lista todas as skills disponíveis com detalhes."""
    cerebro = request.app.state.cerebro
    skills_list = []

    for skill in cerebro.registry.list_all():
        skills_list.append({
            "nome": skill.name,
            "descricao": skill.description,
            "runtime": skill.runtime.value,
            "status": skill.status.value,
            "capabilities": skill.capabilities,
            "keywords": skill.keywords,
            "endpoint": f"/api/skills/{skill.name}",
        })

    return skills_list
