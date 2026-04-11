"""
data_manager.py — Modulo de dados estruturados do Data Core.
Armazena metricas, configuracoes, resultados e outros dados do sistema.
"""

from config import DEFAULT_RESULTS_PER_QUERY, MAX_RESULTS_PER_QUERY, get_supabase
from retry import rate_limiter, retry_operation
from utils import format_response, utc_isoformat

TABLE = "system_data"


# ============================================================
# OPERACOES DE ESCRITA
# ============================================================

def store_data(params):
    """Guarda ou atualiza um dado estruturado (upsert por namespace+key)."""
    namespace = params["namespace"]
    key = params["key"]
    value = params["value"]

    record = {
        "namespace": namespace,
        "key": key,
        "value": value,
        "data_type": params.get("data_type", "general"),
        "description": params.get("description"),
        "updated_at": utc_isoformat(),
    }
    record = {k: v for k, v in record.items() if v is not None}

    def _upsert():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).upsert(
            record,
            on_conflict="namespace,key",
        ).execute()
        return result.data[0] if result.data else {}

    result = retry_operation(_upsert)
    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 201,
        f"Dado armazenado: {namespace}/{key}",
        data={"id": result.get("id"), "namespace": namespace, "key": key},
    )


def update_data(params):
    """Atualiza valor de um dado existente."""
    namespace = params["namespace"]
    key = params["key"]

    update = {
        "value": params["value"],
        "updated_at": utc_isoformat(),
    }
    if params.get("description"):
        update["description"] = params["description"]

    # Incrementar versao
    def _update():
        rate_limiter.wait_if_needed()
        client = get_supabase()

        # Buscar versao atual
        existing = client.table(TABLE).select("version") \
            .eq("namespace", namespace).eq("key", key).execute()

        if not existing.data:
            return None

        current_version = existing.data[0].get("version", 1)
        update["version"] = current_version + 1

        result = client.table(TABLE).update(update) \
            .eq("namespace", namespace).eq("key", key).execute()
        return result.data[0] if result.data else None

    result = retry_operation(_update)
    if isinstance(result, dict) and result.get("status") == "error":
        return result
    if not result:
        return format_response(
            "error", 404,
            f"Dado nao encontrado: {namespace}/{key}",
        )

    return format_response(
        "success", 200,
        f"Dado atualizado: {namespace}/{key}",
        data=result,
    )


def delete_data(params):
    """Remove um dado (apenas data_core pode chamar isto)."""
    namespace = params["namespace"]
    key = params["key"]

    def _delete():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).delete() \
            .eq("namespace", namespace).eq("key", key).execute()
        return result.data

    result = retry_operation(_delete)
    if isinstance(result, dict) and result.get("status") == "error":
        return result

    if not result:
        return format_response("error", 404, f"Dado nao encontrado: {namespace}/{key}")

    return format_response("success", 200, f"Dado removido: {namespace}/{key}")


# ============================================================
# OPERACOES DE LEITURA
# ============================================================

def get_data(params):
    """Busca um dado por namespace e key."""
    namespace = params["namespace"]
    key = params["key"]

    def _get():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).select("*") \
            .eq("namespace", namespace).eq("key", key).execute()
        return result.data[0] if result.data else None

    result = retry_operation(_get)
    if isinstance(result, dict) and result.get("status") == "error":
        return result
    if not result:
        return format_response("error", 404, f"Dado nao encontrado: {namespace}/{key}")

    return format_response("success", 200, "Dado encontrado", data=result)


def list_data(params):
    """Lista todos os dados de um namespace."""
    namespace = params["namespace"]
    limit = min(params.get("limit", DEFAULT_RESULTS_PER_QUERY), MAX_RESULTS_PER_QUERY)
    offset = max(params.get("offset", 0), 0)

    def _list():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        query = client.table(TABLE).select("*").eq("namespace", namespace)

        if params.get("data_type"):
            query = query.eq("data_type", params["data_type"])

        query = query.order("updated_at", desc=True)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return result.data

    result = retry_operation(_list)
    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 200,
        f"{len(result)} dados encontrados em '{namespace}'",
        data={"records": result, "count": len(result), "namespace": namespace},
    )


# ============================================================
# DISPATCHER
# ============================================================

def dispatch(action, params):
    """Ponto de entrada do Data Manager."""
    handlers = {
        "store_data": store_data,
        "get_data": get_data,
        "update_data": update_data,
        "delete_data": delete_data,
        "list_data": list_data,
    }
    handler = handlers.get(action)
    if not handler:
        return format_response("error", 400, f"Acao de dados desconhecida: {action}")
    return handler(params)
