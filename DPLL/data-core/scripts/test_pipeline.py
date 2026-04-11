"""
Teste rapido do Data Core pipeline.
Executa: python test_pipeline.py
"""
import json
from pipeline import execute_request

request = {
    "action": "log_action",
    "module": "memory",
    "params": {
        "title": "Data Core inicializado com sucesso",
        "category": "system",
        "description": "Primeiro teste do sistema - tudo funcional!",
        "origin_skill": "data_core"
    },
    "origin_skill": "data_core"
}

print("=== TESTE DO DATA CORE ===")
print(f"Enviando: {json.dumps(request, indent=2)}")
print()

result = execute_request(request)
print("=== RESULTADO ===")
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get("status") == "ok":
    print("\n>>> SUCESSO! O Data Core esta 100% operacional! <<<")
else:
    print(f"\n>>> ERRO: {result.get('message', 'desconhecido')} <<<")
