"""
config.py — Configurações do Content Automation Studio
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# === Anthropic (Claude) ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# === Serper (Pesquisa Web) ===
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# === Shopify — Gadget Hub ===
SHOPIFY_CONFIG = {
    "store_name":    os.getenv("SHOPIFY_STORE_NAME", "gadget-hub-72955"),
    "client_id":     os.getenv("SHOPIFY_CLIENT_ID", "f65ddca01e48a7f827ca3f3787d396a0"),
    "client_secret": os.getenv("SHOPIFY_CLIENT_SECRET", ""),
    "api_version":   os.getenv("SHOPIFY_API_VERSION", "2026-01"),
    "blog_id":       os.getenv("SHOPIFY_BLOG_ID", ""),
}

# === Instagram ===
INSTAGRAM_CONFIG = {
    "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
    "user_id":      os.getenv("INSTAGRAM_USER_ID", ""),
}

# === LinkedIn ===
LINKEDIN_CONFIG = {
    "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
    "author_urn":   os.getenv("LINKEDIN_AUTHOR_URN", ""),
}

# === Twitter/X ===
TWITTER_CONFIG = {
    "api_key":        os.getenv("TWITTER_API_KEY", ""),
    "api_secret":     os.getenv("TWITTER_API_SECRET", ""),
    "access_token":   os.getenv("TWITTER_ACCESS_TOKEN", ""),
    "access_secret":  os.getenv("TWITTER_ACCESS_SECRET", ""),
}

# === WordPress ===
WORDPRESS_CONFIG = {
    "url":      os.getenv("WORDPRESS_URL", ""),
    "user":     os.getenv("WORDPRESS_USER", ""),
    "password": os.getenv("WORDPRESS_PASSWORD", ""),
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

PLATFORM_LIMITS = {
    "instagram": 2200, "linkedin": 3000, "twitter": 280,
    "wordpress": 10000, "shopify": 50000,
}

PLATFORM_INSTRUCTIONS = {
    "instagram": "150-250 palavras + 10 hashtags relevantes + emojis estratégicos",
    "linkedin":  "200-400 palavras, formato profissional, parágrafos, 3-5 hashtags",
    "twitter":   "máximo 280 caracteres, impactante, 2-3 hashtags",
    "wordpress": "600-1000 palavras, estruturado com H2/H3, SEO otimizado, conclusão com CTA",
    "shopify":   "600-1200 palavras, HTML formatado, SEO otimizado, com tags de produto",
}

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "português")
DEFAULT_TONE     = os.getenv("DEFAULT_TONE", "engajante")
TIMEZONE         = os.getenv("TIMEZONE", "Europe/Lisbon")
LOG_DIR          = BASE_DIR / "logs"
DATA_DIR         = BASE_DIR / "data"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 1500
