#!/bin/bash
echo "🧠 CIS — Content Intelligence System — Setup"
echo ""

# Python deps
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt

# Community skills (opcional)
echo ""
echo "📚 Skills da comunidade (opcional):"
echo "  1. Remotion (vídeo programático):"
echo "     npx skills add remotion-dev/skills"
echo ""
echo "  2. Antigravity Awesome Skills (1340+ skills):"
echo "     npx antigravity-awesome-skills --claude"
echo ""
echo "  3. Claude Image Gen (Gemini):"
echo "     /plugin marketplace add guinacio/claude-image-gen"
echo ""
echo "  4. Video Toolkit:"
echo "     git clone https://github.com/digitalsamba/claude-code-video-toolkit.git"
echo ""
echo "  5. claude-skills (220+ skills):"
echo "     git clone https://github.com/alirezarezvani/claude-skills"
echo ""

# Env vars
echo "🔑 Configure variáveis de ambiente:"
echo "  export ANTHROPIC_API_KEY='sua-chave-claude'"
echo "  export TELEGRAM_BOT_TOKEN='seu-token-telegram'"
echo "  export YOUTUBE_API_KEY='sua-chave-youtube'  # Google Cloud Console → YouTube Data API v3"
echo "  export HF_API_KEY='sua-chave-higgsfield'"
echo "  export HF_API_SECRET='seu-secret-higgsfield'"
echo "  export GEMINI_API_KEY='sua-chave-gemini' (opcional)"
echo ""

echo "✅ Pronto! Execute: python main.py"
