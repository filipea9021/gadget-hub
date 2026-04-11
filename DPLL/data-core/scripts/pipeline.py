"""
pipeline.py — Pipeline de execucao segura do Data Core.
TODA requisicao ao sistema passa por aqui.
Sequencia: ambiente → permissoes → acao → params → execucao → log → resposta.
"""

import json
import sys
import traceback

import data_manager
import memory_manager
import media_manager
from config import API_VERSION, check_env
from permissions import check_permission
from utils import (
    emergency_log,
    format_response,
    format_response_json,
    generate_request_id,
    sanitize_error_message,
)
from validators import validate_action, validate_file, validate_params

# Modulos disponíveis
MODULES = {
    "memory": memory_manager,
    "media": media_manager,
    "data": data_manager,
}


def execute_request(request):
    """
    Pipeline completo e seguro para qualquer requisicao.
    Retorna SEMPRE um dict no formato padrao, nunca crasha.
    """

    # Extrair campos da requisicao
    action = request.get("action", "")
    module = request.get("module", "")
    params = request.get("params", {})
    origin = request.get("origin_skill", "unknown")
    req_id = request.get("request_id") or generate_request_id()
    api_version = request.get("api_version", API_VERSION)

    try:
        # --- 1. VERIFICAR AMBIENTE ---
        env_err = check_env()
        if env_err:
            return format_response("error", env_err["code"], env_err["message"], request_id=req_id)

        # --- 2. VERIFICAR PERMISSOES ---
        perm_err = check_permission(origin, module, action, params)
        if perm_err:
            return format_response(
                "error", perm_err["code"], perm_err["message"], request_id=req_id
            )

        # --- 3. VERIFICAR ACAO VALIDA ---
        action_err = validate_action(module, action)
        if action_err:
            return format_response(
                "error", action_err["code"], action_err["message"], request_id=req_id
            )

        # --- 4. VERIFICAR PARAMETROS ---
        param_err = validate_params(action, params)
        if param_err:
            return format_response(
                "error", param_err["code"], param_err["message"], request_id=req_id
            )

        # --- 5. VERIFICAR FICHEIRO (se aplicavel) ---
        if action in ("store_image", "store_video") and "file_path" in params:
            file_type = "image" if action == "store_image" else "video"
            file_err = validate_file(params["file_path"], file_type)
            if file_err:
                return format_response(
                    "error", file_err["code"], file_err["message"], request_id=req_id
                )

        # --- 6. EXECUTAR ---
        dispatcher = MODULES.get(module)
        if not dispatcher:
            return format_response(
                "error", 400, f"Modulo nao encontrado: {module}", request_id=req_id
            )

        result = dispatcher.dispatch(action, params)

        # Adicionar request_id a resposta
        if isinstance(result, dict):
            result["request_id"] = req_id

        # --- 7. LOG AUTOMATICO (acoes que nao sao de log) ---
        if not action.startswith("log_") and isinstance(result, dict) and result.get("code") in (200, 201):
            _auto_log(action, module, origin, result)

        return result

    except Exception as e:
        # --- ERRO NAO PREVISTO ---
        tb = traceback.format_exc()
        emergency_log(f"PIPELINE_ERROR | {action} | {sanitize_error_message(tb)}")

        return format_response(
            "error", 500,
            sanitize_error_message(f"Erro interno: {type(e).__name__}: {e}"),
            request_id=req_id,
        )


def _auto_log(action, module, origin, result):
    """Registra acao automaticamente no log de memoria."""
    try:
        memory_manager.log_entry("log_action", {
            "title": f"{origin} executou {action} em {module}",
            "origin_skill": "data_core",
            "category": "system",
            "metadata": {
                "action": action,
                "module": module,
                "origin_skill": origin,
                "result_code": result.get("code"),
            },
        })
    except Exception:
        pass  # Log automatico nunca deve bloquear a operacao principal


# ============================================================
# CLI — Permite executar via linha de comando
# ============================================================

def main():
    """Ponto de entrada quando executado via: python pipeline.py '{json}'"""
    if len(sys.argv) < 2:
        print(format_response_json(
            "error", 400,
            "Uso: python pipeline.py '{\"action\": \"...\", \"module\": \"...\", \"params\": {...}, \"origin_skill\": \"...\"}'"
        ))
        sys.exit(1)

    try:
        request = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(format_response_json("error", 400, f"JSON invalido: {e}"))
        sys.exit(1)

    result = execute_request(request)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
