# GADGET HUB — Sistema de Gestão em Árvore

> Documento mestre de gestão do projeto Gadget Hub
> Última atualização: 6 de abril de 2026

---

## Visão Geral

```
                          🏠 GADGET HUB
                    Loja de Tecnologia & Gadgets
                         gadget-hub.pt
                              │
        ┌─────────┬──────────┼──────────┬──────────┬──────────┐
        │         │          │          │          │          │
    📦 PRODUTOS  🏪 LOJA  📣 MARKETING  💰 VENDAS  📊 ANALYTICS  🤖 AUTOMAÇÃO
        │         │          │          │          │          │
        │         │          │          │          │          │
    ⚙️ CONFIGURAÇÃO (base de suporte transversal a todos os ramos)
```

---

## 📦 RAMO 1: PRODUTOS

Gestão completa do catálogo de produtos, desde a importação até à publicação.

```
📦 PRODUTOS
├── 📋 Catálogo
│   ├── Gestão via Shopify Admin API
│   ├── CRUD de produtos (criar, editar, eliminar)
│   ├── Gestão de variantes (tamanhos, cores)
│   └── Controlo de inventário
│
├── 📥 Importação
│   ├── CJ Dropshipping (fornecedor principal)
│   │   ├── API de pesquisa de produtos
│   │   ├── Importação de imagens
│   │   └── Sincronização de stock
│   ├── AliExpress (fornecedor secundário)
│   └── Avaliação de novos fornecedores
│
├── 💶 Precificação
│   ├── Markup automático (2.5x–4x custo)
│   ├── Comparação com concorrência
│   ├── Preços psicológicos (€19,99 vs €20)
│   ├── Compare_at_price para descontos visuais
│   └── Regras por categoria
│
├── ✍️ Descrições IA
│   ├── Geração com Claude (SEO-otimizadas)
│   ├── Tradução PT-PT (não brasileiro)
│   ├── Bullet points de benefícios
│   ├── Especificações técnicas
│   └── Meta descriptions
│
└── 🖼️ Imagens
    ├── Importação de CJ Dropshipping CDN
    ├── Otimização (compressão, WebP)
    ├── Alt-text automático (SEO)
    ├── Imagens de lifestyle
    └── Dimensões padronizadas (1024×1024)
```

### Estado Atual — Produtos

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Catálogo | ✅ Feito | Automação | 12 produtos criados via API |
| Importação CJ | ✅ Feito | Automação | Imagens reais importadas |
| Precificação | ✅ Feito | Automação | Compare_at_price configurado |
| Descrições IA | 🟡 Em progresso | Manual + IA | Descrições básicas, falta otimizar SEO |
| Imagens | ✅ Feito | Automação | Imagens CJ importadas |
| Expansão catálogo | 🔴 Por fazer | Automação | Meta: 50+ produtos |

---

## 🏪 RAMO 2: LOJA / SITE

Tudo relacionado com a loja online e a experiência do utilizador.

```
🏪 LOJA / SITE
├── 🎨 Tema
│   ├── Tema Horizon (ID: 200900936029)
│   ├── Dark mode customizado (custom-dark-mode.css)
│   ├── Estilo PCComponentes (badges, cards, animações)
│   ├── Cores: fundo escuro, cyan (#00d4ff), vermelho (#ff4444)
│   └── Responsividade mobile
│
├── 📄 Páginas
│   ├── Home (coleções em destaque)
│   ├── Como Funciona ✅
│   ├── Sobre Nós ✅
│   ├── Política de Privacidade e Termos ✅
│   ├── FAQ (por criar)
│   ├── Contacto (por criar)
│   └── Política de Devoluções (detalhada, por criar)
│
├── 📂 Coleções
│   ├── Casa Inteligente (ID: 706744680797)
│   ├── Áudio (ID: 706744746333)
│   ├── Acessórios (ID: 706744779101)
│   ├── Eletrónicos (ID: 706744811869)
│   ├── Ofertas (ID: 706746777949)
│   └── Home page (ID: 706721284445)
│
├── 🔍 SEO
│   ├── Meta titles otimizados
│   ├── Meta descriptions
│   ├── Schema markup (Product, Organization)
│   ├── Sitemap XML (automático Shopify)
│   ├── Robots.txt
│   └── URLs amigáveis
│
└── ⚡ Performance
    ├── Core Web Vitals
    ├── Otimização de imagens
    ├── Lazy loading
    ├── CSS/JS minificado
    └── CDN Shopify
```

### Estado Atual — Loja

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Tema dark mode | ✅ Feito | Automação | CSS PCComponentes aplicado |
| Páginas info | 🟡 Em progresso | Automação | 3 criadas, faltam FAQ e Contacto |
| Coleções | ✅ Feito | Automação | 6 coleções com produtos |
| Menu navegação | ✅ Feito | Automação | Main menu + Footer menu |
| SEO on-page | 🔴 Por fazer | Manual + IA | Meta tags, schema |
| Performance | 🔴 Por fazer | Manual | Auditar vitals |

---

## 📣 RAMO 3: MARKETING & CONTEÚDO

Estratégias de aquisição de clientes e criação de conteúdo.

```
📣 MARKETING & CONTEÚDO
├── 📱 Redes Sociais
│   ├── Instagram
│   │   ├── Feed posts (produtos, lifestyle)
│   │   ├── Stories (promoções, novidades)
│   │   ├── Reels (unboxing, demos)
│   │   └── Calendário editorial
│   ├── Facebook
│   │   ├── Página da loja
│   │   ├── Posts orgânicos
│   │   └── Marketplace
│   ├── TikTok
│   │   ├── Vídeos de produto
│   │   ├── Trends e challenges
│   │   └── Gadget reviews
│   └── Pinterest
│       └── Pins de produtos e lifestyle
│
├── 📝 Blog
│   ├── Artigos SEO (long-tail keywords)
│   ├── Guias de compra ("Melhores gadgets 2026")
│   ├── Reviews de produtos
│   ├── Tutoriais (como usar smart home)
│   └── Publicação: 2-4 artigos/mês
│
├── 📧 Email Marketing
│   ├── Welcome series (3 emails)
│   ├── Abandoned cart recovery
│   ├── Post-purchase follow-up
│   ├── Newsletter semanal
│   ├── Campanhas sazonais
│   └── Plataforma: Shopify Email ou Klaviyo
│
├── 🎯 Anúncios Pagos
│   ├── Google Ads
│   │   ├── Search (keywords de intenção de compra)
│   │   ├── Shopping (feed de produtos)
│   │   └── Display (remarketing)
│   ├── Facebook/Instagram Ads
│   │   ├── Awareness (interesse em tecnologia)
│   │   ├── Conversão (retargeting)
│   │   └── Lookalike audiences
│   └── TikTok Ads
│       └── In-feed (quando orçamento permitir)
│
└── 📈 Tendências
    ├── Pesquisa de mercado (Google Trends)
    ├── Produtos virais (TikTok Made Me Buy It)
    ├── Sazonalidade (Black Friday, Natal, etc.)
    └── Nicho: gadgets Portugal
```

### Estado Atual — Marketing

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Redes sociais | 🔴 Por fazer | Manual | Criar contas e conteúdo |
| Blog Shopify | 🔴 Por fazer | IA + Manual | Planear calendário editorial |
| Email marketing | 🔴 Por fazer | Automação | Configurar Shopify Email |
| Anúncios | 🔴 Por fazer | Manual | Orçamento a definir |
| Pesquisa tendências | 🟡 Em progresso | IA | Lista de produtos em expansão |

---

## 💰 RAMO 4: VENDAS & PEDIDOS

Gestão do funil de vendas, encomendas e relação com clientes.

```
💰 VENDAS & PEDIDOS
├── 📊 Dashboard
│   ├── Resumo diário de vendas
│   ├── Receita por período
│   ├── Ticket médio
│   ├── Taxa de conversão
│   └── Top produtos vendidos
│
├── 📦 Fulfillment
│   ├── Processamento automático via CJ
│   ├── Números de tracking
│   ├── Notificação ao cliente
│   ├── Prazos de entrega (7-12 dias PT)
│   └── Envio grátis >50€
│
├── 🔄 Devoluções
│   ├── Política de 14 dias (lei PT/EU)
│   ├── Processo de reembolso
│   ├── Formulário de devolução
│   └── RMA tracking
│
└── 👥 Clientes
    ├── Segmentação (novos, recorrentes, VIP)
    ├── Lifetime value (LTV)
    ├── Taxas de retenção
    ├── Programa de fidelidade (futuro)
    └── Reviews e testemunhos
```

### Estado Atual — Vendas

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Dashboard | 🔴 Por fazer | Shopify | Ativar após primeiras vendas |
| Fulfillment CJ | 🔴 Por fazer | Automação | Configurar app CJ no Shopify |
| Devoluções | 🟡 Em progresso | Manual | Página criada, falta processo |
| Gestão clientes | 🔴 Por fazer | Automação | Após primeiras vendas |

---

## 📊 RAMO 5: ANALYTICS

Monitorização de métricas e desempenho do negócio.

```
📊 ANALYTICS
├── 📈 Google Analytics 4
│   ├── Tracking code instalado
│   ├── Eventos de e-commerce
│   ├── Funil de conversão
│   ├── Origens de tráfego
│   └── Comportamento do utilizador
│
├── 📉 Shopify Analytics
│   ├── Relatório de vendas
│   ├── Sessões e visitantes
│   ├── Taxa de conversão
│   ├── Produtos mais vistos
│   └── Relatórios financeiros
│
├── 📋 Relatórios Automáticos
│   ├── Relatório semanal (email/Notion)
│   ├── Relatório mensal completo
│   ├── Alertas de anomalias
│   └── Comparação período anterior
│
└── 🎯 KPIs do Negócio
    ├── Receita mensal
    ├── Nº de encomendas
    ├── Ticket médio
    ├── Taxa de conversão
    ├── CAC (Custo Aquisição Cliente)
    ├── LTV (Lifetime Value)
    ├── ROAS (Return on Ad Spend)
    └── Margem líquida
```

### Estado Atual — Analytics

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| GA4 | 🔴 Por fazer | Manual | Instalar pixel |
| Shopify Analytics | ✅ Disponível | Shopify | Ativo por defeito |
| Relatórios auto | 🔴 Por fazer | Automação | Zapier + Notion |
| KPIs definidos | 🟡 Em progresso | Manual | Lista definida |

---

## 🤖 RAMO 6: AUTOMAÇÃO

Sistemas automáticos que reduzem trabalho manual.

```
🤖 AUTOMAÇÃO
├── ⏰ Scheduler
│   ├── Verificação diária de stock
│   ├── Atualização de preços semanal
│   ├── Publicação automática de posts
│   ├── Backup semanal de dados
│   └── Relatórios agendados
│
├── ⚡ Workflows Zapier
│   ├── Nova encomenda → Email + Slack + Calendar
│   ├── Novo produto → Post redes sociais
│   ├── Stock baixo → Alerta email + Slack
│   ├── Nova review → Notificação + Agradecimento
│   └── Novo contacto → CRM + Welcome email
│
├── 🔔 Notificações
│   ├── Alertas de stock baixo (<5 unidades)
│   ├── Novas vendas (Slack #vendas)
│   ├── Reviews de clientes
│   ├── Erros de sistema
│   └── Relatórios diários
│
└── 🤖 Chatbot
    ├── Respostas automáticas FAQ
    ├── Tracking de encomendas
    ├── Recomendações de produtos
    └── Escalação para humano
```

### Estado Atual — Automação

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Python scripts | ✅ Feito | Automação | Sistema base no repo |
| Scheduler | 🔴 Por fazer | Automação | Implementar cron/scheduler |
| Zapier workflows | 🔴 Por fazer | Manual | Conector ativo |
| Notificações | 🔴 Por fazer | Automação | Slack conector ativo |
| Chatbot | 🔴 Por fazer | IA | Fase futura |

---

## ⚙️ RAMO 7: CONFIGURAÇÃO

Infraestrutura técnica que suporta todo o projeto.

```
⚙️ CONFIGURAÇÃO
├── 🔑 APIs
│   ├── Shopify Admin API (REST, session-based)
│   ├── CJ Dropshipping API
│   ├── Anthropic Claude API
│   ├── Serper API (pesquisa web)
│   ├── Meta Marketing API (futuro)
│   └── Google Ads API (futuro)
│
├── 🌐 Domínio
│   ├── GoDaddy: gadget-hub.pt (a configurar)
│   ├── DNS: apontar para Shopify
│   ├── SSL: automático Shopify
│   └── Email: engine.ia009@gmail.com
│
├── 💳 Pagamentos
│   ├── Shopify Payments (cartões)
│   ├── PayPal
│   ├── MB Way / Multibanco (via EASYPAY ou similar)
│   └── Transferência bancária
│
└── 🔒 Segurança
    ├── SSL/TLS (Shopify)
    ├── RGPD compliance
    ├── Política de cookies
    ├── Proteção de dados
    └── Backup de dados
```

### Estado Atual — Configuração

| Módulo | Estado | Responsável | Notas |
|--------|--------|------------|-------|
| Shopify API | ✅ Feito | Automação | CSRF token method |
| CJ API | 🟡 Em progresso | Automação | Scraping funcional |
| Domínio | 🔴 Por fazer | Manual | GoDaddy conector ativo |
| Pagamentos | 🔴 Por fazer | Manual | Configurar Shopify Payments |
| RGPD | 🟡 Em progresso | Manual + IA | Página de privacidade criada |

---

## Resumo Global do Estado do Projeto

| Ramo | Progresso | Prioridade |
|------|-----------|------------|
| 📦 Produtos | 70% | 🔴 Alta |
| 🏪 Loja/Site | 60% | 🔴 Alta |
| 📣 Marketing | 5% | 🟡 Média |
| 💰 Vendas | 10% | 🟡 Média |
| 📊 Analytics | 10% | 🟢 Baixa |
| 🤖 Automação | 30% | 🟡 Média |
| ⚙️ Configuração | 40% | 🔴 Alta |

---

## Próximos Passos Prioritários

1. **Expandir catálogo** para 50+ produtos (Tarefa 2)
2. **Configurar domínio** gadget-hub.pt via GoDaddy
3. **Ativar pagamentos** (Shopify Payments + MB Way)
4. **Criar páginas** FAQ e Contacto
5. **Implementar SEO** (meta tags, schema markup)
6. **Configurar email marketing** (welcome series)
7. **Lançar redes sociais** (Instagram + Facebook)
8. **Configurar Zapier workflows** básicos

---

*Documento gerado por Claude Opus — Projeto Gadget Hub*
*Filipe Azevedo | abril 2026*
