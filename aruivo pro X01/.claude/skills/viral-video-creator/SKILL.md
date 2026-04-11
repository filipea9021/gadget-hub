---
name: viral-video-creator
description: "Workflow completo para criar vídeos virais curtos gerados por IA (YouTube Shorts, TikTok, Reels). Use esta skill quando o usuário quiser criar um vídeo viral, short com IA, conteúdo animado para redes sociais, ou qualquer coisa envolvendo: transformar uma ideia em vídeo curto, gerar imagens cinematográficas com IA e animá-las, escrever roteiros otimizados para engajamento em Shorts/TikTok/Reels, ou produzir um documento completo de produção de vídeo. Também dispara com: 'vídeo viral', 'YouTube Short', 'vídeo TikTok', 'Reels', 'vídeo com IA', 'animar imagem', 'imagem para vídeo', 'vídeo a partir de prompt', 'criar vídeo viral', 'short viral', 'viral video', 'AI video', 'animate image', 'image to video'."
---

# Criador de Vídeos Virais

Crie vídeos curtos que param o scroll usando geração de imagens com IA + animação. Esta skill te guia pelo pipeline completo: de uma ideia bruta até um documento pronto para produção com prompts, roteiros, timing e estratégia de engajamento.

O insight central deste workflow é que shorts virais com IA seguem uma fórmula: visuais cinematográficos gerados por IA + ganchos de mistério/curiosidade + isca estratégica de engajamento. Canais como @airon_ia provam que isso funciona — eles mostram visuais impressionantes de IA com contexto suficiente para deixar os espectadores desesperados para saber o prompt.

## Quando Usar Esta Skill

- Usuário quer criar um YouTube Short, TikTok ou Reel viral usando IA
- Usuário quer gerar imagens cinematográficas com IA e animá-las em vídeo
- Usuário tem um projeto/marca e quer promovê-lo através de conteúdo curto com IA
- Usuário pede para criar um "vídeo com IA" ou quer replicar um estilo viral de conteúdo IA
- Usuário diz qualquer coisa sobre "criar vídeo", "fazer short", "vídeo viral", "animar essa imagem"

## Modo de Operação: Cloud vs Local

Esta skill suporta dois modos de operação:

**Modo Cloud (preferido — automação 100%):**
Quando o cloud storage está configurado (`CLOUD_PROVIDER` != `local`), todo o pipeline funciona sem intervenção manual. Imagens e vídeos são transferidos diretamente entre APIs e cloud storage, sem passar pelo computador local.

```python
from core.cloud_storage import get_storage_provider
from core.asset_manager import AssetManager

storage = get_storage_provider()
manager = AssetManager(storage)
project = await manager.create_project("meu_video")
# Tudo automático a partir daqui
```

**Modo Browser (fallback):**
Quando o cloud não está configurado, usa automação de browser (Claude in Chrome MCP) para interagir com as plataformas web. Limitação: o browser pode bloquear uploads de ficheiros locais por segurança. Nesse caso, o usuário faz upload manual e o Claude cuida do resto (prompts, configurações, geração).

Consultar `CLOUD_ARCHITECTURE.md` para detalhes da arquitetura cloud.

## O Pipeline

O workflow tem 7 estágios. Complete-os em ordem, mas adapte ao que o usuário já tem — se ele trouxer sua própria imagem, pule para o Estágio 4.

### Estágio 1: Análise de Referência

Antes de criar qualquer coisa, entenda como é o "viral" no nicho do usuário.

**O que fazer:**
- Pergunte ao usuário por um vídeo ou canal de referência que ele quer emular (se ainda não forneceu)
- Se fornecer uma URL, analise: duração, ritmo, estilo de texto sobreposto, mood da música, estrutura do gancho, posicionamento do CTA
- Se não houver referência disponível, use a fórmula do @airon_ia como padrão (funciona bem em vários nichos):
  - Duração de 20-30 segundos
  - Visuais cinematográficos com IA (um tema contínuo)
  - Texto sobreposto branco em negrito com sombra
  - Gancho de curiosidade nos primeiros 3 segundos
  - CTA no final pedindo para comentar pelo prompt
  - Prompt mostrado brevemente (2-3 frames) para provocar sem revelar

**Resultado:** Um modelo mental do estilo alvo. Não precisa de arquivo — isso informa tudo a seguir.

### Estágio 2: Tema e Narrativa

Conecte o vídeo a algo significativo — um projeto, marca, ideia ou estética.

**O que fazer:**
- Pergunte sobre o que é o vídeo ou o que está promovendo (se ainda não estiver claro)
- Identifique a metáfora visual central. As melhores mapeiam um conceito abstrato para um ambiente cinematográfico:
  - IA/tecnologia → deserto com fluxos de dados holográficos
  - Criatividade → cidade subaquática com arte bioluminescente
  - Crescimento → floresta onde as árvores são feitas de luz/código
  - Poder → cume de montanha com tempestades de energia
  - Mistério → templo abandonado com artefatos flutuantes
- A metáfora deve ser visualmente espetacular E emocionalmente ressonante

**Resultado:** Uma declaração clara do tema, ex.: "Paisagem desértica onde a IA transforma areia estéril em redes vivas de dados — representa o projeto CIS trazendo inteligência para conteúdo bruto."

### Estágio 3: Engenharia de Prompts de Imagem

Este é o coração da skill. Um bom prompt produz imagens que parecem frames de cinema.

**Estrutura do prompt (siga este padrão):**

```
[Sujeito/figura] + [ambiente com escala] + [iluminação/hora do dia] +
[o "elemento mágico" — o visual de IA/tech/fantasia] + [câmera/composição] +
[tags de qualidade]
```

**Regras para prompts eficazes:**
- Comece com o sujeito principal e sua ação ("A lone figure in a flowing dark cloak walks...")
- Construa o ambiente com escala massiva — use palavras como "endless", "vast", "towering", "monumental"
- Sempre especifique a iluminação: "golden hour", "dramatic sunset", "neon-lit night"
- O "elemento mágico" é o que torna viral — fluxos de dados brilhantes, estruturas holográficas, partículas de luz, formações cristalinas. Seja específico e vívido.
- Inclua indicações de composição: "camera follows from behind", "aerial drone shot", "shallow depth of field"
- Termine com tags de qualidade: "Cinematic 4K, ultra-realistic, dramatic lighting"
- Para Shorts/TikTok, sempre adicione "vertical 9:16 portrait" ao prompt

**NOTA:** Os prompts de imagem devem ser escritos em inglês, mesmo que o resto do documento esteja em português. Os modelos de IA respondem melhor a prompts em inglês.

**Crie 3 variantes de prompt:**
1. **Prompt principal** — o plano hero, máximo detalhe e qualidade cinematográfica
2. **Variante dinâmica** — mais movimento, ângulo de câmera diferente, mais energia
3. **Backup (curto)** — versão condensada para ferramentas com limite de caracteres

**Exemplo (tema deserto):**
```
A lone figure in a flowing dark cloak walks through an endless, vast golden
desert at sunset. Massive, ancient sand dunes rise like ocean waves around
them, their ridges razor-sharp against a burning orange and crimson sky.
Streams of glowing blue holographic data, code fragments, neural network
diagrams, and pulsing light particles emerge from the sand beneath their
feet and spiral upward into the sky like digital sandstorms. The wind
carries fine golden sand particles that catch the last rays of sunlight,
creating a shimmering veil of light. Cinematic 4K, ultra-realistic,
dramatic lighting, golden hour, vertical 9:16 portrait.
```

### Estágio 4: Geração de Imagem

Gere as imagens usando ferramentas de IA.

**Ferramentas recomendadas (em ordem de preferência):**

| Ferramenta | Modelo | Custo | Melhor Para |
|------------|--------|-------|-------------|
| Upsampler (upsampler.com) | Nano Banana 2 | Créditos | Alta qualidade, interface boa |
| Higgsfield (higgsfield.ai) | Nano Banana 2 / Pro | Tier gratuito disponível | Imagens cinematográficas |
| Leonardo.ai | Vários | Tier gratuito | Estilo consistente, bom detalhe |
| Ideogram | Ideogram 2.0 | Tier gratuito | Renderização de texto em imagens |

**Configurações de geração:**
- **Proporção:** Sempre 9:16 (vertical) para Shorts/TikTok/Reels
- **Resolução:** A mais alta disponível (1080x1920 ideal)
- **Gere 4+ variações** e escolha a melhor
- Procure por: sensação cinematográfica, boa iluminação, sujeito claro, fator "uau"

#### Modo Cloud (quando configurado):
```python
# Gera imagem via API e guarda diretamente no cloud
from core.asset_manager import AssetManager

asset = await manager.store_image_from_url(
    project_id=project.project_id,
    source_url=api_response.image_url,  # URL retornada pela API
    scene="cena_1",
    prompt=prompt_usado,
    model="nano_banana_2"
)
# Imagem já está no cloud, acessível por asset.cloud_url
```

#### Modo Browser (fallback):
1. Acesse a plataforma (Upsampler, Higgsfield, etc.) via Chrome
2. Cole o prompt, defina proporção para 9:16
3. Gere e faça download do resultado
4. Se o download automático falhar, peça ao usuário para baixar manualmente

### Estágio 5: Animação Imagem-para-Vídeo

Anime a imagem estática em um clipe de vídeo.

**Modo Cloud:** Usa APIs diretas — a imagem é passada por URL do cloud, o vídeo gerado é guardado de volta no cloud. Automação 100%.

**Modo Browser (fallback):** Usa automação de browser (Claude in Chrome MCP) para fazer upload das imagens e gerar os vídeos.

**Escreva um prompt de animação** que descreva o movimento desejado:
```
[descrever movimento do sujeito] + [efeitos ambientais] + [movimento de câmera] + [iluminação]
```

**Exemplo:**
```
The cloaked figure walks slowly forward through the golden desert. Wind blows
sand particles and the dark cloak billows dramatically. Glowing blue holographic
data streams spiral upward from the sand, pulsing with light. Camera slowly
pushes in with a cinematic dolly movement. Golden hour lighting with dramatic shadows.
```

**NOTA:** Prompts de animação devem ser escritos em inglês para melhor resultado nos modelos de IA.

#### Modo Cloud — Animação via API (preferido)

Quando o cloud storage está ativo, a animação é feita via APIs diretas:

```python
# 1. Obter URL da imagem no cloud
images = await manager.get_all_images(project_id)
image_url = await storage.get_url(images[0].cloud_path)

# 2. Chamar API de animação (ex: Kling API)
# A imagem é passada por URL — sem download/upload local
video_result = await kling_api.image_to_video(
    image_url=image_url,
    prompt=animation_prompt,
    duration=5,
    aspect_ratio="9:16"
)

# 3. Guardar vídeo de volta no cloud
await manager.store_video_from_url(
    project_id=project_id,
    source_url=video_result.video_url,
    scene="cena_1",
    animation_prompt=animation_prompt,
    model="kling_v3"
)
```

**Fluxo para 5 cenas:**
```
Para cada cena no manifest:
  1. Ler cloud_url da imagem
  2. Chamar API com imagem URL + prompt de animação
  3. Guardar vídeo resultante no cloud
  4. Atualizar manifest
→ Resultado: 5 clips de 5s prontos no cloud
```

#### Ferramentas de Animação (ordem de preferência)

| Ferramenta | URL | Tier Grátis | Melhor Para |
|------------|-----|-------------|-------------|
| **Kling AI** | klingai.com | Sim (5s clips) | Resultados cinematográficos, melhor qualidade |
| **Hailuo AI** | hailuoai.video | Sim | Boa qualidade geral, rápido |
| Pika | pika.art | Sim | Clips curtos, movimentos sutis |
| Luma Dream Machine | lumalabs.ai/dream-machine | Sim | Alternativa rápida |
| Higgsfield | higgsfield.ai | Pode precisar créditos | Alta qualidade |

#### Automação: Kling AI (Preferido)

Use as ferramentas de browser (Claude in Chrome MCP) para automatizar o processo:

**Pré-requisitos:**
- O usuário precisa estar logado em klingai.com
- As imagens geradas no Estágio 4 devem estar baixadas no computador do usuário

**Fluxo de automação:**

1. **Abrir o Kling AI:**
   ```
   - Usar tabs_context_mcp para obter/criar uma tab
   - Navegar para: https://klingai.com/image-to-video
   - Esperar a página carregar (wait 3s)
   - Tirar screenshot para verificar se está logado
   - Se não logado, avisar o usuário para fazer login manualmente
   ```

2. **Upload da imagem:**
   ```
   - Usar find para localizar o botão de upload ou área de drag-and-drop
   - Localizar o input de arquivo (type="file") com find ou read_page
   - Usar file_upload com o ref do input e o caminho da imagem
     Exemplo: file_upload(paths=["/Users/.../Downloads/imagem.png"], ref="ref_XX", tabId=XXX)
   - Esperar o upload completar (wait 3s)
   - Tirar screenshot para confirmar
   ```

3. **Inserir o prompt de animação:**
   ```
   - Usar find para localizar o campo de prompt/descrição
   - Usar form_input para inserir o prompt de animação em inglês
   - Verificar com screenshot
   ```

4. **Configurar e gerar:**
   ```
   - Verificar configurações (duração: 5s, modo: standard/professional)
   - Usar find para localizar o botão "Generate" / "Create" / "Gerar"
   - Clicar no botão com computer(action="left_click", ref=...)
   - Esperar geração (pode levar 1-5 minutos)
   - Fazer polling com screenshots a cada 30s até o vídeo aparecer
   ```

5. **Download do vídeo:**
   ```
   - Quando o vídeo estiver pronto, localizar botão de download
   - Clicar para baixar
   - Confirmar download com o usuário
   ```

6. **Repetir para cada cena:**
   ```
   - Para cada imagem do roteiro, repetir os passos 2-5
   - Usar o prompt de animação correspondente a cada cena
   ```

**IMPORTANTE — Limitações do browser:**
- Chrome é concedido no tier "read" para computer-use — use Claude in Chrome MCP para todas as interações
- Se o site mudar de layout, adapte usando `find` e `read_page` para localizar elementos
- Se o upload falhar via `file_upload`, peça ao usuário para fazer upload manualmente e continue com o prompt
- Sempre peça confirmação do usuário antes de clicar em botões que consomem créditos

#### Automação: Hailuo AI (Alternativa)

**Fluxo de automação:**

1. **Abrir o Hailuo AI:**
   ```
   - Navegar para: https://hailuoai.video/create
   - Esperar a página carregar
   - Verificar login com screenshot
   ```

2. **Selecionar modo Image-to-Video:**
   ```
   - Usar find para localizar "Image to Video" ou "Imagem para Vídeo"
   - Clicar para selecionar o modo
   ```

3. **Upload e prompt:**
   ```
   - Localizar input de arquivo e usar file_upload
   - Localizar campo de prompt e usar form_input
   - Inserir o prompt de animação em inglês
   ```

4. **Gerar e baixar:**
   ```
   - Localizar e clicar no botão de geração
   - Esperar conclusão (polling com screenshots)
   - Baixar o vídeo resultante
   ```

#### Automação: Upsampler (Se já estiver na plataforma)

Se o usuário já estiver usando o Upsampler (upsampler.com) para geração de imagens, verifique se a plataforma oferece image-to-video:

```
- Navegar para: https://upsampler.com/dashboard/tools/video/generate
- Se existir, usar o mesmo fluxo: upload da imagem + prompt + gerar
- Vantagem: o usuário já está logado e tem créditos
```

#### Fluxo Manual (Fallback)

Se a automação falhar por qualquer motivo (site mudou, CAPTCHA, erro de upload), forneça instruções claras para o usuário fazer manualmente:

1. Abrir [klingai.com/image-to-video](https://klingai.com/image-to-video) (ou hailuoai.video)
2. Fazer upload da imagem da cena
3. Colar o prompt de animação (já estará no documento de produção)
4. Selecionar duração de 5 segundos
5. Clicar em "Generate"
6. Baixar quando pronto
7. Repetir para cada cena

**Dicas de animação:**
- Gere clips de 4-6 segundos para cada imagem/cena
- Mantenha a animação sutil e cinematográfica — dolly lento, parallax suave
- Evite movimento excessivo; deixe os visuais respirarem
- Você combinará os clips na pós-produção
- Se uma animação não ficar boa, regere com um prompt ligeiramente diferente

### Estágio 6: Roteiro e Timing

Escreva o roteiro do vídeo com timing preciso, textos sobrepostos e narração.

**Estrutura para um Short de 26 segundos:**

| Tempo | Visual | Texto na Tela |
|-------|--------|---------------|
| 0-3s | Gancho de abertura — visual mais impressionante | Pergunta de curiosidade que para o scroll |
| 3-8s | Revelação do sujeito principal | Frase curta e impactante |
| 8-14s | A "mágica" acontecendo | O que faz (construindo intriga) |
| 14-20s | Revelação de escala/poder | A capacidade impressionante |
| 20-24s | Clímax — explosão visual ou transformação | A frase de impacto |
| 24-26s | Logo/canal + CTA | "Quer o prompt? Comenta [emoji]" |

**Fórmula do gancho (os primeiros 3 segundos são tudo):**
- "E se [coisa impossível] fosse real?"
- "Você não vai acreditar no que [ferramenta] acabou de criar..."
- "Isso foi feito inteiramente por IA em [tempo curto]..."
- "O que acontece quando [conceito] encontra [IA]?"

**Estilo do texto sobreposto:**
- Fonte: Bold, sans-serif, branca com sombra/contorno escuro
- Posição: Centro ou terço inferior
- Animação: Fade in, ou pop com leve escala
- Máximo de 5-8 palavras por texto sobreposto

**Narração opcional:**
Escreva um roteiro de voiceover de 15-20 segundos que conte uma mini-história. Use frases curtas e impactantes. Construa tensão. Termine com o nome do projeto/marca.

### Estágio 7: Estratégia de Engajamento e Documento de Produção

Empacote tudo em um documento completo de produção.

**Táticas de engajamento que geram comentários:**
- Mostre o prompt da IA brevemente (2-3 frames) — espectadores pausam para ler mas não conseguem captar tudo
- Nunca coloque o prompt completo na descrição — force as pessoas a comentar "quero o prompt"
- CTA final: "Quer o prompt? Comenta [PALAVRA-CHAVE] [emoji]" — a palavra-chave deve se relacionar ao tema do vídeo
- Fixe um comentário que diga "Comenta [PALAVRA-CHAVE] que eu mando o prompt no privado"

**Estratégia de hashtags:**
- Misture amplas + nicho: #ia #inteligenciaartificial #aiart #[tema] #[ferramenta usada] #[nome do projeto]
- 5-8 hashtags no total, não mais

**O documento de produção deve conter:**
1. Todas as variantes de prompt (principal, dinâmica, backup)
2. O roteiro completo com tabela de timing
3. Texto de narração
4. Estratégia de engajamento (CTA, hashtags, estratégia de comentários)
5. Notas de pós-produção (estilo de música, fonte, transições, specs de formato)
6. Links para as ferramentas usadas

Salve o documento como `PROMPT_VIDEO_[TEMA].md` no workspace do usuário.

## Checklist de Pós-Produção

Antes de publicar, garanta que:
- [ ] Vídeo está em formato vertical 9:16 (1080x1920)
- [ ] Duração é de 20-30 segundos
- [ ] Gancho nos primeiros 3 segundos prende a atenção
- [ ] Textos sobrepostos são legíveis e bem cronometrados
- [ ] Música combina com o mood (lo-fi épico, ambient cinematográfico ou orquestral dramático)
- [ ] CTA é claro e específico
- [ ] Prompt é mostrado brevemente mas não é totalmente legível
- [ ] Thumbnail (se necessário) é o frame mais impactante

## Recomendações de Música

- **Épico/Cinematográfico:** Pesquise "royalty free cinematic ambient" na YouTube Audio Library
- **Lo-fi:** Pesquise "lo-fi epic" ou "lo-fi cinematic"
- **Dramático:** Pesquise "dramatic orchestral royalty free"
- Use a biblioteca de música do CapCut para acesso rápido a sons em alta

## Recomendações de Editor (Grátis)

- **CapCut** — melhor para Shorts/TikTok, tem templates, legendas automáticas, efeitos trending
- **DaVinci Resolve** — nível profissional, grátis, mais controle
- **InShot** — amigável para mobile, edições rápidas
- **VN Video Editor** — mobile, boa edição de timeline

## Nota de Idioma

Esta skill funciona em português (pt-BR) e inglês. Adapte todos os textos sobrepostos, CTAs e hashtags ao idioma do usuário. Os prompts de geração de imagem e animação devem sempre ser escritos em inglês para melhor resultado nos modelos de IA. O restante do documento de produção deve acompanhar o idioma do usuário.
