---
name: cis-image-generation
description: Geração de imagens para o CIS. Integra claude-image-gen (Gemini), Higgsfield (Seedream/FLUX), e Canvas Design. Trigger quando o pipeline precisar gerar thumbnails, imagens para posts, capas, banners, artes visuais, infográficos, ou qualquer asset visual. Também trigger para "thumbnail", "imagem", "banner", "capa", "arte", "visual", "infográfico", "poster", "design".
---

# CIS Image Generation Skill

Skill de geração de imagens que combina múltiplos engines.

## Ferramentas Integradas

### 1. claude-image-gen (guinacio/claude-image-gen)
- **O que faz**: Gera imagens via Google Gemini
- **Instalação**: `/plugin marketplace add guinacio/claude-image-gen`
- **Capacidades**:
  - Text-to-image via Gemini
  - Múltiplos aspect ratios
  - Boa para imagens realistas e conceituais
  - CLI + MCP server
- **Quando usar**: Imagens conceituais, fotos estilizadas, assets genéricos

### 2. Higgsfield AI (integrado no CIS)
- **O que faz**: Geração via Seedream V4 e outros modelos
- **SDK**: `pip install higgsfield-client`
- **Capacidades**:
  - Text-to-image (Seedream V4, FLUX)
  - Image-to-video (70+ presets cinematográficos)
  - Resoluções até 2K
  - Aspect ratios customizáveis
- **Quando usar**: Thumbnails de alta qualidade, imagens para ads, base para vídeo

### 3. Canvas Design
- **Fonte**: ComposioHQ/awesome-claude-skills
- **O que faz**: Cria artes visuais em PNG/PDF com princípios de design
- **Capacidades**:
  - Posters e designs estáticos
  - Filosofia de design e princípios estéticos
  - Layouts profissionais
  - Infográficos
- **Quando usar**: Designs que precisam de layout preciso, infográficos, posters

## Pipeline de Geração de Imagens

```
Necessidade visual identificada
    ↓
Classificação do tipo:
├── Thumbnail YouTube → Higgsfield (alto impacto, texto bold)
├── Post Instagram → claude-image-gen (estético) ou Canvas Design (infográfico)
├── Banner/Capa → Higgsfield (2K, widescreen)
├── Infográfico → Canvas Design (layout preciso)
├── Asset para vídeo → Higgsfield (input para image-to-video)
└── Arte conceitual → claude-image-gen (flexível)
    ↓
Geração do prompt otimizado (via Claude)
    ↓
Geração da imagem
    ↓
Review de qualidade
```

## Specs de Thumbnail por Plataforma

| Plataforma | Resolução | Aspect Ratio | Notas |
|------------|-----------|--------------|-------|
| YouTube | 1280x720 | 16:9 | Texto grande, contraste alto, rosto |
| TikTok | 1080x1920 | 9:16 | Capa do vídeo, texto centralizado |
| Instagram | 1080x1080 | 1:1 | Clean, visual-first |
| LinkedIn | 1200x627 | ~1.91:1 | Profissional, dados |
| X/Twitter | 1200x675 | 16:9 | Impactante, poucas palavras |

## Uso no CIS

Chamada via `integrations/manager.py` quando `mode=produce` inclui imagem.
Também chamada pelo `seo_optimizer.py` para gerar texto de thumbnail.
