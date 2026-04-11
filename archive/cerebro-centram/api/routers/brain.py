"""
Router do Cérebro Central — o endpoint mais importante.

Recebe comandos em linguagem natural e roteia para a skill certa.
Suporta execução single (1 skill) e flow (multi-skill com dependências).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()


class BrainRequest(BaseModel):
    """Comando para o Cérebro Central."""

    comando: str = Field(..., description="Comando em linguagem natural", examples=[
        "Pesquisar produtos trending de gadgets e criar landing page",
        "Gerar imagem do produto Smart LED Strip",
        "Executar fluxo completo para o nicho de smart home",
    ])
    contexto: Optional[dict[str, Any]] = Field(
        default=None,
        description="Contexto extra (output de skill anterior, parâmetros, etc.)",
    )


class BrainResponse(BaseModel):
    """Resposta do Cérebro Central."""

    status: str = Field(..., description="sucesso | parcial | erro | skip")
    modo: Optional[str] = Field(default=None, description="single | flow | none")
    skill: Optional[str] = Field(default=None, description="Skill executada (modo single)")
    dados: Optional[dict[str, Any]] = Field(default=None, description="Dados retornados")
    mensagem: Optional[str] = Field(default=None, description="Mensagem para o operador")


@router.post("/brain", response_model=BrainResponse)
async def execute_brain(request: Request, body: BrainRequest) -> BrainResponse:
    """
    Cérebro Central — envia um comando em linguagem natural.

    O LLM analisa a intenção, escolhe a melhor skill (ou combina várias),
    e executa automaticamente. Retorna o resultado completo.

    Exemplos:
    - "Pesquisar produto trending de tecnologia"
    - "Criar landing page para fones bluetooth com design escuro"
    - "Processar todas as imagens do produto X e publicar no Shopify"
    """
    cerebro = request.app.state.cerebro

    # Injeta contexto no comando se fornecido
    if body.contexto:
        cerebro.context.update(body.contexto)

    result = await cerebro.execute(body.comando)

    return BrainResponse(
        status=result.get("status", "erro"),
        modo=result.get("mode") or result.get("modo"),
        skill=result.get("skill"),
        dados=result.get("dados") or result.get("resultados"),
        mensagem=result.get("mensagem"),
    )
