---
name: cis-skill-library
description: Biblioteca de skills da comunidade integrada ao CIS. Conecta com antigravity-awesome-skills (1340+), alirezarezvani/claude-skills (220+), e AI Agent Social Media Manager (17 skills autônomas). Trigger quando precisar buscar uma skill específica da comunidade, instalar nova capacidade, ou quando nenhuma skill existente do CIS cobrir o caso de uso. Também trigger para "instalar skill", "buscar skill", "preciso de uma skill para", "tem alguma skill que", "automação social media".
---

# CIS Skill Library

Conexão com as maiores bibliotecas de skills da comunidade.

## Bibliotecas Conectadas

### 1. Antigravity Awesome Skills (sickn33/antigravity-awesome-skills)
- **Skills**: 1.340+
- **Instalação**: `npx antigravity-awesome-skills --claude`
- **Categorias relevantes pro CIS**:
  - brainstorming — ideação de features e conteúdo
  - content-creator — criação de conteúdo
  - seo workflows — otimização para busca
  - social media — distribuição
  - prompt-engineering — otimização de prompts internos
- **GitHub**: https://github.com/sickn33/antigravity-awesome-skills

### 2. alirezarezvani/claude-skills
- **Skills**: 220+ com 332 scripts Python (zero deps)
- **Instalação**: `git clone https://github.com/alirezarezvani/claude-skills`
- **Destaques pro CIS**:
  - content-creator — blog posts, artigos, SEO
  - social-media-manager — gestão de redes
  - copywriting — copy de vendas, ads
  - brand-voice — consistência de tom/voz
- **GitHub**: https://github.com/alirezarezvani/claude-skills

### 3. AI Agent Social Media Manager (referência arquitetural)
- **Skills**: 17 especializadas em produção autônoma
- **Arquitetura**:
  - Pipeline: input bruto → conteúdo pronto → publicação
  - Usa Remotion (vídeo) + Key.ai (imagem/vídeo) + Cernio (publicação)
  - 100% autônomo: prompt → conteúdo publicado sem intervenção
- **Relevância**: Modelo de referência para o CIS atingir automação total
- **Capacidades-chave**:
  - Pesquisa web → script → voiceover → vídeo → thumbnail → publicação
  - Infográficos LinkedIn via HTML render
  - Carrosseis multi-slide
  - Upload direto para YouTube, Instagram, TikTok, LinkedIn, X

## Como Buscar Skills

```python
# Via antigravity (CLI)
npx antigravity-awesome-skills search "content creation"
npx antigravity-awesome-skills search "video production"
npx antigravity-awesome-skills search "social media"

# Via alirezarezvani (scripts Python)
python scripts/search.py --query "seo"
python scripts/search.py --category marketing
```

## Roadmap de Integração com CIS

### Fase 1 (Atual)
- Skills do CIS como wrappers que referenciam ferramentas da comunidade
- Orchestrator roteia para skills corretas baseado no contexto

### Fase 2 (Próxima)
- Instalação automática de skills da comunidade sob demanda
- Skill resolver: quando o CIS não tem capacidade, busca na biblioteca

### Fase 3 (Futuro)
- Sistema de publicação automática (inspirado no AI Agent Social Media Manager)
- Integração com Cernio/Later para posting direto
- Loop de aprendizado: métricas de performance → ajuste de skills
