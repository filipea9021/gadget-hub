"""
validators.py — Validacao de parametros, ficheiros e acoes.
Toda requisicao passa por aqui ANTES de qualquer operacao.
"""

import mimetypes
import os
from pathlib import Path

from config import (
    ALLOWED_FOLDERS,
    MAX_DOC_SIZE_BYTES,
    MAX_IMAGE_SIZE_BYTES,
    MAX_VIDEO_SIZE_BYTES,
)

# ============================================================
# MAGIC BYTES — Verificacao de tipo real do ficheiro
# ============================================================

MAGIC_BYTES = {
    "image/png": b"\x89PNG",
    "image/jpeg": b"\xff\xd8\xff",
    "image/gif": b"GIF8",
    "image/webp": b"RIFF",
    "image/svg+xml": b"<svg",
    "image/bmp": b"BM",
    "video/mp4": b"\x00\x00\x00",
    "application/pdf": b"%PDF",
}

# ============================================================
# SCHEMAS DE VALIDACAO POR ACAO
# ============================================================

VALIDATION_SCHEMAS = {
    # --- Memory Manager ---
    "log_action": {
        "required": ["title", "origin_skill"],
        "optional": ["category", "description", "tags", "metadata", "session_id"],
        "types": {
            "title": str,
            "origin_skill": str,
            "category": str,
            "description": str,
            "tags": list,
            "metadata": dict,
            "session_id": str,
        },
    },
    "log_decision": {
        "required": ["title", "description", "origin_skill"],
        "optional": ["category", "tags", "metadata", "session_id"],
        "types": {
            "title": str,
            "description": str,
            "origin_skill": str,
            "category": str,
            "tags": list,
            "metadata": dict,
        },
    },
    "log_learning": {
        "required": ["title", "description", "origin_skill"],
        "optional": ["category", "tags", "metadata"],
        "types": {
            "title": str,
            "description": str,
            "origin_skill": str,
            "category": str,
            "tags": list,
            "metadata": dict,
        },
    },
    "log_error": {
        "required": ["title", "severity", "origin_skill"],
        "optional": ["category", "description", "tags", "metadata"],
        "types": {
            "title": str,
            "severity": str,
            "origin_skill": str,
            "description": str,
        },
        "allowed_values": {
            "severity": ["debug", "info", "warning", "error", "critical"],
        },
    },
    "log_config": {
        "required": ["title", "origin_skill"],
        "optional": ["description", "metadata"],
        "types": {"title": str, "origin_skill": str, "description": str, "metadata": dict},
    },
    "search_memory": {
        "required": [],
        "optional": ["query", "type", "category", "origin_skill", "tags", "limit", "offset"],
        "types": {
            "query": str,
            "type": str,
            "category": str,
            "origin_skill": str,
            "tags": list,
            "limit": int,
            "offset": int,
        },
        "allowed_values": {
            "type": ["action_log", "decision_log", "learning", "error_log", "config_snapshot"],
        },
    },
    "get_recent": {
        "required": [],
        "optional": ["limit", "type", "origin_skill"],
        "types": {"limit": int, "type": str, "origin_skill": str},
    },
    # --- Media Manager ---
    "store_image": {
        "required": ["file_path", "folder", "origin_skill"],
        "optional": ["tags", "purpose", "campaign_id", "description"],
        "types": {
            "file_path": str,
            "folder": str,
            "origin_skill": str,
            "tags": list,
            "purpose": str,
            "campaign_id": str,
            "description": str,
        },
        "allowed_folders": ALLOWED_FOLDERS.get("images", []),
    },
    "store_video": {
        "required": ["file_path", "folder", "origin_skill"],
        "optional": ["tags", "purpose", "campaign_id", "description"],
        "types": {
            "file_path": str,
            "folder": str,
            "origin_skill": str,
            "tags": list,
            "purpose": str,
            "campaign_id": str,
            "description": str,
        },
        "allowed_folders": ALLOWED_FOLDERS.get("videos", []),
    },
    "get_media": {
        "required": ["id"],
        "optional": [],
        "types": {"id": str},
    },
    "search_media": {
        "required": [],
        "optional": ["tags", "folder", "file_type", "origin_skill", "purpose",
                      "campaign_id", "status", "limit", "offset"],
        "types": {
            "tags": list,
            "folder": str,
            "file_type": str,
            "origin_skill": str,
            "limit": int,
            "offset": int,
        },
        "allowed_values": {
            "file_type": ["image", "video", "document", "other"],
            "status": ["active", "archived", "temp"],
        },
    },
    "list_media": {
        "required": ["bucket", "folder"],
        "optional": ["limit", "offset"],
        "types": {"bucket": str, "folder": str, "limit": int, "offset": int},
    },
    "update_media": {
        "required": ["id"],
        "optional": ["tags", "purpose", "description", "campaign_id", "status", "category"],
        "types": {
            "id": str,
            "tags": list,
            "purpose": str,
            "description": str,
            "campaign_id": str,
            "status": str,
            "category": str,
        },
        "allowed_values": {
            "status": ["active", "archived", "temp"],
        },
    },
    "archive_media": {
        "required": ["id"],
        "optional": [],
        "types": {"id": str},
    },
    "get_media_url": {
        "required": ["id"],
        "optional": [],
        "types": {"id": str},
    },
    # --- Data Manager ---
    "store_data": {
        "required": ["namespace", "key", "value"],
        "optional": ["data_type", "description"],
        "types": {
            "namespace": str,
            "key": str,
            "data_type": str,
            "description": str,
        },
        # value pode ser qualquer tipo (sera guardado como JSONB)
    },
    "get_data": {
        "required": ["namespace", "key"],
        "optional": [],
        "types": {"namespace": str, "key": str},
    },
    "update_data": {
        "required": ["namespace", "key", "value"],
        "optional": ["description"],
        "types": {"namespace": str, "key": str, "description": str},
    },
    "delete_data": {
        "required": ["namespace", "key"],
        "optional": [],
        "types": {"namespace": str, "key": str},
    },
    "list_data": {
        "required": ["namespace"],
        "optional": ["data_type", "limit", "offset"],
        "types": {"namespace": str, "data_type": str, "limit": int, "offset": int},
    },
}

# ============================================================
# ACOES VALIDAS POR MODULO
# ============================================================

VALID_ACTIONS = {
    "memory": [
        "log_action", "log_decision", "log_learning", "log_error",
        "log_config", "search_memory", "get_recent",
    ],
    "media": [
        "store_image", "store_video", "get_media", "search_media",
        "list_media", "update_media", "archive_media", "get_media_url",
    ],
    "data": [
        "store_data", "get_data", "update_data", "delete_data", "list_data",
    ],
}


# ============================================================
# FUNCOES DE VALIDACAO
# ============================================================

def validate_action(module, action):
    """Verifica se a acao existe no modulo indicado."""
    if module not in VALID_ACTIONS:
        return {
            "status": "error",
            "code": 400,
            "message": f"Modulo invalido: '{module}'. Disponiveis: {list(VALID_ACTIONS.keys())}",
        }
    if action not in VALID_ACTIONS[module]:
        return {
            "status": "error",
            "code": 400,
            "message": (
                f"Acao invalida: '{action}' no modulo '{module}'. "
                f"Acoes disponiveis: {VALID_ACTIONS[module]}"
            ),
        }
    return None


def validate_params(action, params):
    """Valida parametros contra o schema da acao."""
    schema = VALIDATION_SCHEMAS.get(action)
    if not schema:
        return {
            "status": "error",
            "code": 400,
            "message": f"Schema de validacao nao encontrado para acao: '{action}'",
        }

    # 1. Campos obrigatorios
    for field in schema["required"]:
        if field not in params or params[field] is None:
            return {
                "status": "error",
                "code": 400,
                "message": f"Campo obrigatorio em falta: '{field}'",
                "recovery": (
                    f"Adicionar '{field}' aos parametros. "
                    f"Tipo esperado: {schema['types'].get(field, 'any')}"
                ),
            }

    # 2. Tipos
    for field, expected_type in schema.get("types", {}).items():
        if field in params and params[field] is not None:
            if not isinstance(params[field], expected_type):
                return {
                    "status": "error",
                    "code": 400,
                    "message": (
                        f"Tipo errado para '{field}': "
                        f"esperado {expected_type.__name__}, "
                        f"recebido {type(params[field]).__name__}"
                    ),
                }

    # 3. Valores permitidos
    for field, allowed in schema.get("allowed_values", {}).items():
        if field in params and params[field] is not None:
            if params[field] not in allowed:
                return {
                    "status": "error",
                    "code": 400,
                    "message": (
                        f"Valor invalido para '{field}': '{params[field]}'. "
                        f"Permitidos: {allowed}"
                    ),
                }

    # 4. Pastas permitidas
    if "allowed_folders" in schema and "folder" in params:
        if params["folder"] not in schema["allowed_folders"]:
            return {
                "status": "error",
                "code": 400,
                "message": (
                    f"Pasta invalida: '{params['folder']}'. "
                    f"Permitidas: {schema['allowed_folders']}"
                ),
            }

    return None


def validate_file(file_path, expected_type="image"):
    """Valida ficheiro antes de qualquer processamento."""

    # 1. Existe?
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "code": 404,
            "message": f"Ficheiro nao encontrado: {file_path}",
            "recovery": "Verificar o caminho do ficheiro",
        }

    # 2. Tamanho > 0?
    size = os.path.getsize(file_path)
    if size == 0:
        return {
            "status": "error",
            "code": 400,
            "message": "Ficheiro vazio (0 bytes) — provavelmente corrompido",
        }

    # 3. Dentro do limite?
    limits = {
        "image": MAX_IMAGE_SIZE_BYTES,
        "video": MAX_VIDEO_SIZE_BYTES,
        "document": MAX_DOC_SIZE_BYTES,
    }
    max_size = limits.get(expected_type, MAX_IMAGE_SIZE_BYTES)
    if size > max_size:
        return {
            "status": "error",
            "code": 413,
            "message": (
                f"Ficheiro muito grande: {size / 1024 / 1024:.1f}MB "
                f"(limite: {max_size / 1024 / 1024:.0f}MB)"
            ),
            "recovery": "Comprimir o ficheiro ou usar formato mais eficiente",
        }

    # 4. Tipo correto? (magic bytes)
    try:
        with open(file_path, "rb") as f:
            header = f.read(8)

        mime = mimetypes.guess_type(file_path)[0]
        if mime and mime in MAGIC_BYTES:
            expected_magic = MAGIC_BYTES[mime]
            if not header.startswith(expected_magic):
                return {
                    "status": "error",
                    "code": 400,
                    "message": (
                        f"Ficheiro corrompido ou extensao errada. "
                        f"Extensao indica '{mime}' mas conteudo nao corresponde"
                    ),
                    "recovery": "Verificar se o ficheiro nao esta corrompido",
                }
    except Exception:
        pass  # Nao bloquear upload por falha na verificacao de magic bytes

    return None
