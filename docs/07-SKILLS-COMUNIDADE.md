# GADGET HUB — Skills da Comunidade para Claude

> Guia de skills especializadas para potenciar o projeto Gadget Hub
> Última atualização: 6 de abril de 2026

---

## Resumo

As skills da comunidade são pacotes de instruções especializadas que tornam o Claude muito mais eficaz em tarefas específicas. Abaixo está o mapeamento completo de skills recomendadas para cada área do Gadget Hub.

---

## Pacotes de Skills Recomendados

### 1. Marketing Skills (Corey Haines) — 35+ skills

**Repositório:** `coreyhaines31/marketingskills`
**Instalação Claude Code:** `npx skills add coreyhaines31/marketingskills`

| Skill | Descrição | Uso no Gadget Hub |
|-------|-----------|-------------------|
| `copywriting` | Escrita persuasiva para vendas | Descrições de produto, landing pages |
| `seo-audit` | Auditoria SEO completa | Auditar páginas da loja |
| `page-cro` | Otimização de conversão de páginas | Melhorar taxa de conversão da loja |
| `email-sequence` | Sequências de email marketing | Welcome series, abandoned cart |
| `social-media` | Estratégia redes sociais | Posts Instagram, Facebook, TikTok |
| `ad-creative` | Criação de anúncios | Copy Google Ads, Facebook Ads |
| `analytics-tracking` | Configuração de analytics | GA4, eventos de e-commerce |
| `launch` | Lançamento de produtos | Estratégia de lançamento da loja |
| `pricing` | Estratégia de preços | Definir markup, promoções |
| `signup-cro` | Otimização de inscrições | Newsletter, conta de cliente |
| `form-cro` | Otimização de formulários | Checkout, contacto |

---

### 2. SEO & GEO Skills (Aaron He Zhu) — 20 skills

**Repositório:** `aaron-he-zhu/seo-geo-claude-skills`
**Instalação Claude Code:** `npx skills add aaron-he-zhu/seo-geo-claude-skills`

| Skill | Descrição | Uso no Gadget Hub |
|-------|-----------|-------------------|
| `keyword-research` | Pesquisa de palavras-chave | Keywords PT para produtos e blog |
| `content-writing` | Escrita de conteúdo SEO | Blog posts, descrições de produto |
| `technical-seo-audit` | Auditoria SEO técnica | Velocidade, schema, sitemap |
| `schema-markup` | Schema markup JSON-LD | Product, Organization, FAQ |
| `competitor-analysis` | Análise de concorrência SEO | Comparar com PCDiga, Worten |

**Framework incluído:** CORE-EEAT (Content, Optimization, Relevance, Experience, Expertise, Authority, Trust)

---

### 3. Claude SEO (AgriciDaniel) — 19 sub-skills

**Repositório:** `AgriciDaniel/claude-seo`
**Instalação:**
```bash
git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git
bash claude-seo/install.sh
```

| Skill | Descrição | Uso no Gadget Hub |
|-------|-----------|-------------------|
| `technical-seo` | SEO técnico avançado | Core Web Vitals, crawlability |
| `e-e-a-t` | Framework E-E-A-T Google | Autoridade da loja, confiança |
| `schema` | Dados estruturados | Rich snippets nos resultados |
| `local-seo` | SEO local | Posicionamento em Portugal |
| `pdf-reports` | Relatórios SEO em PDF | Relatórios mensais |

---

### 4. OpenClaudia Marketing Skills — 62+ skills

**Repositório:** `OpenClaudia/openclaudia-skills`
**Instalação Claude Code:** `npx skills add OpenClaudia/openclaudia-skills`

| Skill | Descrição | Uso no Gadget Hub |
|-------|-----------|-------------------|
| `seo-audit` | Auditoria SEO | Auditar toda a loja |
| `write-blog` | Escrita de blog | Blog Shopify com artigos SEO |
| `email-sequence` | Sequências email | Campanhas automatizadas |
| `competitor-analysis` | Análise concorrência | Benchmark vs mercado |
| `product-launch` | Lançamento de produto | Novos produtos na loja |
| `cold-email` | Email a frio | Contacto com fornecedores |
| `discord-bot` | Bot Discord | Comunidade (futuro) |

---

### 5. Marketing Skills Mega Pack (kostja94) — 160+ skills

**Repositório:** `kostja94/marketing-skills`
**Instalação Claude Code:** `npx skills add kostja94/marketing-skills`

**O maior pacote disponível**, inclui:
- SEO técnico (40+ tipos de páginas)
- SEO on-page avançado
- Conteúdo e copywriting
- Paid ads (Google, Facebook, TikTok)
- Estratégias de growth
- Email marketing avançado

---

### 6. Claude Skills 220+ (alirezarezvani) — Mega pack

**Repositório:** `alirezarezvani/claude-skills`
**Instalação Claude Code:** `npx skills add alirezarezvani/claude-skills`

**Personas pré-configuradas relevantes:**

| Persona | Descrição | Quando usar |
|---------|-----------|-------------|
| `growth-marketer` | Especialista em crescimento | Estratégia de marketing |
| `solo-founder` | Fundador a solo | Decisões estratégicas |
| `startup-cto` | CTO de startup | Decisões técnicas |

---

## Mapa de Skills por Área do Projeto

```
📦 PRODUTOS
├── Descrições → copywriting, content-writing
├── SEO produtos → keyword-research, schema-markup
└── Precificação → pricing

🏪 LOJA / SITE
├── Auditoria SEO → seo-audit, technical-seo-audit
├── Schema markup → schema-markup, schema
├── Performance → technical-seo
├── Conversão → page-cro, signup-cro, form-cro
└── Conteúdo páginas → content-writing

📣 MARKETING
├── Redes sociais → social-media
├── Blog → write-blog, content-writing
├── Email marketing → email-sequence
├── Anúncios → ad-creative
├── Lançamentos → launch, product-launch
└── Concorrência → competitor-analysis

📊 ANALYTICS
├── Tracking → analytics-tracking
├── Relatórios → pdf-reports
└── Keywords → keyword-research

🤖 AUTOMAÇÃO
├── Email sequences → email-sequence
├── Cold outreach → cold-email
└── Growth → growth-marketer (persona)
```

---

## Ordem de Instalação Recomendada

| Prioridade | Pacote | Razão |
|------------|--------|-------|
| 1️⃣ | Marketing Skills (Corey Haines) | Mais versátil, cobre copywriting + SEO + CRO |
| 2️⃣ | SEO & GEO Skills (Aaron He Zhu) | Framework CORE-EEAT essencial para SEO |
| 3️⃣ | Claude SEO (AgriciDaniel) | Complementa com SEO técnico e local |
| 4️⃣ | Marketing Mega Pack (kostja94) | 160+ skills para cobertura total |
| 5️⃣ | OpenClaudia Skills | Blog writing e product launch |
| 6️⃣ | Claude Skills 220+ | Personas estratégicas |

---

## Como Usar as Skills

### No Claude Code (terminal):
```bash
# Instalar skill
npx skills add coreyhaines31/marketingskills

# Usar skill numa conversa
# Basta mencionar a área e o Claude aplica automaticamente
```

### No Cowork Mode:
As skills não são instaláveis diretamente no Cowork. Em alternativa:
1. Usar os princípios de cada skill como prompts especializados
2. Instalar no Claude Code CLI se disponível
3. Criar skills personalizadas no Cowork usando o skill-creator

---

## Exemplo Prático: Fluxo de Trabalho com Skills

### Adicionar novo produto ao Gadget Hub:

1. **keyword-research** → Pesquisar keywords PT para o produto
2. **copywriting** → Escrever título e descrição persuasiva
3. **schema-markup** → Adicionar dados estruturados
4. **ad-creative** → Criar copy para anúncios
5. **social-media** → Criar posts para redes sociais
6. **email-sequence** → Incluir em campanha de lançamento

---

*Documento gerado por Claude Opus — Projeto Gadget Hub*
*Filipe Azevedo | abril 2026*
