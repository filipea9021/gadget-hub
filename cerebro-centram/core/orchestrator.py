"""
CÉREBRO CENTRAL — Orquestrador Inteligente com LangGraph.

O Cérebro Central é o componente mais importante do sistema.
Ele recebe comandos de alto nível, usa um LLM para entender a intenção,
roteia para a skill correta, gerencia dependências entre skills,
e coordena fluxos multi-skill.

Diferenças do orquestrador JS anterior:
- Usa LLM para roteamento (não keywords)
- Gerencia estado com grafo de execução
- Suporta skills Python + JS via bridge
- Ciclo de feedback automático
- Memória de contexto entre execuções
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import Settings
from core.bridge import JSBridge
from core.llm import LLMClient
from core.models import Task, TaskPriority, TaskStatus
from core.registry import SkillInfo, SkillRegistry, SkillRuntime

console = Console()


# ── Prompts do Cérebro Central ──

ROUTER_SYSTEM_PROMPT = """Você é o Cérebro Central do sistema Cerebro Centram.
Sua função é analisar comandos e decidir qual skill deve executar cada tarefa.

{skills_description}

## Regras de Roteamento
1. Analise a intenção do comando
2. Identifique a skill mais adequada
3. Se o comando envolve múltiplas skills, decomponha em etapas ordenadas
4. Se nenhuma skill se aplica, responda com skill "none"

## Formato de Resposta (JSON)
Para comando simples (1 skill):
{{
  "mode": "single",
  "skill": "nome_da_skill",
  "reason": "por que esta skill foi escolhida",
  "refined_command": "comando refinado/clarificado para a skill"
}}

Para comando complexo (múltiplas skills):
{{
  "mode": "flow",
  "steps": [
    {{
      "order": 1,
      "skill": "nome_da_skill",
      "command": "comando para esta etapa",
      "depends_on": null
    }},
    {{
      "order": 2,
      "skill": "outra_skill",
      "command": "comando que usa output da etapa 1",
      "depends_on": 1
    }}
  ],
  "reason": "explicação do fluxo"
}}

Para comando impossível:
{{
  "mode": "none",
  "reason": "por que nenhuma skill pode resolver isto"
}}

Responda APENAS com JSON válido."""


CONTEXT_PROMPT = """## Contexto Atual
- Histórico de operações: {history_count}
- Última skill usada: {last_skill}
- Skills ativas: {active_skills}

## Comando do Operador
{command}"""


class ExecutionMode(str, Enum):
    SINGLE = "single"
    FLOW = "flow"
    NONE = "none"


class CerebroCentral:
    """
    O Cérebro Central — orquestrador inteligente do sistema.

    Recebe comandos de alto nível, usa LLM para decidir a melhor
    estratégia, e coordena a execução entre skills Python e JS.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = LLMClient(settings)
        self.registry = SkillRegistry()
        self.bridge = JSBridge()
        self.history: list[dict[str, Any]] = []
        self.context: dict[str, Any] = {}  # contexto compartilhado entre skills

        console.print(
            Panel(
                f"[bold blue]CÉREBRO CENTRAL[/bold blue] iniciado\n"
                f"Skills ativas: {len(self.registry.list_active())} "
                f"({sum(1 for s in self.registry.list_active() if s.runtime == SkillRuntime.PYTHON)} Python + "
                f"{sum(1 for s in self.registry.list_active() if s.runtime == SkillRuntime.JAVASCRIPT)} JS)",
                title="🧠 Cerebro Centram",
                border_style="blue",
            )
        )

    async def execute(self, command: str) -> dict[str, Any]:
        """
        Ponto de entrada principal. Recebe um comando em linguagem natural,
        decide a estratégia e executa.

        Args:
            command: Comando do operador (ex: "Criar landing page para o produto X")

        Returns:
            Resultado da execução
        """
        console.print(f"\n[bold]📥 Comando:[/bold] {command}")

        # 1. Rotear com LLM
        routing = await self._route_command(command)

        if routing["mode"] == ExecutionMode.NONE:
            console.print(f"[yellow]⚠ Nenhuma skill aplicável:[/yellow] {routing.get('reason', '')}")
            return {"status": "skip", "reason": routing.get("reason", "Comando não reconhecido")}

        # 2. Executar conforme o modo
        if routing["mode"] == ExecutionMode.SINGLE:
            result = await self._execute_single(routing)
        elif routing["mode"] == ExecutionMode.FLOW:
            result = await self._execute_flow(routing)
        else:
            result = {"status": "erro", "mensagem": f"Modo desconhecido: {routing['mode']}"}

        # 3. Registrar no histórico
        self._record_history(command, routing, result)

        return result

    async def _route_command(self, command: str) -> dict:
        """Usa o LLM para decidir qual skill deve executar o comando."""
        console.print("[dim]🔍 Analisando comando com IA...[/dim]")

        # Monta o prompt com as skills disponíveis
        skills_desc = self.registry.get_routing_prompt()
        system_prompt = ROUTER_SYSTEM_PROMPT.format(skills_description=skills_desc)

        # Contexto
        last_skill = self.history[-1]["skill"] if self.history else "nenhuma"
        active_names = ", ".join(s.name for s in self.registry.list_active())

        user_message = CONTEXT_PROMPT.format(
            history_count=len(self.history),
            last_skill=last_skill,
            active_skills=active_names,
            command=command,
        )

        try:
            response = await self.llm.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=2048,
                temperature=0.1,  # determinístico para roteamento
            )

            routing = json.loads(self._clean_json(response.content))
            mode = routing.get("mode", "none")

            if mode == "single":
                skill_name = routing.get("skill", "")
                reason = routing.get("reason", "")
                console.print(f"[green]🎯 Skill:[/green] {skill_name} — {reason}")
            elif mode == "flow":
                steps = routing.get("steps", [])
                console.print(f"[green]🔁 Fluxo com {len(steps)} etapas[/green]")
                for step in steps:
                    console.print(f"   {step['order']}. {step['skill']} → {step['command'][:60]}...")

            return routing

        except (json.JSONDecodeError, Exception) as e:
            console.print(f"[yellow]⚠ Fallback para roteamento por keywords[/yellow]")
            return self._route_by_keywords(command)

    def _route_by_keywords(self, command: str) -> dict:
        """Fallback: roteamento por keywords quando o LLM falha."""
        command_lower = command.lower()
        best_skill = None
        best_score = 0

        for skill in self.registry.list_active():
            score = sum(1 for kw in skill.keywords if kw.lower() in command_lower)
            if score > best_score:
                best_score = score
                best_skill = skill.name

        if best_skill:
            return {
                "mode": "single",
                "skill": best_skill,
                "reason": "roteamento por keywords (fallback)",
                "refined_command": command,
            }
        return {"mode": "none", "reason": "Nenhuma skill corresponde ao comando"}

    async def _execute_single(self, routing: dict) -> dict:
        """Executa um comando com uma única skill."""
        skill_name = routing["skill"]
        command = routing.get("refined_command", "")
        skill_info = self.registry.get(skill_name)

        if not skill_info:
            return {"status": "erro", "mensagem": f"Skill '{skill_name}' não encontrada"}

        console.print(f"\n[bold blue]⚡ Executando:[/bold blue] {skill_info.name} ({skill_info.runtime.value})")

        if skill_info.runtime == SkillRuntime.PYTHON:
            return await self._execute_python_skill(skill_info, command)
        elif skill_info.runtime == SkillRuntime.JAVASCRIPT:
            return self._execute_js_skill(skill_info, command)
        else:
            return {"status": "erro", "mensagem": f"Runtime não suportado: {skill_info.runtime}"}

    async def _execute_flow(self, routing: dict) -> dict:
        """Executa um fluxo multi-skill com dependências."""
        steps = routing.get("steps", [])
        results = []
        step_outputs = {}

        console.print(
            Panel(
                f"[bold]Fluxo com {len(steps)} etapas[/bold]\n"
                + "\n".join(f"  {s['order']}. {s['skill']}" for s in steps),
                title="🔁 Execução Multi-Skill",
                border_style="yellow",
            )
        )

        for step in sorted(steps, key=lambda s: s["order"]):
            order = step["order"]
            skill_name = step["skill"]
            command = step["command"]
            depends_on = step.get("depends_on")

            console.print(f"\n[bold]── Etapa {order}/{len(steps)}: {skill_name} ──[/bold]")

            # Injeta contexto da etapa anterior se houver dependência
            context = None
            if depends_on and depends_on in step_outputs:
                context = step_outputs[depends_on]

            skill_info = self.registry.get(skill_name)
            if not skill_info:
                results.append({"status": "erro", "skill": skill_name, "mensagem": "Skill não encontrada"})
                break

            if skill_info.runtime == SkillRuntime.PYTHON:
                result = await self._execute_python_skill(skill_info, command, context)
            else:
                result = self._execute_js_skill(skill_info, command, context)

            results.append(result)
            step_outputs[order] = result

            if result.get("status") == "erro":
                console.print(f"[red]✗ Etapa {order} falhou. Interrompendo fluxo.[/red]")
                break

            console.print(f"[green]✓ Etapa {order} concluída[/green]")

        succeeded = sum(1 for r in results if r.get("status") != "erro")
        return {
            "status": "sucesso" if succeeded == len(steps) else "parcial",
            "total_etapas": len(steps),
            "etapas_concluidas": succeeded,
            "resultados": results,
        }

    async def _execute_python_skill(
        self, skill_info: SkillInfo, command: str, context: Optional[dict] = None
    ) -> dict:
        """Executa uma skill Python."""
        if skill_info.name == "dev":
            from core.models import ProjectBrief
            from skills.dev.agent import DevSkill

            skill = DevSkill(self.settings)
            # Para a skill dev, o comando é tratado como briefing
            brief = ProjectBrief(
                name=command.split()[0:3] if command else ["projeto"],
                description=command,
            )
            # Use the LLM to extract a proper brief from the command
            brief = await self._extract_brief(command)
            project = await skill.generate_project(brief)
            project_dir = skill.save_project(project)
            return {
                "status": "sucesso",
                "skill": "dev",
                "dados": {
                    "project_dir": str(project_dir),
                    "files_count": len(project.files),
                    "files": [f.path for f in project.files],
                },
                "mensagem": f"Projeto gerado com {len(project.files)} arquivos em {project_dir}",
            }

        elif skill_info.name == "shopify":
            return {
                "status": "sucesso",
                "skill": "shopify",
                "dados": {"note": "Integração Shopify disponível via automation/platforms/shopify.py"},
                "mensagem": "Skill Shopify pronta — configure SHOPIFY_API_KEY no .env para ativar",
            }

        elif skill_info.name == "content_generator":
            return {
                "status": "sucesso",
                "skill": "content_generator",
                "dados": {"note": "Gerador de conteúdo disponível via automation/modules/generator.py"},
                "mensagem": "Skill de geração de conteúdo pronta",
            }

        elif skill_info.name == "imagens":
            from skills.imagens.agent import ImagensSkill

            skill = ImagensSkill(self.settings)
            # Determina operação a partir do comando
            command_lower = command.lower()

            if "banner" in command_lower:
                text = context.get("headline", command) if context else command
                product_img = context.get("imagem_produto") if context else None
                result = await skill.create_banner(text, product_img)
            elif "fundo" in command_lower or "background" in command_lower:
                image_url = context.get("image_url", "") if context else ""
                result = await skill.remove_background(image_url)
            elif "gerar" in command_lower or "criar imagem" in command_lower:
                product_name = context.get("produto_nome", command) if context else command
                result = await skill.generate_product_image(product_name)
            elif "lote" in command_lower or "batch" in command_lower:
                urls = context.get("image_urls", []) if context else []
                operation = "upscale" if "upscale" in command_lower else "remove-bg"
                result = await skill.batch_process(urls, operation)
            else:
                # Default: upscale
                image_url = context.get("image_url", "") if context else ""
                scale = 4 if "4x" in command_lower else 2
                result = await skill.upscale(image_url, scale)

            return result

        elif skill_info.name == "n8n":
            from skills.n8n.agent import N8NSkill, WORKFLOW_WEBHOOKS

            skill = N8NSkill(self.settings)
            command_lower = command.lower()

            if "listar" in command_lower or "list" in command_lower:
                result = await skill.list_workflows()
            elif "execuções" in command_lower or "execucoes" in command_lower or "historico" in command_lower:
                result = await skill.get_executions()
            elif "fluxo completo" in command_lower or "fluxo_completo" in command_lower:
                # Dispara o fluxo completo via webhook
                webhook_info = WORKFLOW_WEBHOOKS["fluxo_completo"]
                webhook_url = f"{skill.base_url}{webhook_info['webhook_path']}"
                payload = context or {"comando": command}
                result = await skill.trigger_webhook(webhook_url, payload)
            elif "publicar" in command_lower:
                webhook_info = WORKFLOW_WEBHOOKS["publicar_produto"]
                webhook_url = f"{skill.base_url}{webhook_info['webhook_path']}"
                payload = context or {"comando": command}
                result = await skill.trigger_webhook(webhook_url, payload)
            elif "campanha" in command_lower or "marketing" in command_lower:
                webhook_info = WORKFLOW_WEBHOOKS["campanha_marketing"]
                webhook_url = f"{skill.base_url}{webhook_info['webhook_path']}"
                payload = context or {"comando": command}
                result = await skill.trigger_webhook(webhook_url, payload)
            elif "imagens" in command_lower or "processar" in command_lower:
                webhook_info = WORKFLOW_WEBHOOKS["processar_imagens"]
                webhook_url = f"{skill.base_url}{webhook_info['webhook_path']}"
                payload = context or {"comando": command}
                result = await skill.trigger_webhook(webhook_url, payload)
            else:
                # Tenta disparar por workflow_id
                result = await skill.trigger_workflow(command.strip(), context)

            return result

        return {"status": "erro", "skill": skill_info.name, "mensagem": "Skill Python sem handler"}

    def _execute_js_skill(
        self, skill_info: SkillInfo, command: str, context: Optional[dict] = None
    ) -> dict:
        """Executa uma skill JavaScript via bridge."""
        return self.bridge.execute_skill(skill_info.name, command, context)

    async def _extract_brief(self, command: str) -> "ProjectBrief":
        """Usa o LLM para extrair um ProjectBrief estruturado de um comando."""
        from core.models import ProjectBrief

        prompt = f"""Extraia um briefing de projeto do seguinte comando:
"{command}"

Responda em JSON:
{{
  "name": "nome-do-projeto-em-kebab-case",
  "description": "descrição clara do projeto",
  "project_type": "landing_page|api|fullstack|component",
  "features": ["feature 1", "feature 2"],
  "style_preferences": "preferências visuais"
}}"""

        try:
            response = await self.llm.generate(
                system_prompt="Extraia briefings de projeto de comandos. Responda APENAS em JSON.",
                user_message=prompt,
                max_tokens=1024,
                temperature=0.2,
            )
            data = json.loads(self._clean_json(response.content))
            return ProjectBrief(
                name=data.get("name", "novo-projeto"),
                description=data.get("description", command),
                project_type=data.get("project_type", "landing_page"),
                features=data.get("features", []),
                style_preferences=data.get("style_preferences"),
            )
        except Exception:
            return ProjectBrief(name="novo-projeto", description=command)

    def get_status(self) -> dict:
        """Retorna o status completo do sistema."""
        skills = {}
        for skill in self.registry.list_all():
            skills[skill.name] = {
                "descricao": skill.description,
                "runtime": skill.runtime.value,
                "status": skill.status.value,
                "execucoes": sum(1 for h in self.history if h["skill"] == skill.name),
            }
        return {
            "skills": skills,
            "total_operacoes": len(self.history),
            "provider_llm": self.settings.llm_provider.value,
        }

    def show_status(self) -> None:
        """Mostra status formatado no console."""
        status = self.get_status()

        table = Table(title="🧠 Cérebro Central — Status", border_style="blue")
        table.add_column("Skill", style="bold")
        table.add_column("Runtime")
        table.add_column("Status")
        table.add_column("Execuções", justify="right")

        for name, info in status["skills"].items():
            runtime_color = "cyan" if info["runtime"] == "python" else "yellow"
            status_icon = "🟢" if info["status"] == "active" else "🔴"
            table.add_row(
                name,
                f"[{runtime_color}]{info['runtime']}[/{runtime_color}]",
                status_icon,
                str(info["execucoes"]),
            )

        console.print(table)
        console.print(f"\nTotal de operações: {status['total_operacoes']}")
        console.print(f"Provider LLM: {status['provider_llm']}")

    def _record_history(self, command: str, routing: dict, result: dict) -> None:
        """Registra operação no histórico."""
        self.history.append({
            "command": command,
            "skill": routing.get("skill", routing.get("steps", [{}])[0].get("skill", "unknown")),
            "mode": routing.get("mode", "unknown"),
            "status": result.get("status", "unknown"),
            "timestamp": datetime.now().isoformat(),
        })

    @staticmethod
    def _clean_json(text: str) -> str:
        """Remove markdown wrappers de JSON."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
