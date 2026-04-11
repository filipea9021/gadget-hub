"""
Skill n8n — Integração com n8n Cloud para automação de workflows.
Permite ao Cérebro Central disparar, monitorar e criar fluxos automatizados.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx
from rich.console import Console
from rich.panel import Panel

from config.settings import Settings

console = Console()


class N8NSkill:
    """
    Skill de integração com n8n Cloud.

    Capacidades:
    - Disparar workflows via webhook
    - Monitorar execuções
    - Criar e atualizar workflows via API
    """

    name = "n8n"
    description = "Automação de workflows via n8n Cloud"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = getattr(settings, "n8n_base_url", "")
        self.api_key = getattr(settings, "n8n_api_key", "")

    async def trigger_webhook(self, webhook_url: str, payload: dict[str, Any]) -> dict:
        """
        Dispara um workflow via webhook do n8n.

        Args:
            webhook_url: URL do webhook (ex: https://seu-n8n.app.n8n.cloud/webhook/xxx)
            payload: Dados a enviar para o workflow
        """
        console.print(f"[dim]🔗 Disparando webhook n8n...[/dim]")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()

                return {
                    "status": "sucesso",
                    "skill": "n8n",
                    "dados": {
                        "status_code": response.status_code,
                        "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                    },
                    "mensagem": f"Workflow disparado com sucesso (HTTP {response.status_code})",
                }
        except httpx.HTTPError as e:
            return {
                "status": "erro",
                "skill": "n8n",
                "dados": None,
                "mensagem": f"Erro ao disparar webhook: {str(e)}",
            }

    async def trigger_workflow(self, workflow_id: str, data: Optional[dict] = None) -> dict:
        """
        Dispara um workflow pelo ID via API do n8n.

        Args:
            workflow_id: ID do workflow no n8n
            data: Dados de input para o workflow
        """
        if not self.base_url or not self.api_key:
            return {
                "status": "erro",
                "skill": "n8n",
                "mensagem": "N8N_BASE_URL e N8N_API_KEY não configurados no .env",
            }

        console.print(f"[dim]⚡ Disparando workflow {workflow_id}...[/dim]")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                    headers={"X-N8N-API-KEY": self.api_key},
                    json=data or {},
                )
                response.raise_for_status()
                return {
                    "status": "sucesso",
                    "skill": "n8n",
                    "dados": response.json(),
                    "mensagem": f"Workflow {workflow_id} ativado",
                }
        except httpx.HTTPError as e:
            return {"status": "erro", "skill": "n8n", "mensagem": str(e)}

    async def list_workflows(self) -> dict:
        """Lista todos os workflows no n8n."""
        if not self.base_url or not self.api_key:
            return {"status": "erro", "mensagem": "N8N_BASE_URL e N8N_API_KEY não configurados"}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/workflows",
                    headers={"X-N8N-API-KEY": self.api_key},
                )
                response.raise_for_status()
                workflows = response.json().get("data", [])
                return {
                    "status": "sucesso",
                    "skill": "n8n",
                    "dados": {"workflows": [{"id": w["id"], "name": w["name"], "active": w["active"]} for w in workflows]},
                    "mensagem": f"{len(workflows)} workflows encontrados",
                }
        except httpx.HTTPError as e:
            return {"status": "erro", "skill": "n8n", "mensagem": str(e)}

    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> dict:
        """Obtém as últimas execuções de workflows."""
        if not self.base_url or not self.api_key:
            return {"status": "erro", "mensagem": "N8N_BASE_URL e N8N_API_KEY não configurados"}

        try:
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id

            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/executions",
                    headers={"X-N8N-API-KEY": self.api_key},
                    params=params,
                )
                response.raise_for_status()
                return {
                    "status": "sucesso",
                    "skill": "n8n",
                    "dados": response.json(),
                    "mensagem": "Execuções obtidas",
                }
        except httpx.HTTPError as e:
            return {"status": "erro", "skill": "n8n", "mensagem": str(e)}


# ── Definições dos webhooks para cada fluxo ──

WORKFLOW_WEBHOOKS = {
    "fluxo_completo": {
        "description": "Pesquisa produto → Gera conteúdo → Upsampler imagens → Publica Shopify → Campanha marketing",
        "webhook_path": "/webhook/cerebro-fluxo-completo",
    },
    "publicar_produto": {
        "description": "Gera descrição + imagens → Publica no Shopify",
        "webhook_path": "/webhook/cerebro-publicar-produto",
    },
    "campanha_marketing": {
        "description": "Gera conteúdo + imagens → Publica nas redes sociais",
        "webhook_path": "/webhook/cerebro-campanha",
    },
    "processar_imagens": {
        "description": "Recebe imagens → Upscale via upsampler → Retorna URLs",
        "webhook_path": "/webhook/cerebro-imagens",
    },
}
