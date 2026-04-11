"""
permissions.py — Mapa de permissoes por skill.
Define o que cada skill pode fazer em cada modulo.
"""

# ============================================================
# MAPA DE PERMISSOES
# ============================================================
# "*" = acesso total (apenas data_core)
# Lista = acoes especificas permitidas

PERMISSIONS = {
    "marketing": {
        "memory": [
            "log_action", "log_decision", "log_learning", "log_error",
            "search_memory", "get_recent",
        ],
        "media": [
            "store_image", "store_video", "get_media", "search_media",
            "list_media", "get_media_url", "update_media",
        ],
        "media_folders": ["marketing", "temp"],
        "data": ["store_data", "get_data", "list_data", "update_data"],
        "data_namespaces": ["marketing"],
    },
    "site_creator": {
        "memory": [
            "log_action", "log_decision", "log_learning", "log_error",
            "search_memory", "get_recent",
        ],
        "media": [
            "store_image", "get_media", "search_media",
            "list_media", "get_media_url",
        ],
        "media_folders": ["products", "branding", "temp"],
        "data": ["store_data", "get_data", "list_data", "update_data"],
        "data_namespaces": ["site_creator"],
    },
    "data_core": {
        "memory": "*",
        "media": "*",
        "media_folders": "*",
        "data": "*",
        "data_namespaces": "*",
    },
}

# Acoes que modificam dados (escrita)
WRITE_ACTIONS = {
    "data": ["store_data", "update_data", "delete_data"],
    "media": ["store_image", "store_video", "update_media", "archive_media"],
}


def check_permission(origin_skill, module, action, params=None):
    """
    Verifica se a skill tem permissao para a operacao.
    Retorna None se permitido, ou dict de erro se negado.
    """
    params = params or {}

    # 1. Skill existe no mapa?
    perms = PERMISSIONS.get(origin_skill)
    if not perms:
        return {
            "status": "error",
            "code": 403,
            "message": (
                f"Skill desconhecida: '{origin_skill}'. "
                f"Skills registadas: {list(PERMISSIONS.keys())}"
            ),
            "recovery": "Registar esta skill no ficheiro permissions.py",
        }

    # 2. Acao permitida no modulo?
    allowed_actions = perms.get(module, [])
    if allowed_actions != "*" and action not in allowed_actions:
        return {
            "status": "error",
            "code": 403,
            "message": (
                f"Skill '{origin_skill}' nao tem permissao para "
                f"'{action}' no modulo '{module}'"
            ),
        }

    # 3. Pasta de media permitida? (so para acoes de escrita)
    if module == "media" and "folder" in params:
        if action in WRITE_ACTIONS.get("media", []):
            allowed_folders = perms.get("media_folders", [])
            if allowed_folders != "*" and params["folder"] not in allowed_folders:
                return {
                    "status": "error",
                    "code": 403,
                    "message": (
                        f"Skill '{origin_skill}' nao pode escrever na pasta "
                        f"'{params['folder']}'. Pastas permitidas: {allowed_folders}"
                    ),
                }

    # 4. Namespace de dados permitida? (so para acoes de escrita)
    if module == "data" and "namespace" in params:
        if action in WRITE_ACTIONS.get("data", []):
            allowed_ns = perms.get("data_namespaces", [])
            if allowed_ns != "*" and params["namespace"] not in allowed_ns:
                return {
                    "status": "error",
                    "code": 403,
                    "message": (
                        f"Skill '{origin_skill}' nao pode modificar namespace "
                        f"'{params['namespace']}'. Permitidas: {allowed_ns}"
                    ),
                }

    return None  # Permitido
