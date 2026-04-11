"""
Script rápido para testar se tudo está configurado corretamente.
Rode: python test_connection.py
"""

import sys
sys.path.insert(0, ".")

def test_ollama_connection():
    """Testa se o Ollama está rodando e acessível."""
    print("🔍 Testando conexão com Ollama...")
    try:
        import ollama
        client = ollama.Client(host="http://localhost:11434")
        models = client.list()
        model_names = [m.model for m in models.models] if hasattr(models, 'models') else []
        if model_names:
            print(f"✅ Ollama conectado! Modelos disponíveis: {', '.join(model_names)}")
            return True
        else:
            print("⚠️  Ollama conectado, mas nenhum modelo instalado.")
            print("   Rode: ollama pull llama3.1")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com Ollama: {e}")
        print("   Verifique se o Ollama está rodando (ollama serve)")
        return False


def test_config():
    """Testa se as configurações estão corretas."""
    print("\n🔍 Testando configurações...")
    try:
        from config.settings import get_settings
        settings = get_settings()
        print(f"✅ Provider: {settings.llm_provider.value}")
        print(f"✅ Modelo Ollama: {settings.ollama_model}")
        print(f"✅ Output dir: {settings.output_dir}")
        return True
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False


def test_quick_generation():
    """Testa uma geração rápida com o Ollama."""
    print("\n🔍 Testando geração rápida...")
    try:
        import ollama
        client = ollama.Client(host="http://localhost:11434")
        response = client.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            options={"temperature": 0.1, "num_predict": 10},
        )
        text = response["message"]["content"].strip()
        print(f"✅ Resposta do modelo: {text}")
        return True
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🧠 CEREBRO CENTRAM — Teste de Configuração")
    print("=" * 50)

    results = []
    results.append(("Conexão Ollama", test_ollama_connection()))
    results.append(("Configurações", test_config()))

    if results[0][1]:  # Se Ollama conectou
        results.append(("Geração rápida", test_quick_generation()))

    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL")
    print("=" * 50)
    all_ok = True
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\n🚀 Tudo pronto! Rode: python core/cli.py interactive")
    else:
        print("\n⚠️  Corrija os erros acima antes de continuar.")
