---
name: cis-video-production
description: Produção completa de vídeo para o CIS. Usa Remotion (vídeo programático via React), claude-code-video-toolkit (voiceover, música, SFX), e AI Video Generator (Sora/Veo). Trigger sempre que o pipeline precisar produzir vídeo, criar animações, gerar voiceover, adicionar música, editar vídeo, ou qualquer tarefa de produção audiovisual. Também trigger quando o usuário mencionar "vídeo", "reels", "shorts", "TikTok", "animação", "voiceover", "narração", ou "editar vídeo".
---

# CIS Video Production Skill

Skill de produção de vídeo que integra 3 ferramentas da comunidade num pipeline unificado.

## Ferramentas Integradas

### 1. Remotion (remotion-dev/skills)
- **O que faz**: Cria vídeos programaticamente usando React
- **Instalação**: `npx skills add remotion-dev/skills`
- **Quando usar**: Vídeos educacionais, explainers, product demos, ads animados
- **Capacidades**:
  - Composições React renderizadas como vídeo
  - Motion graphics, SVG animado, texto animado
  - Safe zones pra plataformas (TikTok, Reels, Shorts)
  - Preview local em localhost:3003
  - Render em qualquer resolução/FPS

### 2. Claude Code Video Toolkit (digitalsamba/claude-code-video-toolkit)
- **O que faz**: Toolkit completo de produção com voiceover, música e SFX
- **Instalação**: `git clone https://github.com/digitalsamba/claude-code-video-toolkit.git`
- **Quando usar**: Adicionar voz, música, efeitos sonoros ao vídeo
- **Capacidades**:
  - Voiceover via Qwen3-TTS (self-hosted, gratuito) ou ElevenLabs
  - Música via ACE-Step (gratuito) ou ElevenLabs
  - Sound effects gerados
  - Redub de vídeo existente
  - Setup completo de cloud GPU

### 3. AI Video Generator (mcpmarket.com)
- **O que faz**: Geração de vídeo cinematográfico via modelos de IA
- **Quando usar**: Vídeos realistas, cinematográficos, não-animados
- **Capacidades**:
  - Google Veo 3.1
  - OpenAI Sora 2 Pro
  - Controle de câmera, VFX, estilo

## Pipeline de Produção

```
Roteiro (do ScriptWriter)
    ↓
Decisão de formato:
├── Animação/Explainer → Remotion
├── Cinematográfico/Realista → AI Video Generator + Higgsfield
└── Qualquer formato → Pode combinar ambos
    ↓
Adicionar áudio (Video Toolkit):
├── Voiceover (Qwen3-TTS ou ElevenLabs)
├── Background music (ACE-Step)
└── SFX
    ↓
Render final
    ↓
Otimização por plataforma (resolução, safe zones, duração)
```

## Configuração de Safe Zones por Plataforma

- **TikTok/Reels/Shorts (9:16)**: Top 150px, Bottom 170px, Sides 60px
- **YouTube (16:9)**: Margens padrão
- **Font mínima mobile**: Headlines 56px+, body 36px+, labels 28px+

## Uso no CIS

O orchestrator chama esta skill quando `mode=produce` e o tipo inclui vídeo.
O módulo `integrations/video_producer.py` implementa a lógica de roteamento.

### Referências
- `references/remotion-guide.md` — Melhores práticas do Remotion
- `references/video-toolkit-commands.md` — Comandos do toolkit
- `references/platform-specs.md` — Specs por plataforma (resolução, duração, formato)
