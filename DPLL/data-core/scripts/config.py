"""
config.py — Configuracao central do Data Core Agent.
Carrega variaveis de ambiente e inicializa conexao com Supabase.
"""

import os
import sys
from pathlib import Path

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv nao instalado — usar variaveis de ambiente do sistema

# --- Constantes do Sistema ---

SYSTEM_NAME = "data-core"
API_VERSION = "1.0"

# Limites de ficheiros
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024   # 10MB
MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024   # 50MB
MAX_DOC_SIZE_BYTES = 20 * 1024 * 1024     # 20MB

# Limites de dados
MAX_RESULTS_PER_QUERY = 100
DEFAULT_RESULTS_PER_QUERY = 20
MAX_TAGS = 50
MAX_TAG_LENGTH = 100
MAX_METADATA_BYTES = 50_000  # 50KB
MAX_METADATA_DEPTH = 3

# Limpeza
TEMP_FILE_MAX_AGE_DAYS = 7
STALE_UPLOAD_MAX_AGE_HOURS = 1
LOG_RETENTION_DAYS = 90

# Cache
CACHE_DIR = Path("/tmp/data_core_cache")
CACHE_TTL_SECONDS = 300  # 5 minutos

# Rate limiting
MAX_REQUESTS_PER_SECOND = 50

# Buckets do Supabase Storage
STORAGE_BUCKETS = {
    "images": {"public": True},
    "videos": {"public": True},
    "documents": {"public": False},
}

# Pastas permitidas por bucket
ALLOWED_FOLDERS = {
    "images": ["marketing", "products", "branding", "temp"],
    "videos": ["marketing", "tutorials", "temp"],
    "documents": ["reports", "exports"],
}

# --- Validacao de Ambiente ---

REQUIRED_ENV_VARS = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]


def check_env():
    """Verifica se todas as variaveis de ambiente estao configuradas."""
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        return {
            "status": "error",
            "code": 500,
            "message": f"Variaveis de ambiente em falta: {', '.join(missing)}",
            "recovery": (
                f"Criar ficheiro .env em {Path(__file__).parent / '.env'} com: "
                + ", ".join(f"{v}=<valor>" for v in missing)
            ),
        }
    return None


# --- Conexao Supabase ---

_supabase_client = None


def get_supabase():
    """Retorna cliente Supabase (singleton). Cria na primeira chamada."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Verificar ambiente primeiro
    env_err = check_env()
    if env_err:
        raise RuntimeError(env_err["message"])

    try:
        from supabase import create_client, Client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        _supabase_client = create_client(url, key)
        return _supabase_client
    except ImportError:
        raise RuntimeError(
            "Modulo 'supabase' nao instalado. "
            "Executar: pip install supabase --break-system-packages"
        )
    except Exception as e:
        raise RuntimeError(f"Falha ao conectar ao Supabase: {e}")


def check_supabase_connection():
    """Testa se a conexao ao Supabase esta funcional."""
    try:
        client = get_supabase()
        # Query simples para testar conexao
        client.table("memory_logs").select("id").limit(1).execute()
        return None  # OK
    except Exception as e:
        return {
            "status": "error",
            "code": 503,
            "message": f"Conexao ao Supabase falhou: {e}",
            "recovery": "Verificar SUPABASE_URL e SUPABASE_SERVICE_KEY no ficheiro .env",
        }
