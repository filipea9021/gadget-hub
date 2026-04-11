---
name: cis-content-intelligence
description: Pesquisa, análise, repurposing e escrita de conteúdo para o CIS. Integra Content Repurposing (YouTube → multiplataforma), Content Research Writer (pesquisa + citações + hooks), e Twitter Algorithm Optimizer (otimização para X/Twitter). Trigger quando o pipeline precisar pesquisar conteúdo viral, reescrever conteúdo para múltiplas plataformas, melhorar hooks, adicionar citações, otimizar tweets/threads, ou transformar um vídeo/artigo em posts para várias redes. Também trigger para "repurpose", "repost", "adaptar conteúdo", "transformar vídeo em post", "otimizar tweet", "thread", "carrossel".
---

# CIS Content Intelligence Skill

Skill de inteligência de conteúdo que combina pesquisa, escrita e repurposing.

## Ferramentas Integradas

### 1. Content Repurposing (MindStudio Agent Skills)
- **O que faz**: Transforma vídeo do YouTube em conteúdo pronto para 3+ plataformas
- **Instalação**: `npm install @mindstudio-ai/agent youtube-transcript`
- **Pipeline**:
  1. Fetch transcript do YouTube
  2. Extrai insights-chave
  3. Gera conteúdo específico por plataforma:
     - LinkedIn: post profissional com insights
     - Instagram: caption + hashtags + visual suggestion
     - X/Twitter: thread ou tweet otimizado
  4. Gera imagem/visual de acompanhamento
- **Quando usar**: Qualquer URL de vídeo/podcast que precisa virar conteúdo multiplataforma

### 2. Content Research Writer
- **Fonte**: ComposioHQ/awesome-claude-skills
- **O que faz**: Escrita de conteúdo de alta qualidade com pesquisa
- **Capacidades**:
  - Pesquisa aprofundada sobre o tema
  - Adição de citações e fontes
  - Melhoria de hooks de abertura
  - Feedback seção por seção
  - Estruturação de argumentos
- **Quando usar**: Criação de conteúdo longo, artigos, scripts que precisam de base factual

### 3. Twitter/X Algorithm Optimizer
- **Fonte**: ComposioHQ/awesome-claude-skills
- **O que faz**: Otimiza conteúdo para máximo alcance no X/Twitter
- **Capacidades**:
  - Análise baseada no algoritmo open-source do Twitter
  - Rewrite de tweets para melhor engagement
  - Otimização de timing, formato, hashtags
  - Análise de threads vs tweet único
  - Scoring de potencial viral
- **Quando usar**: Qualquer conteúdo destinado ao X/Twitter

## Pipeline de Conteúdo

```
Input (URL, tema, ou conteúdo existente)
    ↓
Pesquisa (Content Research Writer):
├── Busca referências e dados
├── Extrai insights-chave
└── Constrói base factual
    ↓
Criação por plataforma:
├── YouTube → Script longo com hooks + CTA (ScriptWriter do CIS)
├── TikTok/Reels → Script curto, gancho nos 3 primeiros segundos
├── LinkedIn → Post profissional com insights (Content Repurposing)
├── Instagram → Caption + visual + carrossel (Content Repurposing)
├── X/Twitter → Tweet/Thread otimizado (Twitter Algorithm Optimizer)
└── Blog → Artigo longo com citações (Content Research Writer)
    ↓
Validação e otimização final
```

## Formatos de Saída por Plataforma

| Plataforma | Formato | Limite | Tom |
|------------|---------|--------|-----|
| YouTube | Script completo | 8-15 min | Educativo/Engajante |
| TikTok | Script curto | 15-60s | Rápido/Impactante |
| Instagram | Caption + CTA | 2200 chars | Visual/Inspiracional |
| LinkedIn | Post + doc carousel | 3000 chars | Profissional/Insight |
| X/Twitter | Tweet ou thread | 280/tweet | Conciso/Provocativo |
| Blog | Artigo SEO | 1500-3000 palavras | Informativo/Autoridade |

## Uso no CIS

Os módulos `modules/creation/` e `modules/optimization/` chamam esta skill.
O orchestrator roteia automaticamente baseado na plataforma-alvo do contexto.
