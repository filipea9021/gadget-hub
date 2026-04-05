"""
modules/publisher.py — Orquestrador de publicação multi-plataforma
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self):
        self._plataformas = {}
        self._carregar_plataformas()

    def _carregar_plataformas(self):
        try:
            from platforms.shopify import ShopifyPublisher
            self._plataformas["shopify"] = ShopifyPublisher()
            logger.info("Shopify: configurado")
        except Exception as e:
            logger.warning("Shopify não configurado: %s", e)

    def plataformas_disponiveis(self):
        return list(self._plataformas.keys())

    def publicar(self, conteudo, plataforma, imagem_path=None, dry_run=False, **kwargs):
        plataforma = plataforma.lower().strip()
        if plataforma not in self._plataformas:
            return {"sucesso": False, "erro": f"Plataforma '{plataforma}' não disponível"}
        if dry_run:
            return {"sucesso": True, "plataforma": plataforma, "dry_run": True, "preview": conteudo[:200]}
        try:
            return self._plataformas[plataforma].publicar(conteudo=conteudo, imagem_path=imagem_path, **kwargs)
        except Exception as e:
            return {"sucesso": False, "plataforma": plataforma, "erro": str(e)}
