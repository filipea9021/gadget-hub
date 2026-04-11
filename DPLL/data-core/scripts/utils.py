"""
utils.py — Funcoes auxiliares usadas por todos os modulos do Data Core.
Hash, formatacao de respostas, sanitizacao, timestamps UTC.
"""

import hashlib
import json
import os
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# TIMESTAMPS — Sempre UTC
# ============================================================

def utc_now():
    """Retorna datetime actual em UTC. USAR SEMPRE em vez de datetime.now()."""
    return datetime.now(timezone.utc)


def utc_isoformat():
    """Retorna string ISO 8601 em UTC."""
    return utc_now().isoformat()


# ============================================================
# RESPOSTAS — Formato padrao
# ============================================================

def format_response(status, code, message, data=None, request_id=None):
    """Cria resposta no formato padrao. TODA resposta do sistema usa isto."""
    response = {
        "status": status,
        "code": code,
        "message": message,
        "data": data or {},
        "request_id": request_id or "",
        "timestamp": utc_isoformat(),
    }
    return response


def format_response_json(status, code, message, data=None, request_id=None):
    """Igual a format_response mas retorna JSON string."""
    return json.dumps(
        format_response(status, code, message, data, request_id),
        indent=2,
        ensure_ascii=False,
        default=str,
    )


# ============================================================
# HASH — Calculo seguro (streaming para ficheiros grandes)
# ============================================================

def calculate_hash(file_path, chunk_size=8192):
    """Calcula SHA-256 sem carregar ficheiro inteiro em memoria."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


# ============================================================
# SANITIZACAO — Nomes, tags, metadata
# ============================================================

def sanitize_filename(name):
    """Remove caracteres perigosos de nomes de ficheiros."""
    if not name or not isinstance(name, str):
        return "unnamed_file"

    # 1. Normalizar unicode (NFC — forma canonica composta)
    name = unicodedata.normalize("NFC", name)
    # 2. Remover path traversal
    name = name.replace("..", "").replace("/", "_").replace("\\", "_")
    # 3. Remover caracteres de controlo
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    # 4. Remover caracteres problematicos para URLs
    name = re.sub(r'[<>:"|?*]', "_", name)
    # 5. Limitar tamanho
    name = name[:200]
    # 6. Garantir que nao e vazio
    if not name.strip() or name.strip() == ".":
        name = "unnamed_file"
    return name.strip()


def sanitize_tags(tags):
    """Valida e limita array de tags."""
    if not isinstance(tags, list):
        return []

    from config import MAX_TAGS, MAX_TAG_LENGTH

    clean = []
    for tag in tags[:MAX_TAGS]:
        if isinstance(tag, str) and tag.strip():
            # Normalizar: minusculas, sem espacos extra, limitado
            clean_tag = tag.strip()[:MAX_TAG_LENGTH].lower()
            clean_tag = re.sub(r"\s+", "-", clean_tag)  # espacos → hifens
            if clean_tag and clean_tag not in clean:  # sem duplicatas
                clean.append(clean_tag)
    return clean


def sanitize_metadata(metadata):
    """Limita profundidade e tamanho de metadata JSONB."""
    if not isinstance(metadata, dict):
        return {}

    from config import MAX_METADATA_BYTES, MAX_METADATA_DEPTH

    # Verificar tamanho total
    try:
        json_str = json.dumps(metadata, default=str)
    except (TypeError, ValueError):
        return {"_error": "metadata nao serializavel para JSON"}

    if len(json_str.encode("utf-8")) > MAX_METADATA_BYTES:
        return {
            "_error": f"metadata excede {MAX_METADATA_BYTES // 1000}KB",
            "_original_size_bytes": len(json_str.encode("utf-8")),
        }

    # Verificar profundidade
    def _check_depth(obj, current=0):
        if current > MAX_METADATA_DEPTH:
            return False
        if isinstance(obj, dict):
            return all(_check_depth(v, current + 1) for v in obj.values())
        if isinstance(obj, list):
            return all(_check_depth(v, current + 1) for v in obj)
        return True

    if not _check_depth(metadata):
        return {
            "_error": f"metadata excede profundidade maxima de {MAX_METADATA_DEPTH} niveis"
        }

    return metadata


# ============================================================
# GERACAO DE CAMINHOS — Unicos, seguros
# ============================================================

def generate_storage_path(original_name, folder):
    """Gera caminho unico no storage. NUNCA usa o nome original como caminho."""
    ext = Path(original_name).suffix.lower() if original_name else ""
    # Garantir extensao valida
    if not ext or len(ext) > 10:
        ext = ""
    unique_id = uuid.uuid4().hex[:12]
    timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{unique_id}{ext}"
    return f"{folder}/{safe_name}"


def generate_request_id():
    """Gera ID unico para requisicao."""
    return uuid.uuid4().hex[:16]


# ============================================================
# SEGURANCA — Sanitizacao de erros
# ============================================================

def sanitize_error_message(error_msg):
    """Remove credenciais e dados sensiveis de mensagens de erro."""
    sensitive_patterns = [
        os.getenv("SUPABASE_SERVICE_KEY", ""),
        os.getenv("SUPABASE_ANON_KEY", ""),
        os.getenv("SUPABASE_URL", ""),
    ]
    sanitized = str(error_msg)
    for pattern in sensitive_patterns:
        if pattern and len(pattern) > 5:
            sanitized = sanitized.replace(pattern, "[REDACTED]")
    return sanitized


# ============================================================
# FICHEIROS TEMPORARIOS — Limpeza segura
# ============================================================

def cleanup_temp_file(file_path):
    """Apaga ficheiro temporario de forma segura."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass  # Nao bloquear por falha de limpeza


# ============================================================
# LOGGING DE EMERGENCIA — Quando o banco nao funciona
# ============================================================

EMERGENCY_LOG_PATH = Path("/tmp/data_core_emergency.log")

_log_depth = 0
MAX_LOG_DEPTH = 1


def emergency_log(message):
    """Escreve em ficheiro local quando o banco nao esta disponivel."""
    try:
        with open(EMERGENCY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{utc_isoformat()} | {message}\n")
    except Exception:
        pass  # Ultimo recurso — nao ha mais nada a fazer
