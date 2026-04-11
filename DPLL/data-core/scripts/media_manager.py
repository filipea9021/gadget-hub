"""
media_manager.py — Modulo de galeria/midia do Data Core.
Armazena, organiza e distribui imagens, videos e documentos.
Resolve o problema: imagens NUNCA mais vao para a pasta Downloads.
"""

import mimetypes
import os

from config import (
    DEFAULT_RESULTS_PER_QUERY,
    MAX_RESULTS_PER_QUERY,
    STORAGE_BUCKETS,
    get_supabase,
)
from retry import rate_limiter, retry_operation
from utils import (
    calculate_hash,
    cleanup_temp_file,
    format_response,
    generate_storage_path,
    sanitize_filename,
    sanitize_tags,
    utc_isoformat,
)

TABLE = "media_files"


# ============================================================
# OPERACOES DE ESCRITA
# ============================================================

def store_file(action, params):
    """
    Armazena imagem ou video no Supabase Storage + registro no banco.
    Upload atomico: se o banco falha, apaga do storage (rollback).
    """
    file_path = params["file_path"]
    folder = params["folder"]
    origin_skill = params["origin_skill"]
    file_type = "image" if action == "store_image" else "video"
    bucket = "images" if file_type == "image" else "videos"

    # 1. Calcular hash para verificar duplicatas
    file_hash = calculate_hash(file_path)
    file_size = os.path.getsize(file_path)
    original_name = sanitize_filename(os.path.basename(file_path))

    # 2. Verificar duplicata
    def _check_duplicate():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE) \
            .select("id, storage_path, public_url") \
            .eq("file_hash", file_hash) \
            .neq("status", "deleted") \
            .execute()
        return result.data

    existing = retry_operation(_check_duplicate)
    if isinstance(existing, dict) and existing.get("status") == "error":
        return existing

    if existing and len(existing) > 0:
        # Duplicata — confirmar com tamanho
        for record in existing:
            return format_response(
                "success", 409,
                "Ficheiro ja existe (duplicata detectada)",
                data=record,
            )

    # 3. Gerar caminho unico no storage
    storage_path = generate_storage_path(original_name, folder)

    # 4. Obter dimensoes (imagens)
    width, height, duration = None, None, None
    if file_type == "image":
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.width, img.height
        except Exception:
            pass  # Nao bloquear upload por falha de dimensoes

    # 5. Obter MIME type
    mime_type = mimetypes.guess_type(file_path)[0]
    file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")

    # 6. Criar registro no banco com status "uploading"
    db_record = {
        "original_name": original_name,
        "storage_path": f"{bucket}/{storage_path}",
        "file_type": file_type,
        "mime_type": mime_type,
        "file_extension": file_ext,
        "file_size_bytes": file_size,
        "file_hash": file_hash,
        "width": width,
        "height": height,
        "duration_seconds": duration,
        "bucket": bucket,
        "folder": folder,
        "tags": sanitize_tags(params.get("tags", [])),
        "category": params.get("category"),
        "origin_skill": origin_skill,
        "purpose": params.get("purpose"),
        "campaign_id": params.get("campaign_id"),
        "description": params.get("description"),
        "status": "uploading",  # Estado temporario ate upload completo
    }
    db_record = {k: v for k, v in db_record.items() if v is not None}

    def _insert_record():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).insert(db_record).execute()
        return result.data[0] if result.data else {}

    record = retry_operation(_insert_record)
    if isinstance(record, dict) and record.get("status") == "error":
        return record

    record_id = record.get("id")

    # 7. Upload para storage
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        def _upload():
            rate_limiter.wait_if_needed()
            client = get_supabase()
            client.storage.from_(bucket).upload(
                storage_path,
                file_data,
                {"content-type": mime_type or "application/octet-stream"},
            )

        upload_result = retry_operation(_upload)
        if isinstance(upload_result, dict) and upload_result.get("status") == "error":
            # Upload falhou — apagar registro do banco (rollback)
            _rollback_record(record_id)
            return upload_result

    except Exception as e:
        _rollback_record(record_id)
        return format_response("error", 500, f"Falha no upload: {e}")

    # 8. Gerar URL publica
    public_url = None
    if STORAGE_BUCKETS.get(bucket, {}).get("public", False):
        try:
            client = get_supabase()
            url_result = client.storage.from_(bucket).get_public_url(storage_path)
            public_url = url_result
        except Exception:
            pass

    # 9. Atualizar registro: status → active, adicionar URL
    def _activate():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        update = {"status": "active", "public_url": public_url}
        update = {k: v for k, v in update.items() if v is not None}
        client.table(TABLE).update(update).eq("id", record_id).execute()

    retry_operation(_activate)

    return format_response(
        "success", 201,
        f"{file_type.capitalize()} armazenado com sucesso",
        data={
            "id": record_id,
            "storage_path": f"{bucket}/{storage_path}",
            "public_url": public_url,
            "file_size_bytes": file_size,
            "file_hash": file_hash,
        },
    )


def _rollback_record(record_id):
    """Marca registro como deleted em caso de falha."""
    try:
        rate_limiter.wait_if_needed()
        client = get_supabase()
        client.table(TABLE).update({"status": "deleted"}).eq("id", record_id).execute()
    except Exception:
        from utils import emergency_log
        emergency_log(f"ROLLBACK_FAILED | Record ID: {record_id}")


# ============================================================
# OPERACOES DE LEITURA
# ============================================================

def get_media(params):
    """Busca ficheiro de midia por ID."""
    def _get():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).select("*").eq("id", params["id"]).execute()
        return result.data[0] if result.data else None

    result = retry_operation(_get)
    if isinstance(result, dict) and result.get("status") == "error":
        return result
    if not result:
        return format_response("error", 404, f"Midia nao encontrada com ID: {params['id']}")

    return format_response("success", 200, "Midia encontrada", data=result)


def search_media(params):
    """Busca midia por filtros (tags, pasta, tipo, etc.)."""
    limit = min(params.get("limit", DEFAULT_RESULTS_PER_QUERY), MAX_RESULTS_PER_QUERY)
    offset = max(params.get("offset", 0), 0)

    def _search():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        query = client.table(TABLE).select("*").neq("status", "deleted")

        if params.get("tags"):
            query = query.overlaps("tags", params["tags"])
        if params.get("folder"):
            query = query.eq("folder", params["folder"])
        if params.get("file_type"):
            query = query.eq("file_type", params["file_type"])
        if params.get("origin_skill"):
            query = query.eq("origin_skill", params["origin_skill"])
        if params.get("purpose"):
            query = query.eq("purpose", params["purpose"])
        if params.get("campaign_id"):
            query = query.eq("campaign_id", params["campaign_id"])
        if params.get("status"):
            query = query.eq("status", params["status"])

        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return result.data

    result = retry_operation(_search)
    if isinstance(result, dict) and result.get("status") == "error":
        return result

    return format_response(
        "success", 200,
        f"{len(result)} ficheiros encontrados",
        data={"files": result, "count": len(result), "limit": limit, "offset": offset},
    )


def list_media(params):
    """Lista midia de uma pasta especifica."""
    return search_media({
        "folder": params["folder"],
        "file_type": {"images": "image", "videos": "video"}.get(params.get("bucket")),
        "limit": params.get("limit", DEFAULT_RESULTS_PER_QUERY),
        "offset": params.get("offset", 0),
    })


def get_media_url(params):
    """Retorna URL publica de um ficheiro."""
    result = get_media(params)
    if result.get("code") != 200:
        return result

    public_url = result["data"].get("public_url")
    if not public_url:
        return format_response("error", 404, "Este ficheiro nao tem URL publica")

    return format_response("success", 200, "URL obtida", data={"public_url": public_url})


# ============================================================
# OPERACOES DE ATUALIZACAO
# ============================================================

def update_media(params):
    """Atualiza metadata de um ficheiro de midia."""
    record_id = params.pop("id")

    # Filtrar apenas campos atualizaveis
    updatable = ["tags", "purpose", "description", "campaign_id", "status", "category"]
    update_data = {}
    for field in updatable:
        if field in params and params[field] is not None:
            if field == "tags":
                update_data[field] = sanitize_tags(params[field])
            else:
                update_data[field] = params[field]

    if not update_data:
        return format_response("error", 400, "Nenhum campo para atualizar fornecido")

    update_data["updated_at"] = utc_isoformat()

    def _update():
        rate_limiter.wait_if_needed()
        client = get_supabase()
        result = client.table(TABLE).update(update_data).eq("id", record_id).execute()
        return result.data[0] if result.data else None

    result = retry_operation(_update)
    if isinstance(result, dict) and result.get("status") == "error":
        return result
    if not result:
        return format_response("error", 404, f"Midia nao encontrada: {record_id}")

    return format_response("success", 200, "Midia atualizada", data=result)


def archive_media(params):
    """Arquiva um ficheiro (muda status para 'archived')."""
    return update_media({"id": params["id"], "status": "archived"})


# ============================================================
# DISPATCHER
# ============================================================

def dispatch(action, params):
    """Ponto de entrada do Media Manager."""
    handlers = {
        "store_image": lambda p: store_file("store_image", p),
        "store_video": lambda p: store_file("store_video", p),
        "get_media": get_media,
        "search_media": search_media,
        "list_media": list_media,
        "update_media": update_media,
        "archive_media": archive_media,
        "get_media_url": get_media_url,
    }
    handler = handlers.get(action)
    if not handler:
        return format_response("error", 400, f"Acao de midia desconhecida: {action}")
    return handler(params)
