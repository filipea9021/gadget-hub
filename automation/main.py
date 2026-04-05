"""
main.py — Ponto de entrada do Content Automation Studio
Uso: python main.py
"""
import logging
import sys
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(f"logs/automation_{datetime.now():%Y%m%d}.log")])


def menu_principal():
    print("\n" + "=" * 55)
    print("  GADGET HUB — Content Automation Studio")
    print("=" * 55)
    print("\n  1. Listar produtos Shopify")
    print("  2. Gerar post para redes sociais")
    print("  3. Gerar descrição SEO para produto")
    print("  4. Buscar tendências na internet")
    print("  5. Info da loja")
    print("  0. Sair\n")
    return input("  Escolha: ").strip()


def listar_produtos():
    from platforms.shopify import ShopifyClient
    shopify = ShopifyClient()
    produtos = shopify.listar_produtos(limit=20)
    if not produtos:
        print("\n  Nenhum produto encontrado.")
        return
    print(f"\n  {len(produtos)} produtos:\n")
    for i, p in enumerate(produtos, 1):
        preco = p["variants"][0]["price"] if p.get("variants") else "?"
        print(f"  {i}. {p['title']} — €{preco}")
    return produtos


def gerar_post():
    from platforms.shopify import ShopifyClient
    from modules.generator import ContentGenerator
    shopify = ShopifyClient()
    generator = ContentGenerator()
    produtos = shopify.produtos_para_conteudo(limit=10)
    if not produtos:
        print("\n  Sem produtos.")
        return
    print("\n  Produtos:")
    for i, p in enumerate(produtos, 1):
        print(f"  {i}. {p['titulo']} — €{p['preco']}")
    escolha = input("\n  Número: ").strip()
    try:
        produto = produtos[int(escolha) - 1]
    except (ValueError, IndexError):
        print("  Inválido.")
        return
    plataforma = input("  Plataforma (instagram/linkedin/twitter): ").strip() or "instagram"
    resumo = f"PRODUTO: {produto['titulo']}\nPREÇO: €{produto['preco']}\nTIPO: {produto['tipo']}\nTAGS: {produto['tags']}\nURL: {produto['url']}"
    print(f"\n  A gerar para {plataforma}...\n")
    print(generator.gerar_post_produto(resumo, plataforma))


def info_loja():
    from platforms.shopify import ShopifyClient
    shopify = ShopifyClient()
    info = shopify.info_loja()
    print(f"\n  Loja: {info.get('name','?')}")
    print(f"  Email: {info.get('email','?')}")
    print(f"  Domínio: {info.get('domain','?')}")
    print(f"  Moeda: {info.get('currency','?')}")


def main():
    while True:
        opcao = menu_principal()
        if opcao == "1": listar_produtos()
        elif opcao == "2": gerar_post()
        elif opcao == "3": print("\n  Em desenvolvimento.")
        elif opcao == "4":
            from modules.searcher import WebSearcher
            s = WebSearcher()
            q = input("\n  Tema: ").strip() or "gadgets 2026"
            print(s.buscar(q))
        elif opcao == "5": info_loja()
        elif opcao == "0": print("\n  Até logo!\n"); break
        input("\n  Enter para continuar...")

if __name__ == "__main__":
    main()
