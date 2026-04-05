"""
platforms/shopify.py — Integração com Shopify Admin API
Token auto-renovável via client_credentials (expira 24h)
"""
import requests
import logging
import time
import os
from typing import Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ShopifyAuth:
    """Gere autenticação com renovação automática do token."""

    def __init__(self, store_name: str, client_id: str, client_secret: str):
        self.store_name = store_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None

    def get_token(self) -> str:
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(hours=1):
                return self.access_token
        return self._request_new_token()

    def _request_new_token(self) -> str:
        url = f"https://{self.store_name}.myshopify.com/admin/oauth/access_token"
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 86399)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            logger.info("Token Shopify renovado. Expira em %d horas.", expires_in // 3600)
            return self.access_token
        except requests.exceptions.HTTPError as e:
            logger.error("Erro ao obter token: %s — %s", e, response.text[:300])
            raise
        except Exception as e:
            logger.error("Erro de conexão: %s", e)
            raise


class ShopifyClient:
    """Cliente para a Shopify Admin REST API com token auto-renovável."""

    def __init__(self, store_name="", client_id="", client_secret="", api_version="2026-01"):
        if not store_name or not client_id or not client_secret:
            try:
                from config import SHOPIFY_CONFIG
                store_name = store_name or SHOPIFY_CONFIG.get("store_name", "")
                client_id = client_id or SHOPIFY_CONFIG.get("client_id", "")
                client_secret = client_secret or SHOPIFY_CONFIG.get("client_secret", "")
                api_version = SHOPIFY_CONFIG.get("api_version", api_version)
            except ImportError:
                store_name = store_name or os.getenv("SHOPIFY_STORE_NAME", "")
                client_id = client_id or os.getenv("SHOPIFY_CLIENT_ID", "")
                client_secret = client_secret or os.getenv("SHOPIFY_CLIENT_SECRET", "")
                api_version = os.getenv("SHOPIFY_API_VERSION", api_version)

        if not all([store_name, client_id, client_secret]):
            raise ValueError("Faltam credenciais Shopify no .env")

        self.store_name = store_name
        self.api_version = api_version
        self.base_url = f"https://{store_name}.myshopify.com/admin/api/{api_version}"
        self.auth = ShopifyAuth(store_name, client_id, client_secret)
        logger.info("Shopify Client: %s (API %s)", store_name, api_version)

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        token = self.auth.get_token()
        headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}

        try:
            response = requests.request(method=method, url=url, headers=headers, json=data, params=params, timeout=30)
            if response.status_code == 401:
                self.auth.access_token = None
                token = self.auth.get_token()
                headers["X-Shopify-Access-Token"] = token
                response = requests.request(method=method, url=url, headers=headers, json=data, params=params, timeout=30)

            call_limit = response.headers.get("X-Shopify-Shop-Api-Call-Limit", "0/40")
            used, total = map(int, call_limit.split("/"))
            if used > total * 0.8:
                time.sleep(2.0)

            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            logger.error("Shopify API %s: %s", response.status_code, response.text[:300])
            raise

    # — PRODUTOS —
    def listar_produtos(self, limit=50, status="active"):
        params = {"limit": min(limit, 250), "status": status}
        result = self._request("GET", "products.json", params=params)
        return result.get("products", [])

    def buscar_produto(self, product_id):
        result = self._request("GET", f"products/{product_id}.json")
        return result.get("product", {})

    def criar_produto(self, dados):
        result = self._request("POST", "products.json", data={"product": dados})
        produto = result.get("product", {})
        logger.info("Produto criado: %s (ID: %s)", produto.get("title"), produto.get("id"))
        return produto

    def atualizar_produto(self, product_id, dados):
        result = self._request("PUT", f"products/{product_id}.json", data={"product": dados})
        return result.get("product", {})

    def atualizar_descricao(self, product_id, descricao_html):
        return self.atualizar_produto(product_id, {"body_html": descricao_html})

    def eliminar_produto(self, product_id):
        self._request("DELETE", f"products/{product_id}.json")
        return True

    # — VARIANTES —
    def listar_variantes(self, product_id):
        result = self._request("GET", f"products/{product_id}/variants.json")
        return result.get("variants", [])

    def atualizar_variante(self, variant_id, dados):
        result = self._request("PUT", f"variants/{variant_id}.json", data={"variant": dados})
        return result.get("variant", {})

    # — COLEÇÕES —
    def listar_colecoes(self):
        result = self._request("GET", "custom_collections.json")
        return result.get("custom_collections", [])

    def criar_colecao(self, titulo, descricao=""):
        result = self._request("POST", "custom_collections.json", data={"custom_collection": {"title": titulo, "body_html": descricao}})
        return result.get("custom_collection", {})

    # — BLOG —
    def listar_blogs(self):
        result = self._request("GET", "blogs.json")
        return result.get("blogs", [])

    def criar_artigo(self, blog_id, titulo, conteudo_html, autor="", tags="", publicado=True, imagem_src=None):
        artigo = {"title": titulo, "body_html": conteudo_html, "tags": tags, "published": publicado}
        if autor: artigo["author"] = autor
        if imagem_src: artigo["image"] = {"src": imagem_src}
        result = self._request("POST", f"blogs/{blog_id}/articles.json", data={"article": artigo})
        return result.get("article", {})

    # — PÁGINAS —
    def listar_paginas(self):
        result = self._request("GET", "pages.json")
        return result.get("pages", [])

    def criar_pagina(self, titulo, conteudo_html, publicada=True):
        result = self._request("POST", "pages.json", data={"page": {"title": titulo, "body_html": conteudo_html, "published": publicada}})
        return result.get("page", {})

    # — PEDIDOS —
    def listar_pedidos(self, status="any", limit=50):
        result = self._request("GET", "orders.json", params={"status": status, "limit": min(limit, 250)})
        return result.get("orders", [])

    # — INVENTÁRIO —
    def listar_locations(self):
        result = self._request("GET", "locations.json")
        return result.get("locations", [])

    # — TEMAS —
    def listar_temas(self):
        result = self._request("GET", "themes.json")
        return result.get("themes", [])

    # — INFO —
    def info_loja(self):
        result = self._request("GET", "shop.json")
        return result.get("shop", {})

    # — HELPERS —
    def produtos_para_conteudo(self, limit=10):
        produtos = self.listar_produtos(limit=limit)
        resultado = []
        for p in produtos:
            preco = p["variants"][0].get("price", "N/D") if p.get("variants") else "N/D"
            imagem = p["images"][0].get("src", "") if p.get("images") else ""
            resultado.append({
                "id": p["id"], "titulo": p["title"], "descricao": p.get("body_html", ""),
                "preco": preco, "moeda": "EUR", "tags": p.get("tags", ""),
                "tipo": p.get("product_type", ""), "vendor": p.get("vendor", ""),
                "imagem_url": imagem,
                "url": f"https://{self.store_name}.myshopify.com/products/{p.get('handle', '')}",
            })
        return resultado

    def gerar_resumo_produto(self, product_id):
        p = self.buscar_produto(product_id)
        if not p: return ""
        preco = p["variants"][0]["price"] if p.get("variants") else "N/D"
        return (
            f"PRODUTO: {p['title']}\n"
            f"TIPO: {p.get('product_type','N/D')}\n"
            f"MARCA: {p.get('vendor','N/D')}\n"
            f"PREÇO: {preco} EUR\n"
            f"TAGS: {p.get('tags','')}\n"
            f"DESCRIÇÃO: {p.get('body_html','Sem descrição')}\n"
            f"URL: https://{self.store_name}.myshopify.com/products/{p.get('handle','')}"
        )


class ShopifyPublisher:
    """Wrapper para integrar com o Publisher."""

    def __init__(self):
        from config import SHOPIFY_CONFIG
        self.client = ShopifyClient(
            store_name=SHOPIFY_CONFIG.get("store_name", ""),
            client_id=SHOPIFY_CONFIG.get("client_id", ""),
            client_secret=SHOPIFY_CONFIG.get("client_secret", ""),
            api_version=SHOPIFY_CONFIG.get("api_version", "2026-01"),
        )
        self.blog_id = SHOPIFY_CONFIG.get("blog_id", None)

    def publicar(self, conteudo, imagem_path=None, **kwargs):
        if not self.blog_id:
            blogs = self.client.listar_blogs()
            if not blogs: return {"sucesso": False, "erro": "Nenhum blog encontrado"}
            self.blog_id = blogs[0]["id"]
        linhas = conteudo.strip().split("\n")
        titulo = linhas[0].strip("# ").strip()
        corpo = "\n".join(linhas[1:]).strip()
        corpo_html = f"<p>{corpo.replace(chr(10)+chr(10), '</p><p>').replace(chr(10), '<br>')}</p>"
        tags = kwargs.get("tags", "automação, conteúdo-ia")
        try:
            artigo = self.client.criar_artigo(blog_id=self.blog_id, titulo=titulo, conteudo_html=corpo_html, tags=tags)
            return {"sucesso": True, "plataforma": "shopify", "id": artigo.get("id"), "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
