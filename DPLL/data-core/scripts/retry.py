"""
retry.py — Logica de retry, cache local e rate limiter.
Protege contra falhas de rede e limites do Supabase.
"""

import json
import time
from collections import deque
from pathlib import Path

from config import CACHE_DIR, CACHE_TTL_SECONDS, MAX_REQUESTS_PER_SECOND
from utils import emergency_log, utc_isoformat


# ============================================================
# RETRY — Tentativas automaticas com backoff exponencial
# ============================================================

def retry_operation(func, max_retries=3, base_delay=1.0):
    """
    Executa funcao com retry automatico.
    Espera crescente entre tentativas: 1s, 2s, 4s.
    Retorna resultado da funcao ou dict de erro.
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                emergency_log(
                    f"RETRY | Tentativa {attempt + 1}/{max_retries} falhou: {e}. "
                    f"Proxima em {delay}s"
                )
                time.sleep(delay)

    # Todas as tentativas falharam
    emergency_log(f"RETRY_FAILED | Todas as {max_retries} tentativas falharam: {last_error}")
    return {
        "status": "error",
        "code": 503,
        "message": f"Servico indisponivel apos {max_retries} tentativas: {last_error}",
        "recovery": "Verificar conexao internet e status do Supabase em status.supabase.com",
    }


# ============================================================
# CACHE LOCAL — Leitura com fallback
# ============================================================

def cached_read(cache_key, fetch_func):
    """
    Tenta cache local antes de ir ao Supabase.
    Se Supabase falha, usa cache expirado como fallback.
    """
    cache_file = CACHE_DIR / f"{cache_key}.json"

    # Verificar cache valido
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass  # Cache corrompido — buscar do Supabase

    # Cache expirado ou inexistente — buscar do Supabase
    try:
        result = fetch_func()

        # Salvar em cache
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(
                json.dumps(result, default=str, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass  # Falha ao salvar cache — nao bloquear

        return result

    except Exception as e:
        # Supabase falhou — usar cache expirado se existir
        if cache_file.exists():
            emergency_log(
                f"CACHE_FALLBACK | Supabase offline, usando cache expirado para '{cache_key}'"
            )
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Sem cache de fallback
        raise


def clear_cache():
    """Limpa todo o cache local."""
    count = 0
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except OSError:
                pass
    return count


# ============================================================
# RATE LIMITER — Controlo de requests por segundo
# ============================================================

class RateLimiter:
    """Controla numero de requests por segundo ao Supabase."""

    def __init__(self, max_per_second=None):
        self.max_per_second = max_per_second or MAX_REQUESTS_PER_SECOND
        self.timestamps = deque()

    def wait_if_needed(self):
        """Aguarda se estiver perto do limite."""
        now = time.time()

        # Limpar timestamps com mais de 1 segundo
        while self.timestamps and now - self.timestamps[0] > 1.0:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_per_second:
            sleep_time = 1.0 - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.timestamps.append(time.time())


# Instancia global — importar de qualquer modulo
rate_limiter = RateLimiter()
