"""
CIS - Content Intelligence System
Configuração central do projeto
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ClaudeConfig:
    api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

@dataclass
class TelegramConfig:
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    allowed_users: list = field(default_factory=list)

@dataclass
class ScraperConfig:
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    scrape_interval_hours: int = 24    # frequência do scraping autônomo
    max_results_per_search: int = 25
    cache_ttl_hours: int = 24

@dataclass
class IntegrationSlot:
    """Slot genérico para APIs externas de IA (imagem, vídeo, áudio, etc.)"""
    name: str
    api_key: str = ""
    base_url: str = ""
    enabled: bool = False
    category: str = "general"  # image, video, audio, general

@dataclass
class CloudConfig:
    """Configuração do cloud storage para assets (imagens, vídeos, áudio)."""
    provider: str = os.getenv("CLOUD_PROVIDER", "local")  # local, google_drive, supabase, cloudflare_r2
    base_path: str = "/cis-assets"

    # Google Drive
    google_drive_folder_id: str = os.getenv("GDRIVE_FOLDER_ID", "")

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    supabase_bucket: str = os.getenv("SUPABASE_BUCKET", "cis-assets")

    # Cloudflare R2
    r2_account_id: str = os.getenv("R2_ACCOUNT_ID", "")
    r2_access_key: str = os.getenv("R2_ACCESS_KEY_ID", "")
    r2_secret_key: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    r2_bucket: str = os.getenv("R2_BUCKET", "cis-assets")

    # Local (fallback para dev)
    local_root: str = os.getenv("CLOUD_LOCAL_ROOT", "./cis-assets")

    def to_provider_config(self) -> dict:
        """Retorna config formatada para o provider selecionado."""
        base = {"base_path": self.base_path}
        if self.provider == "google_drive":
            return {**base, "folder_id": self.google_drive_folder_id}
        elif self.provider == "supabase":
            return {**base, "supabase_url": self.supabase_url,
                    "service_key": self.supabase_service_key,
                    "bucket": self.supabase_bucket}
        elif self.provider == "cloudflare_r2":
            return {**base, "account_id": self.r2_account_id,
                    "access_key": self.r2_access_key,
                    "secret_key": self.r2_secret_key,
                    "bucket": self.r2_bucket}
        else:  # local
            return {**base, "root_dir": self.local_root}


@dataclass
class VideoAPIConfig:
    """Configuração das APIs de geração de vídeo (acesso direto, sem browser)."""
    kling_api_key: str = os.getenv("KLING_API_KEY", "")
    kling_api_secret: str = os.getenv("KLING_API_SECRET", "")
    hailuo_api_key: str = os.getenv("HAILUO_API_KEY", "")
    upsampler_api_key: str = os.getenv("UPSAMPLER_API_KEY", "")
    higgsfield_api_key: str = os.getenv("HF_API_KEY", "")
    higgsfield_api_secret: str = os.getenv("HF_API_SECRET", "")


@dataclass
class CISConfig:
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    cloud: CloudConfig = field(default_factory=CloudConfig)
    video_apis: VideoAPIConfig = field(default_factory=VideoAPIConfig)
    db_path: str = "memory/cis_memory.db"

    # Slots para integrações externas — adicionar conforme necessário
    integrations: dict = field(default_factory=lambda: {
        # Exemplos de slots prontos para ativar:
        # "runway": IntegrationSlot("Runway", category="video"),
        # "midjourney": IntegrationSlot("Midjourney", category="image"),
        # "elevenlabs": IntegrationSlot("ElevenLabs", category="audio"),
        # "leonardo": IntegrationSlot("Leonardo AI", category="image"),
        # "pika": IntegrationSlot("Pika", category="video"),
        # "kling": IntegrationSlot("Kling AI", category="video"),
        # "suno": IntegrationSlot("Suno", category="audio"),
    })

    def add_integration(self, key: str, name: str, api_key: str, base_url: str = "", category: str = "general"):
        self.integrations[key] = IntegrationSlot(
            name=name, api_key=api_key, base_url=base_url, 
            enabled=True, category=category
        )

    def get_active_integrations(self, category: Optional[str] = None):
        active = {k: v for k, v in self.integrations.items() if v.enabled}
        if category:
            active = {k: v for k, v in active.items() if v.category == category}
        return active


config = CISConfig()
