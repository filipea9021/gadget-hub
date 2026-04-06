"""
Bridge — Ponte entre o Cérebro Central (Python) e as Skills JS.
Permite executar skills JavaScript do sistema/ a partir do Python.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


class JSBridge:
    """
    Ponte para executar skills JavaScript a partir do Python.
    Usa Node.js como runtime para chamar os módulos JS existentes.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Args:
            repo_root: Raiz do repo gadget-hub (onde está sistema/)
        """
        self.repo_root = repo_root or self._detect_repo_root()

    def execute_skill(self, skill_name: str, command: str, context: Optional[dict] = None) -> dict:
        """
        Executa uma skill JS e retorna o resultado.

        Args:
            skill_name: Nome da skill (ex: 'pesquisa_produtos')
            command: Comando/instrução para a skill
            context: Contexto adicional (dados de skills anteriores)

        Returns:
            Dicionário com resultado da skill
        """
        console.print(f"[dim]🔌 Bridge JS → executando skill '{skill_name}'...[/dim]")

        # Monta o script Node.js temporário que importa e executa a skill
        js_code = self._build_execution_script(skill_name, command, context)

        try:
            result = subprocess.run(
                ["node", "--input-type=module"],
                input=js_code,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.repo_root),
            )

            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout.strip())
                    return output
                except json.JSONDecodeError:
                    return {
                        "status": "sucesso",
                        "skill": skill_name,
                        "dados": {"raw_output": result.stdout.strip()},
                        "mensagem": result.stdout.strip(),
                    }
            else:
                return {
                    "status": "erro",
                    "skill": skill_name,
                    "dados": None,
                    "mensagem": f"Erro ao executar skill JS: {result.stderr.strip()}",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "erro",
                "skill": skill_name,
                "dados": None,
                "mensagem": "Timeout: skill JS demorou mais de 30s para responder",
            }
        except FileNotFoundError:
            return {
                "status": "erro",
                "skill": skill_name,
                "dados": None,
                "mensagem": "Node.js não encontrado. Instale em: https://nodejs.org",
            }

    def check_node_available(self) -> bool:
        """Verifica se Node.js está disponível."""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _build_execution_script(
        self, skill_name: str, command: str, context: Optional[dict] = None
    ) -> str:
        """Monta o script JS que será executado via Node."""

        skill_map = {
            "pesquisa_produtos": ("./sistema/skills/skill1-produtos.js", "SkillPesquisaProdutos"),
            "criacao_site": ("./sistema/skills/skill2-site.js", "SkillCriacaoSite"),
            "marketing": ("./sistema/skills/skill3-marketing.js", "SkillMarketing"),
            "automacao": ("./sistema/skills/skill4-automacao.js", "SkillAutomacao"),
        }

        if skill_name not in skill_map:
            return f'console.log(JSON.stringify({{status: "erro", mensagem: "Skill {skill_name} não mapeada no bridge"}}));'

        module_path, class_name = skill_map[skill_name]
        context_json = json.dumps(context) if context else "null"
        command_escaped = command.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

        return f"""
import {{ {class_name} }} from '{module_path}';

const skill = new {class_name}();
const context = {context_json};

try {{
    const resultado = await skill.executar(`{command_escaped}`, context);
    console.log(JSON.stringify(resultado));
}} catch (err) {{
    console.log(JSON.stringify({{
        status: 'erro',
        skill: '{skill_name}',
        mensagem: err.message
    }}));
}}
"""

    def _detect_repo_root(self) -> Path:
        """Detecta a raiz do repo gadget-hub."""
        current = Path(__file__).resolve()
        # Sobe até encontrar a pasta sistema/
        for parent in current.parents:
            if (parent / "sistema").is_dir():
                return parent
        # Fallback: assume 2 níveis acima do cerebro-centram/core/
        return current.parent.parent.parent
