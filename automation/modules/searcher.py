"""
modules/searcher.py — Busca de informações na internet via Serper.dev
"""
import requests
import logging
import os

logger = logging.getLogger(__name__)


class WebSearcher:
    BASE_URL = "https://google.serper.dev"

    def __init__(self, api_key=""):
        if not api_key:
            try:
                from config import SERPER_API_KEY
                api_key = SERPER_API_KEY
            except ImportError:
                api_key = os.getenv("SERPER_API_KEY", "")
        if not api_key:
            raise ValueError("SERPER_API_KEY não configurada")
        self.headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    def buscar(self, query, num_results=8, idioma="pt"):
        try:
            response = requests.post(f"{self.BASE_URL}/search", headers=self.headers,
                json={"q": query, "num": num_results, "gl": idioma, "hl": idioma}, timeout=15)
            response.raise_for_status()
            data = response.json()
            resultados = []
            for item in data.get("organic", [])[:num_results]:
                resultados.append(f"**{item.get('title','')}**\n{item.get('snippet','')}\nFonte: {item.get('link','')}\n")
            return "\n---\n".join(resultados) if resultados else "Sem resultados."
        except Exception as e:
            return f"Erro ao buscar: {e}"

    def buscar_noticias(self, query, num_results=5):
        try:
            response = requests.post(f"{self.BASE_URL}/news", headers=self.headers,
                json={"q": query, "num": num_results}, timeout=15)
            response.raise_for_status()
            data = response.json()
            resultados = []
            for item in data.get("news", [])[:num_results]:
                resultados.append(f"**{item.get('title','')}**\n{item.get('snippet','')}\nFonte: {item.get('source','')} — {item.get('date','')}\n")
            return "\n---\n".join(resultados) if resultados else "Sem notícias."
        except Exception as e:
            return f"Erro: {e}"
