"""
CIS — YouTube Scraper (Fase 2)
Coleta conteúdo viral real via YouTube Data API v3.

Setup:
  1. Google Cloud Console → habilitar YouTube Data API v3
  2. Criar API Key → YOUTUBE_API_KEY no .env
  Quota: 10.000 unidades/dia (search=100 por chamada, list=1)
"""

import os
import json
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional


# Mapeamento nicho → YouTube category IDs
NICHE_CATEGORIES = {
    "finance":       ["27", "25"],   # Education, News
    "investimento":  ["27", "25"],
    "crypto":        ["27", "28"],
    "tech":          ["28", "27"],   # Science & Technology, Education
    "tecnologia":    ["28", "27"],
    "ia":            ["28", "27"],
    "fitness":       ["17", "26"],   # Sports, Howto & Style
    "saude":         ["26", "27"],
    "empreendedorismo": ["27", "22"],
    "marketing":     ["27", "22"],
    "comedy":        ["23", "24"],   # Comedy, Entertainment
    "entretenimento":["24", "23"],
    "gaming":        ["20"],
    "music":         ["10"],
    "lifestyle":     ["22", "26"],   # People & Blogs, Howto & Style
    "educacao":      ["27"],
    "default":       ["22", "24"],
}

# Regiões por idioma
REGION_MAP = {
    "pt-BR": "BR",
    "pt-PT": "PT",
    "en":    "US",
    "es":    "MX",
}


class YouTubeScraper:
    BASE = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self._client: Optional[httpx.AsyncClient] = None

    def _params(self, **extra) -> dict:
        return {"key": self.api_key, **extra}

    async def _get(self, endpoint: str, **params) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                f"{self.BASE}/{endpoint}",
                params=self._params(**params),
            )
            r.raise_for_status()
            return r.json()

    # ------------------------------------------------------------------
    # Método principal: busca vídeos virais por nicho
    # ------------------------------------------------------------------
    async def search_viral(
        self,
        niche: str,
        language: str = "pt-BR",
        days_back: int = 30,
        max_results: int = 25,
    ) -> list[dict]:
        """Busca vídeos virais de um nicho. Retorna lista de ScrapedContent dicts."""
        if not self.api_key:
            return []

        region = REGION_MAP.get(language, "BR")
        published_after = (
            datetime.now(timezone.utc) - timedelta(days=days_back)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Busca por query
        try:
            search_data = await self._get(
                "search",
                part="snippet",
                q=niche,
                order="viewCount",
                type="video",
                regionCode=region,
                relevanceLanguage=language[:2],
                publishedAfter=published_after,
                videoDuration="short",   # Shorts e vídeos curtos
                maxResults=max_results,
            )
        except Exception as e:
            print(f"[YouTubeScraper] search error: {e}")
            return []

        video_ids = [
            item["id"]["videoId"]
            for item in search_data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            return []

        # Busca estatísticas detalhadas (custa só 1 unidade por vídeo)
        return await self._enrich_videos(video_ids, niche)

    async def get_most_popular(
        self,
        niche: str,
        language: str = "pt-BR",
        max_results: int = 50,
    ) -> list[dict]:
        """Busca os vídeos mais populares do momento por categoria."""
        if not self.api_key:
            return []

        region = REGION_MAP.get(language, "BR")
        categories = NICHE_CATEGORIES.get(niche.lower(), NICHE_CATEGORIES["default"])

        all_videos = []
        for category_id in categories[:2]:  # Máx 2 categorias por chamada
            try:
                data = await self._get(
                    "videos",
                    part="snippet,statistics,contentDetails",
                    chart="mostPopular",
                    regionCode=region,
                    videoCategoryId=category_id,
                    maxResults=max_results // len(categories),
                )
                items = data.get("items", [])
                all_videos.extend(self._parse_video_items(items, niche))
            except Exception as e:
                print(f"[YouTubeScraper] mostPopular error (cat {category_id}): {e}")

        return all_videos

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    async def _enrich_videos(self, video_ids: list[str], niche: str) -> list[dict]:
        """Busca estatísticas detalhadas de uma lista de IDs."""
        ids_str = ",".join(video_ids)
        try:
            data = await self._get(
                "videos",
                part="snippet,statistics,contentDetails",
                id=ids_str,
            )
        except Exception as e:
            print(f"[YouTubeScraper] enrich error: {e}")
            return []

        return self._parse_video_items(data.get("items", []), niche)

    def _parse_video_items(self, items: list, niche: str) -> list[dict]:
        """Converte resposta da API no formato ScrapedContent."""
        results = []
        for item in items:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            # Converte duração ISO 8601 para segundos
            duration_sec = self._iso_duration_to_seconds(
                content.get("duration", "PT0S")
            )

            # Só coleta vídeos curtos (até 3 min) ou muito virais
            view_count = int(stats.get("viewCount", 0))
            if duration_sec > 180 and view_count < 500_000:
                continue  # Filtra vídeos longos sem tração

            results.append({
                "platform": "youtube",
                "external_id": item.get("id", ""),
                "niche": niche,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:500],
                "tags": json.dumps(snippet.get("tags", [])[:20]),
                "view_count": view_count,
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "share_count": 0,  # YouTube API não expõe shares
                "duration_seconds": duration_sec,
                "published_at": snippet.get("publishedAt", ""),
                "raw_json": json.dumps(item),
            })

        # Ordena por views (os melhores primeiro)
        results.sort(key=lambda x: x["view_count"], reverse=True)
        return results

    @staticmethod
    def _iso_duration_to_seconds(iso: str) -> int:
        """PT1H2M3S → 3723"""
        import re
        match = re.match(
            r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso
        )
        if not match:
            return 0
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        return h * 3600 + m * 60 + s

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def quota_estimate(self, searches: int = 1, videos: int = 25) -> int:
        """Estima uso de quota: 100/search + 1/video."""
        return searches * 100 + videos


youtube_scraper = YouTubeScraper()
