"""
health_check.py — Verificacao completa do estado do Data Core.
Executar ANTES de operacoes importantes e periodicamente.
"""

import json
import os
import shutil
import sys
from datetime import timedelta
from pathlib import Path

from config import (
    CACHE_DIR,
    LOG_RETENTION_DAYS,
    STALE_UPLOAD_MAX_AGE_HOURS,
    STORAGE_BUCKETS,
    TEMP_FILE_MAX_AGE_DAYS,
    check_env,
    check_supabase_connection,
    get_supabase,
)
from retry import rate_limiter
from utils import emergency_log, format_response_json, utc_isoformat, utc_now

REQUIRED_TABLES = ["memory_logs", "media_files", "system_data"]


# ============================================================
# VERIFICACOES INDIVIDUAIS
# ============================================================

def check_dependencies():
    """Verifica se todas as dependencias Python estao instaladas."""
    required = {
        "supabase": "supabase",
        "dotenv": "python-dotenv",
        "PIL": "Pillow",
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        return {
            "status": "error",
            "code": 500,
            "message": f"Dependencias em falta: {', '.join(missing)}",
            "recovery": f"pip install {' '.join(missing)} --break-system-packages",
        }
    return None


def check_tables():
    """Verifica se todas as tabelas necessarias existem."""
    try:
        client = get_supabase()
        for table in REQUIRED_TABLES:
            rate_limiter.wait_if_needed()
            try:
                client.table(table).select("id").limit(1).execute()
            except Exception as e:
                if "does not exist" in str(e).lower() or "relation" in str(e).lower():
                    return {
                        "status": "error",
                        "code": 500,
                        "message": f"Tabela '{table}' nao existe",
                        "recovery": "Executar setup_supabase.sql no SQL Editor do Supabase",
                    }
                raise
    except RuntimeError as e:
        return {"status": "error", "code": 500, "message": str(e)}
    return None


def check_buckets():
    """Verifica se os buckets de storage existem."""
    try:
        client = get_supabase()
        for bucket_name in STORAGE_BUCKETS:
            rate_limiter.wait_if_needed()
            try:
                client.storage.get_bucket(bucket_name)
            except Exception:
                return {
                    "status": "warning",
                    "code": 200,
                    "message": f"Bucket '{bucket_name}' nao existe — sera criado automaticamente",
                    "auto_fix": True,
                }
    except RuntimeError as e:
        return {"status": "error", "code": 500, "message": str(e)}
    return None


def check_storage_usage():
    """Verifica uso de storage."""
    try:
        client = get_supabase()
        rate_limiter.wait_if_needed()
        result = client.table("media_files") \
            .select("file_size_bytes") \
            .neq("status", "deleted") \
            .execute()

        total_bytes = sum(row.get("file_size_bytes", 0) or 0 for row in result.data)
        limit_bytes = 1 * 1024 * 1024 * 1024  # 1GB (plano gratuito)
        usage_percent = (total_bytes / limit_bytes) * 100 if limit_bytes > 0 else 0

        if usage_percent > 95:
            return {
                "status": "error",
                "code": 507,
                "message": f"Storage quase cheio: {usage_percent:.1f}% ({total_bytes / 1024 / 1024:.1f}MB)",
                "recovery": "Arquivar ficheiros antigos ou fazer upgrade do plano Supabase",
            }
        elif usage_percent > 80:
            return {
                "status": "warning",
                "code": 200,
                "message": f"Storage em {usage_percent:.1f}% ({total_bytes / 1024 / 1024:.1f}MB)",
            }
    except Exception:
        pass  # Nao bloquear health check por falha de calculo
    return None


def check_disk_space(required_bytes=50 * 1024 * 1024):
    """Verifica espaco livre em disco local."""
    try:
        usage = shutil.disk_usage("/tmp")
        if usage.free < required_bytes:
            return {
                "status": "warning",
                "code": 507,
                "message": f"Disco local com pouco espaco: {usage.free / 1024 / 1024:.0f}MB livres",
            }
    except Exception:
        pass
    return None


def check_stale_uploads():
    """Verifica se ha uploads presos (status 'uploading' ha mais de 1h)."""
    try:
        client = get_supabase()
        cutoff = (utc_now() - timedelta(hours=STALE_UPLOAD_MAX_AGE_HOURS)).isoformat()
        rate_limiter.wait_if_needed()
        result = client.table("media_files") \
            .select("id") \
            .eq("status", "uploading") \
            .lt("created_at", cutoff) \
            .execute()

        if result.data:
            return {
                "status": "warning",
                "code": 200,
                "message": f"{len(result.data)} uploads presos encontrados (>1h)",
                "auto_fix": True,
            }
    except Exception:
        pass
    return None


def check_emergency_log():
    """Verifica se ha entradas no log de emergencia."""
    log_path = Path("/tmp/data_core_emergency.log")
    if log_path.exists():
        size = log_path.stat().st_size
        if size > 0:
            return {
                "status": "warning",
                "code": 200,
                "message": f"Log de emergencia tem {size} bytes — verificar /tmp/data_core_emergency.log",
            }
    return None


# ============================================================
# HEALTH CHECK COMPLETO
# ============================================================

def _run_check(name, func):
    """Executa verificacao com protecao contra erros."""
    try:
        result = func()
        if result is None:
            return {"name": name, "status": "ok"}
        return {"name": name, **result}
    except Exception as e:
        return {"name": name, "status": "error", "message": str(e)}


def run_health_check():
    """Executa TODAS as verificacoes e retorna relatorio."""
    checks = [
        _run_check("Dependencias Python", check_dependencies),
        _run_check("Variaveis de ambiente", check_env),
        _run_check("Disco local", check_disk_space),
        _run_check("Conexao Supabase", check_supabase_connection),
        _run_check("Tabelas", check_tables),
        _run_check("Buckets", check_buckets),
        _run_check("Espaco storage", check_storage_usage),
        _run_check("Uploads presos", check_stale_uploads),
        _run_check("Log emergencia", check_emergency_log),
    ]

    failed = [c for c in checks if c.get("status") == "error"]
    warnings = [c for c in checks if c.get("status") == "warning"]

    if failed:
        status = "unhealthy" if len(failed) >= 3 else "degraded"
    else:
        status = "healthy"

    return {
        "system_status": status,
        "total": len(checks),
        "passed": len(checks) - len(failed) - len(warnings),
        "warnings": len(warnings),
        "failed": len(failed),
        "details": checks,
        "timestamp": utc_isoformat(),
    }


# ============================================================
# AUTO-REPARACAO
# ============================================================

def auto_repair():
    """Detecta e corrige problemas automaticamente."""
    repairs = []

    # 1. Criar buckets em falta
    try:
        client = get_supabase()
        for bucket_name, options in STORAGE_BUCKETS.items():
            try:
                client.storage.get_bucket(bucket_name)
            except Exception:
                try:
                    client.storage.create_bucket(bucket_name, options={"public": options.get("public", False)})
                    repairs.append(f"Bucket '{bucket_name}' criado")
                except Exception as e:
                    repairs.append(f"Falha ao criar bucket '{bucket_name}': {e}")
    except Exception:
        repairs.append("Nao foi possivel verificar buckets (sem conexao)")

    # 2. Limpar uploads presos
    try:
        client = get_supabase()
        cutoff = (utc_now() - timedelta(hours=STALE_UPLOAD_MAX_AGE_HOURS)).isoformat()
        rate_limiter.wait_if_needed()
        stale = client.table("media_files") \
            .select("id, storage_path, bucket") \
            .eq("status", "uploading") \
            .lt("created_at", cutoff) \
            .execute()

        for record in stale.data:
            try:
                # Tentar apagar do storage
                if record.get("storage_path") and record.get("bucket"):
                    path = record["storage_path"].replace(f"{record['bucket']}/", "", 1)
                    try:
                        client.storage.from_(record["bucket"]).remove([path])
                    except Exception:
                        pass
                # Marcar como deleted
                client.table("media_files") \
                    .update({"status": "deleted"}) \
                    .eq("id", record["id"]) \
                    .execute()
            except Exception:
                pass
        if stale.data:
            repairs.append(f"{len(stale.data)} uploads presos limpos")
    except Exception:
        pass

    # 3. Limpar ficheiros temporarios antigos
    try:
        client = get_supabase()
        cutoff = (utc_now() - timedelta(days=TEMP_FILE_MAX_AGE_DAYS)).isoformat()
        rate_limiter.wait_if_needed()
        old_temp = client.table("media_files") \
            .select("id") \
            .eq("status", "temp") \
            .lt("created_at", cutoff) \
            .execute()

        for record in old_temp.data:
            try:
                client.table("media_files") \
                    .update({"status": "deleted"}) \
                    .eq("id", record["id"]) \
                    .execute()
            except Exception:
                pass
        if old_temp.data:
            repairs.append(f"{len(old_temp.data)} ficheiros temporarios arquivados")
    except Exception:
        pass

    # 4. Limpar cache local
    try:
        from retry import clear_cache
        cleared = clear_cache()
        if cleared > 0:
            repairs.append(f"{cleared} entradas de cache limpas")
    except Exception:
        pass

    return {
        "status": "success",
        "repairs_made": len(repairs),
        "details": repairs,
        "timestamp": utc_isoformat(),
    }


# ============================================================
# CLI
# ============================================================

def main():
    """Executar via linha de comando: python health_check.py [--repair]"""
    if "--repair" in sys.argv:
        result = auto_repair()
    else:
        result = run_health_check()

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
