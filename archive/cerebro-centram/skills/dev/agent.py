"""
Skill Dev — Agente de Desenvolvimento.
Gera projetos web completos a partir de briefings.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.settings import Settings
from core.llm import LLMClient, LLMResponse
from core.models import GeneratedFile, ProjectBrief, ProjectOutput, Task, TaskStatus
from skills.dev.prompts import BRIEFING_TEMPLATE, ITERATION_PROMPT, REVIEW_PROMPT, SYSTEM_PROMPT

console = Console()


class DevSkill:
    """
    Skill de Desenvolvimento — o primeiro agente do Cerebro Centram.

    Capacidades:
    - Gerar projetos web completos (landing pages, sites, APIs)
    - Revisar código gerado
    - Iterar com base em feedback do operador
    - Salvar projetos em disco prontos para rodar
    """

    name = "dev"
    description = "Agente de desenvolvimento web — gera código de produção a partir de briefings"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = LLMClient(settings)
        self.output_dir = settings.output_dir

    async def generate_project(self, brief: ProjectBrief) -> ProjectOutput:
        """
        Gera um projeto completo a partir de um briefing.

        Args:
            brief: Briefing com nome, descrição, features, etc.

        Returns:
            ProjectOutput com todos os arquivos gerados
        """
        console.print(
            Panel(
                f"[bold blue]Skill Dev[/bold blue] gerando projeto: [bold]{brief.name}[/bold]\n"
                f"Tipo: {brief.project_type} | Stack: {', '.join(brief.tech_stack)}",
                title="🚀 Cerebro Centram",
                border_style="blue",
            )
        )

        # Monta o prompt com o briefing
        user_message = BRIEFING_TEMPLATE.format(
            name=brief.name,
            project_type=brief.project_type,
            description=brief.description,
            tech_stack=", ".join(brief.tech_stack),
            features="\n".join(f"- {f}" for f in brief.features) if brief.features else "A definir com base na descrição",
            style_preferences=brief.style_preferences or "Moderno, limpo, profissional",
            target_audience=brief.target_audience or "Não especificado",
            reference_urls=", ".join(brief.reference_urls) if brief.reference_urls else "Nenhuma",
        )

        # Chama o LLM
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Gerando código...", total=None)
            response = await self.llm.generate(
                system_prompt=SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=8192,
                temperature=0.3,
            )
            progress.update(task, description="Código gerado!")

        # Parse da resposta
        output = self._parse_response(response, brief)

        console.print(
            f"\n[green]✓[/green] Projeto gerado com {len(output.files)} arquivos"
            f" ({response.total_tokens} tokens usados)"
        )

        return output

    async def review_code(self, project: ProjectOutput) -> dict:
        """
        Revisa o código gerado e retorna análise de qualidade.
        """
        console.print("\n[yellow]🔍 Revisando código...[/yellow]")

        code_summary = "\n\n".join(
            f"--- {f.path} ---\n{f.content}" for f in project.files
        )

        response = await self.llm.generate(
            system_prompt=REVIEW_PROMPT,
            user_message=code_summary,
            max_tokens=4096,
            temperature=0.2,
        )

        try:
            review = json.loads(self._clean_json(response.content))
        except json.JSONDecodeError:
            review = {"score": 0, "issues": [], "summary": "Erro ao parsear revisão", "raw": response.content}

        score = review.get("score", 0)
        color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        console.print(f"[{color}]Score de qualidade: {score}/100[/{color}]")

        return review

    async def iterate(self, project: ProjectOutput, feedback: str) -> ProjectOutput:
        """
        Aplica feedback do operador e gera nova versão.
        """
        console.print(
            Panel(
                f"[bold yellow]Iterando[/bold yellow] com feedback:\n{feedback}",
                title="🔄 Skill Dev",
                border_style="yellow",
            )
        )

        current_code = "\n\n".join(
            f"--- {f.path} ---\n{f.content}" for f in project.files
        )

        user_message = ITERATION_PROMPT.format(
            feedback=feedback,
            current_code=current_code,
        )

        response = await self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=8192,
            temperature=0.3,
        )

        output = self._parse_response(response, project.brief)
        console.print(f"[green]✓[/green] Projeto atualizado com {len(output.files)} arquivos")

        return output

    def save_project(self, project: ProjectOutput) -> Path:
        """
        Salva todos os arquivos do projeto em disco.

        Returns:
            Path do diretório do projeto
        """
        project_dir = self.output_dir / project.brief.name
        project_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        for file in project.files:
            file_path = project_dir / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file.content, encoding="utf-8")
            saved_count += 1

        # Salva setup instructions
        readme_path = project_dir / "SETUP.md"
        readme_content = f"""# {project.brief.name}

{project.brief.description}

## Setup

{project.setup_instructions}

## Estrutura

```
{project.structure}
```

---
Gerado automaticamente pelo Cerebro Centram — Skill Dev
"""
        readme_path.write_text(readme_content, encoding="utf-8")

        console.print(
            Panel(
                f"[green]Projeto salvo em:[/green] {project_dir}\n"
                f"Arquivos: {saved_count + 1} (incluindo SETUP.md)",
                title="💾 Salvo",
                border_style="green",
            )
        )

        return project_dir

    def _parse_response(self, response: LLMResponse, brief: ProjectBrief) -> ProjectOutput:
        """Parseia a resposta JSON do LLM em um ProjectOutput."""
        try:
            data = json.loads(self._clean_json(response.content))
        except json.JSONDecodeError:
            console.print("[red]⚠ Erro ao parsear resposta do LLM. Tentando extrair JSON...[/red]")
            # Tenta extrair JSON de dentro de markdown code blocks
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            try:
                data = json.loads(content.strip())
            except json.JSONDecodeError:
                return ProjectOutput(
                    brief=brief,
                    files=[GeneratedFile(
                        path="raw_response.txt",
                        content=response.content,
                        language="text",
                        description="Resposta bruta do LLM (falha no parse)",
                    )],
                    setup_instructions="Erro: resposta do LLM não era JSON válido.",
                )

        files = [
            GeneratedFile(
                path=f.get("path", f"file_{i}.txt"),
                content=f.get("content", ""),
                language=f.get("language", "text"),
                description=f.get("description", ""),
            )
            for i, f in enumerate(data.get("files", []))
        ]

        return ProjectOutput(
            brief=brief,
            files=files,
            structure=data.get("structure", ""),
            setup_instructions=data.get("setup_instructions", "npm install && npm run dev"),
        )

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
