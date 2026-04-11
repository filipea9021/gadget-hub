"""
memory_manager.py — Modulo de memoria do Data Core.
Armazena e recupera logs de acoes, decisoes, aprendizados e erros.
"""

from config import DEFAULT_RESULTS_PER_QUERY, MAX_RESULTS_PER_QUERY, get_supabase
from retry import rate_limiter, retry_operation
from utils import format_response, sanitize_metadata, sanitize_tags, utc_isoformat

# Mapeamento acao → tipo de memoria
ACTION_TO_TYPE = {
    "log_action": "action_log",
    "log_decision": "decision_log",
    "log_learning": "learning",
    "log_error": "error_log",
    "log_config": "config_snapshot",
}

TABLE = "memory_logs"


# ============================================================
# OPERACOES DE ESCRITA
# ============================================================

def log_entry(action, params):
    """Insere um registro de memoria. Usado por log_action, log_decision, etc."""
    memory_type = ACTION_TO_TYPE.get(action)
    if not memory_type:
        return format_response("error", 400, f"Tipo de log desconhecido para acao: {action}")

    # Construir registro
    record = {
        "type": memory_type,
        "title": params["title"],
        "origin_skill": params.get("origin_skill", "unknown"),
        "category": params.get("category"),
        "description": params.get("description"),
        "severity": params.get("severity", "info"),
        "tags": sanitize_tags(params.get("tags", [])),
        "metadata": sanitize_metadata(params.get("metadata", {})),
        "session_id": params.get("session_id"),
    }

    # Remover campos None para nao enviar ao Supabase
    record = {k: v for k, v in record.items() if v is not None}

    def _insert():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).insert(record).execute()
        return result.data[0] if result.data else {}

    result = retry_operation(_insert)

    # retry_operation retorna dict de erro se falhou
    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 201,
        f"Registro de memoria criado ({memory_type})",
        data={"id": result.get("id"), "type": memory_type},
    )


# ============================================================
# OPERACOES DE LEITURA
# ============================================================

def search_memory(params):
    """Busca registros de memoria com filtros."""
    limit = min(params.get("limit", DEFAULT_RESULTS_PER_QUERY), MAX_RESULTS_PER_QUERY)
    offset = max(params.get("offset", 0), 0)

    def _search():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        query = client.table(TABLE).select("*")

        # Aplicar filtros
        if params.get("type"):
            query = query.eq("type", params["type"])
        if params.get("category"):
            query = query.eq("category", params["category"])
        if params.get("origin_skill"):
            query = query.eq("origin_skill", params["origin_skill"])
        if params.get("tags"):
            # Buscar registros que contenham QUALQUER uma das tags
            query = query.overlaps("tags", params["tags"])
        if params.get("query"):
            # Busca textual no titulo e descricao
            search_term = f"%{params['query']}%"
            query = query.or_(f"title.ilike.{search_term},description.ilike.{search_term}")

        # Ordenar e paginar
        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return result.data

    result = retry_operation(_search)

    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 200,
        f"{len(result)} registros encontrados",
        data={"records": result, "count": len(result), "limit": limit, "offset": offset},
    )


def get_recent(params):
    """Retorna os N registros mais recentes."""
    limit = min(params.get("limit", 10), MAX_RESULTS_PER_QUERY)

    def _get():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        query = client.table(TABLE).select("*")

        if params.get("type"):
            query = query.eq("type", params["type"])
        if params.get("origin_skill"):
            query = query.eq("origin_skill", params["origin_skill"])

        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()
        return result.data

    result = retry_operation(_get)

    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 200,
        f"{len(result)} registros recentes",
        data={"records": result, "count": len(result)},
    )


# ============================================================
# DISPATCHER — Redireciona acao para funcao correta
# ============================================================

def dispatch(action, params):
    """Ponto de entrada do Memory Manager."""
    if action in ACTION_TO_TYPE:
        return log_entry(action, params)
    elif action == "search_memory":
        return search_memory(params)
    elif action == "get_recent":
        return get_recent(params)
    else:
        return format_response("error", 400, f"Acao de memoria desconhecida: {action}")
