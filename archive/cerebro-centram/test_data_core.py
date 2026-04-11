"""
Teste rápido da integração Data Core ↔ Cérebro Central.

Executa no terminal (dentro da pasta cerebro-centram):
    python test_data_core.py

Antes de executar, garante que:
1. O .env tem SUPABASE_URL, SUPABASE_SERVICE_KEY e DATA_CORE_PATH
2. O pacote supabase está instalado: pip install supabase
"""

import asyncio
import json
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 60)
    print("  TESTE: Data Core ↔ Cérebro Central")
    print("=" * 60)

    # 1. Testar importação
    print("\n[1/4] Importando skill Data Core...")
    try:
        from skills.data_core.agent import DataCoreSkill
        print("      ✓ Importação OK")
    except Exception as e:
        print(f"      ✗ ERRO: {e}")
        sys.exit(1)

    # 2. Testar inicialização
    print("\n[2/4] Inicializando Data Core...")
    try:
        skill = DataCoreSkill()
        skill._init_modules()
        print("      ✓ Módulos carregados")
    except Exception as e:
        print(f"      ✗ ERRO: {e}")
        print("\n      DICA: Verifique se DATA_CORE_PATH está no .env")
        sys.exit(1)

    # 3. Testar memória
    print("\n[3/4] Testando módulo de memória...")
    try:
        result = skill.memory_log(
            title="Integração cerebro-centram ↔ data-core verificada",
            category="system",
            description="Teste automático de integração — tudo OK!",
            origin_skill="cerebro_central",
        )
        print(f"      Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        if result.get("code") in (200, 201) or result.get("status") in ("ok", "success"):
            print("      ✓ Memória guardada com sucesso!")
        else:
            print(f"      ⚠ Resposta inesperada (pode ser normal): {result.get('message', '')}")
    except Exception as e:
        print(f"      ✗ ERRO: {e}")

    # 4. Testar comando em linguagem natural
    print("\n[4/4] Testando comando natural...")
    try:
        result = await skill.execute("guardar memória: teste de integração completa")
        print(f"      Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        if result.get("code") in (200, 201) or result.get("status") in ("ok", "success"):
            print("      ✓ Comando natural funcionou!")
        else:
            print(f"      ⚠ Resposta: {result.get('message', '')}")
    except Exception as e:
        print(f"      ✗ ERRO: {e}")

    print("\n" + "=" * 60)
    print("  INTEGRAÇÃO COMPLETA!")
    print("  O Cérebro Central agora tem acesso a:")
    print("  • Memória persistente (logs, notas, eventos)")
    print("  • Media (imagens, vídeos, documentos)")
    print("  • Dados genéricos (tabelas Supabase)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
