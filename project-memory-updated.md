**Purpose & context**

Filipe is building "Gadget Hub", a dropshipping e-commerce store focused on tech gadgets, electronics, and smart home products, targeting the Portuguese market (Portugal). The project evolved from an initial AI-driven modular concept into a live Shopify store. The long-term vision extends beyond dropshipping toward private label branding. The project is also documented in Notion under a dedicated workspace, planned across 10 structured parts.

**Store details**

- **Platform**: Shopify (gadget-hub-72955.myshopify.com)
- **Theme**: Horizon v3.5.1 (active)
- **Store name**: Gadget Hub
- **Store email**: filipeazevedo791@gmail.com
- **Market**: Portugal (EUR currency)
- **Language**: Portuguese (store interface), products partially in English
- **Status**: In development (password-protected, not yet public)

**What's been completed**

- **Products**: 69 products imported via CJ Dropshipping across multiple categories
- **Collections**: 17 collections created — Casa Inteligente, Audio, Acessorios, Eletronicos, Ofertas, Wearables, Gaming, Gadgets Auto, Gadgets Cozinha, Iluminacao LED, Power Banks, Seguranca, Smart Home, Acessorios Mobile, Home page, Todas as colecoes
- **Payment**: At least 1 payment method configured
- **Fulfillment**: CJ Dropshipping fulfillment integration activated and saved
- **Legal pages**: All 4 required policies published:
  - Politica de Reembolso/Devolucao (Shopify template)
  - Termos de Servico (Shopify template)
  - Politica de Envio (custom HTML with Portugal-specific shipping rates: CTT normal 3.99 EUR, CTT expresso 6.99 EUR, gratis acima de 50 EUR)
  - Informacoes de Contacto (Shopify template with auto-filled store data)
  - Politica de Privacidade (automated by Shopify)
- **Navigation menu**: Main menu updated with 9 items — Home, Casa Inteligente, Audio, Acessorios, Eletronicos, Ofertas, Wearables, Gaming, Novidades (linked to "Todas as colecoes")
- **Planning docs**: Complete 10-part planning document (DOCX + Notion) covering business overview, market analysis, competitive differentiation, site structure, tech stack, AI skills system, pipeline automation, revenue model, MVP roadmap, and scaling vision

**Current phase: Launch preparation (Fase 1)**

Progress: ~70% complete. Remaining tasks:
1. Personalizar homepage — traduzir textos para PT, customizar banner Hero e seccao de produtos em destaque (theme editor has loading issues)
2. Pesquisar e registar dominio personalizado (e.g., gadget-hub.pt or similar)
3. Remover password da loja e abrir ao publico
4. Verificacao final de toda a Fase 1

**Phase 2 (post-launch)**

- Add MB Way payment method
- Improve product images (replace supplier images with professional ones)
- SEO optimization
- Marketing and social media setup
- Private label branding evolution

**Tools & resources**

- **Shopify Admin**: https://admin.shopify.com/store/gadget-hub-72955
- **Theme editor**: https://admin.shopify.com/store/gadget-hub-72955/themes/200900936029/editor
- **Menu editor**: https://admin.shopify.com/store/gadget-hub-72955/content/menus/338333237597
- **CJ Dropshipping**: Integrated as fulfillment provider
- **Notion MCP integration**: Active. Root project page ID is `33865dbc-f0bf-81c0-94ee-edc7493ce8e3` — use as parent reference for sub-pages. Child pages via `Notion:notion-create-pages`, content updates via `Notion:notion-update-page` with `old_str`/`new_str`.
- **Notion page URL**: `notion.so/a6ff0f0f2ef344c5b3ef627af71b19b5` (inaccessible via fetch — create pages directly in workspace)

**Technical notes**

- Shopify theme editor (Horizon) frequently has loading issues — sidebar panel gets stuck on loading placeholders, preview sometimes shows grey screen. Workaround: navigate to themes list page first, wait for full load, then click "Editar tema".
- Shopify policy editor uses shadow DOM web components with CodeMirror. To insert HTML: target the `._PlainView_1r4k9_53` textarea using native setter + set `cm-content.textContent` directly.
- The Shopify Sidekick chat textarea can interfere with editor targeting — use specific selectors to avoid it.

**About Filipe**

- Based in Portugal
- Building this as a solo entrepreneur
- Communicates in Portuguese (Brazilian/European mix)
- Prefers hands-on execution over lengthy planning discussions
- Has Notion, Gmail, Google Calendar, Google Drive, and Slack integrations available

---
*Last updated: 7 April 2026*
