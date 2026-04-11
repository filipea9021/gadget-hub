"""
CLI do Cerebro Centram.
Interface de linha de comando para interagir com as skills.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import LLMProvider, get_settings
from core.models import ProjectBrief
from core.orchestrator import CerebroCentral
from skills.dev.agent import DevSkill

app = typer.Typer(
    name="cerebro",
    help="🧠 Cerebro Centram — Sistema Autônomo de Skills com IA",
    no_args_is_help=True,
)
console = Console()


def show_banner():
    console.print(
        Panel(
            "[bold blue]CEREBRO CENTRAM[/bold blue]\n"
            "[dim]Sistema Autônomo de Skills com Inteligência Artificial[/dim]",
            border_style="blue",
            padding=(1, 4),
        )
    )


@app.command()
def generate(
    name: str = typer.Option(..., "--name", "-n", help="Nome do projeto"),
    description: str = typer.Option(..., "--desc", "-d", help="Descrição do projeto"),
    project_type: str = typer.Option("landing_page", "--type", "-t", help="Tipo: landing_page, api, fullstack, component"),
    features: list[str] = typer.Option([], "--feature", "-f", help="Features (pode repetir)"),
    style: str = typer.Option("Moderno, limpo, profissional", "--style", "-s", help="Preferências de estilo"),
    audience: str = typer.Option("", "--audience", "-a", help="Público-alvo"),
    output: str = typer.Option("./output", "--output", "-o", help="Diretório de saída"),
    review: bool = typer.Option(True, "--review/--no-review", help="Revisar código após geração"),
):
    """
    🚀 Gera um projeto web completo a partir de um briefing.

    Exemplo:
        cerebro generate -n "minha-landing" -d "Landing page para app de tarefas" -f "Hero section" -f "Pricing" -f "FAQ"
    """
    show_banner()

    settings = get_settings()
    settings.output_dir = Path(output)

    try:
        settings.validate_provider()
    except ValueError as e:
        console.print(f"[red]✗ Erro de configuração:[/red] {e}")
        raise typer.Exit(1)

    brief = ProjectBrief(
        name=name,
        description=description,
        project_type=project_type,
        features=features if features else [],
        style_preferences=style,
        target_audience=audience if audience else None,
    )

    # Mostra resumo do briefing
    table = Table(title="📋 Briefing do Projeto", border_style="blue")
    table.add_column("Campo", style="bold")
    table.add_column("Valor")
    table.add_row("Nome", brief.name)
    table.add_row("Tipo", brief.project_type)
    table.add_row("Descrição", brief.description)
    table.add_row("Features", ", ".join(brief.features) if brief.features else "Auto")
    table.add_row("Estilo", brief.style_preferences or "Padrão")
    table.add_row("Provider", settings.llm_provider.value)
    console.print(table)
    console.print()

    # Executa
    skill = DevSkill(settings)

    async def run():
        project = await skill.generate_project(brief)

        if review:
            review_result = await skill.review_code(project)
            score = review_result.get("score", 0)
            if score < 60:
                console.print("[yellow]⚠ Score baixo. Considere iterar com feedback.[/yellow]")

        project_dir = skill.save_project(project)
        console.print(f"\n[bold green]✓ Projeto pronto em:[/bold green] {project_dir}")

        return project

    asyncio.run(run())


@app.command()
def interactive():
    """
    💬 Modo interativo — responda perguntas para gerar seu projeto.
    """
    show_banner()
    console.print("[dim]Modo interativo — vou te guiar pelo briefing[/dim]\n")

    name = Prompt.ask("[bold]Nome do projeto[/bold]", default="meu-projeto")
    description = Prompt.ask("[bold]Descreva o projeto em 1-2 frases[/bold]")

    type_options = {
        "1": "landing_page",
        "2": "api",
        "3": "fullstack",
        "4": "component",
    }
    console.print("\n[bold]Tipo de projeto:[/bold]")
    console.print("  1. Landing Page")
    console.print("  2. API / Backend")
    console.print("  3. Fullstack (front + back)")
    console.print("  4. Componente isolado")
    type_choice = Prompt.ask("Escolha", choices=["1", "2", "3", "4"], default="1")
    project_type = type_options[type_choice]

    features_input = Prompt.ask(
        "[bold]Features[/bold] (separadas por vírgula, ou Enter para automático)",
        default="",
    )
    features = [f.strip() for f in features_input.split(",") if f.strip()] if features_input else []

    style = Prompt.ask(
        "[bold]Estilo visual[/bold]",
        default="Moderno, limpo, profissional",
    )

    audience = Prompt.ask("[bold]Público-alvo[/bold]", default="")

    output_dir = Prompt.ask("[bold]Diretório de saída[/bold]", default="./output")

    # Confirma
    console.print()
    brief = ProjectBrief(
        name=name,
        description=description,
        project_type=project_type,
        features=features,
        style_preferences=style,
        target_audience=audience if audience else None,
    )

    table = Table(title="📋 Confirmação", border_style="blue")
    table.add_column("Campo", style="bold")
    table.add_column("Valor")
    table.add_row("Nome", brief.name)
    table.add_row("Tipo", brief.project_type)
    table.add_row("Descrição", brief.description)
    table.add_row("Features", ", ".join(brief.features) if brief.features else "Automático")
    table.add_row("Estilo", brief.style_preferences or "Padrão")
    console.print(table)

    if not Prompt.ask("\n[bold]Confirma?[/bold]", choices=["s", "n"], default="s") == "s":
        console.print("[yellow]Cancelado.[/yellow]")
        raise typer.Exit(0)

    settings = get_settings()
    settings.output_dir = Path(output_dir)

    try:
        settings.validate_provider()
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    skill = DevSkill(settings)

    async def run():
        project = await skill.generate_project(brief)
        review_result = await skill.review_code(project)
        project_dir = skill.save_project(project)

        # Loop de iteração
        while True:
            feedback = Prompt.ask(
                "\n[bold]Feedback[/bold] (ou 'ok' para finalizar, 'sair' para cancelar)",
                default="ok",
            )
            if feedback.lower() in ("ok", "sair", "exit", "quit"):
                break

            project = await skill.iterate(project, feedback)
            await skill.review_code(project)
            project_dir = skill.save_project(project)

        console.print(f"\n[bold green]✓ Projeto finalizado em:[/bold green] {project_dir}")

    asyncio.run(run())


@app.command()
def brain(
    output: str = typer.Option("./output", "--output", "-o", help="Diretório de saída"),
):
    """
    🧠 Modo Cérebro Central — envia comandos em linguagem natural e o sistema decide a melhor skill.

    Exemplo:
        cerebro brain
        > Criar landing page para loja de gadgets com hero, pricing e FAQ
        > Pesquisar melhores produtos de fones bluetooth
        > Gerar campanha de marketing para Black Friday
    """
    show_banner()

    settings = get_settings()
    settings.output_dir = Path(output)

    try:
        settings.validate_provider()
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    cerebro = CerebroCentral(settings)

    async def run():
        console.print(
            "\n[dim]Digite comandos em linguagem natural. "
            "O Cérebro Central decide a melhor skill.[/dim]"
        )
        console.print("[dim]Comandos: 'status' para ver skills, 'sair' para encerrar[/dim]\n")

        while True:
            command = Prompt.ask("[bold blue]🧠 Cérebro[/bold blue]")

            if command.lower() in ("sair", "exit", "quit", "q"):
                console.print("[dim]Até a próxima![/dim]")
                break

            if command.lower() == "status":
                cerebro.show_status()
                continue

            if not command.strip():
                continue

            try:
                result = await cerebro.execute(command)
                if result.get("status") == "sucesso":
                    console.print(f"\n[green]✓ {result.get('mensagem', 'Concluído')}[/green]")
                elif result.get("status") == "parcial":
                    completed = result.get("etapas_concluidas", 0)
                    total = result.get("total_etapas", 0)
                    console.print(f"\n[yellow]⚠ Fluxo parcial: {completed}/{total} etapas concluídas[/yellow]")
                elif result.get("status") == "skip":
                    pass  # já mostrou mensagem no execute
                else:
                    console.print(f"\n[red]✗ {result.get('mensagem', 'Erro desconhecido')}[/red]")
            except Exception as e:
                console.print(f"\n[red]✗ Erro: {e}[/red]")

    asyncio.run(run())


@app.command()
def status():
    """
    📊 Mostra o status atual do Cerebro Centram com todas as skills.
    """
    show_banner()

    settings = get_settings()
    cerebro = CerebroCentral(settings)
    cerebro.show_status()


if __name__ == "__main__":
    app()
