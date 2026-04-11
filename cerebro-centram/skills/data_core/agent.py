"""
DataCoreSkill — Skill que conecta o Cérebro Central ao Data Core Agent.

Funciona como ponte entre o orquestrador e o sistema de dados.
Suporta 3 módulos: memory, media, data.

Modo de funcionamento:
1. Importa os módulos do Data Core (via DATA_CORE_PATH ou caminho padrão)
2. Usa o pipeline.execute_request() para todas as operações
3. Traduz comandos em linguagem natural para requests estruturados

Exemplo de uso direto:
    skill = DataCoreSkill(settings)
    result = await skill.execute("guardar memória: reunião com fornecedor às 15h")
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


def _ensure_data_core_path() -> Path:
    """
    Garante que o caminho do Data Core está no sys.path.
    Procura em:
      1. Variável de ambiente DATA_CORE_PATH
      2. Caminho relativo padrão (../../DPLL/data-core/scripts — para dev)
      3. Pasta data-core/scripts no mesmo nível do repo
    """
    # 1. Variável de ambiente (prioridade máxima)
    env_path = os.getenv("DATA_CORE_PATH")
    if env_path:
        p = Path(env_path).resolve()
        if p.exists():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p

    # 2. Caminhos relativos comuns
    base = Path(__file__).resolve().parent  # skills/data_core/
    candidates = [
        base.parent.parent.parent / "DPLL" / "data-core" / "scripts",  # Documents/Claude/Projects/
        base.parent.parent.parent.parent / "DPLL" / "data-core" / "scripts",
        base.parent.parent / "data-core" / "scripts",  # dentro do cerebro-centram
        Path.home() / "Documents" / "Claude" / "Projects" / "DPLL" / "data-core" / "scripts",
    ]

    for candidate in candidates:
        if candidate.exists() and (candidate / "pipeline.py").exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return candidate

    raise FileNotFoundError(
        "Data Core não encontrado! Configure DATA_CORE_PATH no .env\n"
        "Exemplo: DATA_CORE_PATH=C:\\Users\\...\\DPLL\\data-core\\scripts"
    )


class DataCoreSkill:
    """
    Skill completa do Data Core — acesso a memória, media e dados.

    Métodos principais:
        execute(command, context) — Interpreta comando e executa no Data Core
        memory_log(title, ...) — Guardar uma memória/log
        memory_search(query) — Pesquisar memórias
        media_upload(file_path, ...) — Upload de media
        media_list(bucket) — Listar media
        data_store(table, data) — Guardar dados
        data_query(table, filters) — Consultar dados
    """

    def __init__(self, settings: Any = None):
        self.settings = settings
        self._pipeline = None
        self._memory = None
        self._media = None
        self._data = None
        self._initialized = False

    def _init_modules(self) -> None:
        """Inicializa os módulos do Data Core (lazy loading)."""
        if self._initialized:
            return

        data_core_path = _ensure_data_core_path()
        console.print(f"[dim]📦 Data Core carregado de: {data_core_path}[/dim]")

        # Importar módulos do Data Core
        import pipeline
        import memory_manager
        import media_manager
        import data_manager

        self._pipeline = pipeline
        self._memory = memory_manager
        self._media = media_manager
        self._data = data_manager
        self._initialized = True

    # ─────────────────────────────────────────────
    # PONTO DE ENTRADA PRINCIPAL
    # ─────────────────────────────────────────────

    async def execute(self, command: str, context: Optional[dict] = None) -> dict[str, Any]:
        """
        Executa um comando no Data Core.
        Aceita tanto comandos estruturados (JSON) como linguagem natural.

        Args:
            command: Comando em texto (ex: "guardar memória: reunião fornecedor")
            context: Contexto de etapa anterior do pipeline

        Returns:
            Resultado da operação
        """
        self._init_modules()
        command_lower = command.lower()

        try:
            # Tentar interpretar como JSON direto (para integrações)
            if command.strip().startswith("{"):
                request = json.loads(command)
                return self._pipeline.execute_request(request)

            # Roteamento por palavras-chave
            if any(kw in command_lower for kw in ["memória", "memoria", "log", "registar", "guardar nota", "lembrar"]):
                return await self._handle_memory(command, context)
            elif any(kw in command_lower for kw in ["imagem", "foto", "upload", "media", "vídeo", "video", "ficheiro"]):
                return await self._handle_media(command, context)
            elif any(kw in command_lower for kw in ["dados", "data", "guardar", "consultar", "pesquisar", "buscar"]):
                return await self._handle_data(command, context)
            elif any(kw in command_lower for kw in ["health", "status", "saúde", "saude", "teste"]):
                return self._handle_health()
            else:
                # Default: tenta como memória (log genérico)
                return await self._handle_memory(command, context)

        except Exception as e:
            return {
                "status": "error",
                "code": 500,
                "message": f"Erro na skill Data Core: {type(e).__name__}: {e}",
            }

    # ─────────────────────────────────────────────
    # MÓDULO: MEMÓRIA
    # ─────────────────────────────────────────────

    async def _handle_memory(self, command: str, context: Optional[dict] = None) -> dict:
        """Processa comandos relacionados com memória."""
        command_lower = command.lower()

        if any(kw in command_lower for kw in ["pesquisar", "buscar", "procurar", "search", "encontrar"]):
            # Pesquisa de memórias
            query = command.split(":", 1)[-1].strip() if ":" in command else command
            return self.memory_search(query)

        elif any(kw in command_lower for kw in ["listar", "últimos", "recentes", "list"]):
            return self.memory_list()

        else:
            # Guardar memória
            title = command.split(":", 1)[-1].strip() if ":" in command else command
            category = "general"
            if context and "category" in context:
                category = context["category"]
            elif any(kw in command_lower for kw in ["produto", "product"]):
                category = "products"
            elif any(kw in command_lower for kw in ["marketing", "campanha"]):
                category = "marketing"
            elif any(kw in command_lower for kw in ["sistema", "system", "erro", "error"]):
                category = "system"

            description = context.get("description", "") if context else ""
            return self.memory_log(
                title=title,
                category=category,
                description=description,
                origin_skill="cerebro_central",
            )

    def memory_log(
        self,
        title: str,
        category: str = "general",
        description: str = "",
        origin_skill: str = "cerebro_central",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Guardar uma entrada na memória."""
        self._init_modules()
        request = {
            "action": "log_action",
            "module": "memory",
            "params": {
                "title": title,
                "category": category,
                "description": description,
                "origin_skill": origin_skill,
            },
            "origin_skill": origin_skill,
        }
        if metadata:
            request["params"]["metadata"] = metadata
        return self._pipeline.execute_request(request)

    def memory_search(self, query: str, limit: int = 20) -> dict:
        """Pesquisar nas memórias."""
        self._init_modules()
        request = {
            "action": "search_logs",
            "module": "memory",
            "params": {
                "query": query,
                "limit": limit,
                "origin_skill": "cerebro_central",
            },
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    def memory_list(self, limit: int = 20, category: Optional[str] = None) -> dict:
        """Listar memórias recentes."""
        self._init_modules()
        params: dict[str, Any] = {
            "limit": limit,
            "origin_skill": "cerebro_central",
        }
        if category:
            params["category"] = category
        request = {
            "action": "list_logs",
            "module": "memory",
            "params": params,
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    # ─────────────────────────────────────────────
    # MÓDULO: MEDIA
    # ─────────────────────────────────────────────

    async def _handle_media(self, command: str, context: Optional[dict] = None) -> dict:
        """Processa comandos relacionados com media."""
        command_lower = command.lower()

        if any(kw in command_lower for kw in ["upload", "enviar", "carregar"]):
            file_path = context.get("file_path", "") if context else ""
            bucket = "images"
            if any(kw in command_lower for kw in ["vídeo", "video"]):
                bucket = "videos"
            folder = context.get("folder", "temp") if context else "temp"
            return self.media_upload(file_path, bucket, folder)

        elif any(kw in command_lower for kw in ["listar", "list", "ver"]):
            bucket = "images"
            if any(kw in command_lower for kw in ["vídeo", "video"]):
                bucket = "videos"
            elif any(kw in command_lower for kw in ["documento", "doc"]):
                bucket = "documents"
            return self.media_list(bucket)

        elif any(kw in command_lower for kw in ["apagar", "delete", "remover"]):
            file_path = context.get("file_path", "") if context else ""
            bucket = context.get("bucket", "images") if context else "images"
            return self.media_delete(file_path, bucket)

        else:
            return self.media_list("images")

    def media_upload(self, file_path: str, bucket: str = "images", folder: str = "temp") -> dict:
        """Upload de ficheiro para o Supabase Storage."""
        self._init_modules()
        action = "store_image" if bucket == "images" else "store_video"
        request = {
            "action": action,
            "module": "media",
            "params": {
                "file_path": file_path,
                "bucket": bucket,
                "folder": folder,
                "origin_skill": "cerebro_central",
            },
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    def media_list(self, bucket: str = "images", folder: Optional[str] = None) -> dict:
        """Listar ficheiros num bucket."""
        self._init_modules()
        params: dict[str, Any] = {
            "bucket": bucket,
            "origin_skill": "cerebro_central",
        }
        if folder:
            params["folder"] = folder
        request = {
            "action": "list_files",
            "module": "media",
            "params": params,
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    def media_delete(self, file_path: str, bucket: str = "images") -> dict:
        """Apagar ficheiro do storage."""
        self._init_modules()
        request = {
            "action": "delete_file",
            "module": "media",
            "params": {
                "file_path": file_path,
                "bucket": bucket,
                "origin_skill": "cerebro_central",
            },
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    # ─────────────────────────────────────────────
    # MÓDULO: DADOS
    # ─────────────────────────────────────────────

    async def _handle_data(self, command: str, context: Optional[dict] = None) -> dict:
        """Processa comandos relacionados com dados."""
        command_lower = command.lower()

        if any(kw in command_lower for kw in ["guardar", "store", "inserir", "criar"]):
            table = context.get("table", "generic_data") if context else "generic_data"
            data = context.get("data", {}) if context else {}
            return self.data_store(table, data)

        elif any(kw in command_lower for kw in ["consultar", "query", "pesquisar", "buscar", "listar"]):
            table = context.get("table", "generic_data") if context else "generic_data"
            filters = context.get("filters", {}) if context else {}
            return self.data_query(table, filters)

        else:
            # Default: consulta genérica
            table = context.get("table", "generic_data") if context else "generic_data"
            return self.data_query(table)

    def data_store(self, table: str, data: dict, origin_skill: str = "cerebro_central") -> dict:
        """Guardar dados numa tabela."""
        self._init_modules()
        request = {
            "action": "store_data",
            "module": "data",
            "params": {
                "table": table,
                "data": data,
                "origin_skill": origin_skill,
            },
            "origin_skill": origin_skill,
        }
        return self._pipeline.execute_request(request)

    def data_query(
        self, table: str, filters: Optional[dict] = None, limit: int = 20
    ) -> dict:
        """Consultar dados de uma tabela."""
        self._init_modules()
        params: dict[str, Any] = {
            "table": table,
            "limit": limit,
            "origin_skill": "cerebro_central",
        }
        if filters:
            params["filters"] = filters
        request = {
            "action": "query_data",
            "module": "data",
            "params": params,
            "origin_skill": "cerebro_central",
        }
        return self._pipeline.execute_request(request)

    # ─────────────────────────────────────────────
    # SAÚDE / DIAGNÓSTICO
    # ─────────────────────────────────────────────

    def _handle_health(self) -> dict:
        """Verifica a saúde do Data Core."""
        self._init_modules()
        try:
            import health_check
            return health_check.full_check()
        except ImportError:
            return {
                "status": "ok",
                "message": "Data Core carregado (health_check não disponível)",
            }

    def get_capabilities(self) -> dict:
        """Retorna as capacidades completas desta skill."""
        return {
            "skill": "data_core",
            "modules": {
                "memory": {
                    "actions": ["log_action", "search_logs", "list_logs"],
                    "description": "Sistema de memória persistente — guarda logs, notas, eventos",
                },
                "media": {
                    "actions": ["store_image", "store_video", "list_files", "delete_file"],
                    "description": "Gestão de media — imagens, vídeos, documentos no Supabase Storage",
                },
                "data": {
                    "actions": ["store_data", "query_data"],
                    "description": "Armazenamento e consulta de dados genéricos",
                },
            },
        }
