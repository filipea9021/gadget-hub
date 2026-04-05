"""
modules/generator.py — Geração de conteúdo com Claude API
"""
import logging
import os

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self, api_key=""):
        if not api_key:
            try:
                from config import ANTHROPIC_API_KEY
                api_key = ANTHROPIC_API_KEY
            except ImportError:
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada")
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("pip install anthropic")
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 1500

    def gerar(self, informacao, plataforma="instagram", tom="engajante", idioma="português", instrucoes_extras=""):
        limites = {
            "instagram": "150-250 palavras + 10 hashtags + emojis",
            "linkedin": "200-400 palavras, profissional, 3-5 hashtags",
            "twitter": "máximo 280 caracteres, 2-3 hashtags",
            "wordpress": "600-1000 palavras, H2/H3, SEO, CTA",
            "shopify": "600-1200 palavras, HTML, SEO, tags de produto",
        }
        prompt = f"Gera conteúdo para {plataforma.upper()} em {idioma}.\nTOM: {tom}\nFORMATO: {limites.get(plataforma, 'Adapta')}\n\nINFORMAÇÃO BASE:\n{informacao}"
        if instrucoes_extras:
            prompt += f"\n\nINSTRUÇÕES ADICIONAIS:\n{instrucoes_extras}"
        prompt += "\n\n---\nGera APENAS o conteúdo final:"
        try:
            response = self.client.messages.create(model=self.model, max_tokens=self.max_tokens, messages=[{"role": "user", "content": prompt}])
            return response.content[0].text
        except Exception as e:
            return f"Erro: {e}"

    def gerar_descricao_produto(self, resumo_produto, tom="persuasivo"):
        return self.gerar(resumo_produto, plataforma="shopify", tom=tom, instrucoes_extras="Gera descrição HTML para Shopify. Inclui benefícios, specs e CTA. Usa <h2>, <p>, <ul>, <li>, <strong>.")

    def gerar_post_produto(self, resumo_produto, plataforma="instagram"):
        return self.gerar(resumo_produto, plataforma=plataforma, tom="promocional e moderno", instrucoes_extras="Destaca o preço, benefícios e inclui CTA.")
