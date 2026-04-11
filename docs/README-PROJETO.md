# Gadget Hub - Documentação de Projeto

## Visão Geral do Projeto

**Gadget Hub** é uma loja de dropshipping de tecnologia e gadgets em português, construída na plataforma Shopify. Focamo-nos em oferecer os melhores produtos tech ao mercado português com preços competitivos e uma experiência de compra intuitiva.

### Informações Principais

- **Nome da Loja:** Gadget Hub
- **URL da Loja:** https://gadget-hub-72955.myshopify.com
- **Repositório:** https://github.com/filipea9021/gadget-hub
- **Plataforma:** Shopify
- **Status:** Em fase de expansão (Fase 3)

## Mercado-Alvo

- **Localização Principal:** Portugal
- **Faixa Etária:** 18-45 anos
- **Interesses:** Tecnologia, gadgets, eletrônicos, inovação
- **Comportamento:** Compradores online, early adopters de tecnologia, entusiastas de gadgets

## Árvore de Gestão

```
┌─────────────────────────────────────────────────────────┐
│                     GADGET HUB                          │
│         Loja de Dropshipping de Tecnologia              │
│                  Em Shopify                             │
└──────────────────┬──────────────────────────────────────┘
                   │
         ┌─────────┴─────────┬──────────────┬──────────────┬────────────────┐
         │                   │              │              │                │
    ┌────▼─────┐    ┌────────▼───┐  ┌──────▼─────┐  ┌─────▼──────┐  ┌──────▼────────┐
    │ SHOPIFY  │    │ AUTOMATION │  │ SUPPLY    │  │ MARKETING │  │ OPERAÇÕES   │
    │  STORE   │    │   (IA+API) │  │  CHAIN    │  │  & VENDAS │  │  & ANÁLISE  │
    └──────────┘    └────────────┘  └───────────┘  └───────────┘  └─────────────┘
         │                   │              │              │                │
    ├─ Tema              ├─ Python      ├─ CJ Drop   ├─ Email        ├─ Analytics
    ├─ Produtos          ├─ Claude AI   ├─ Zapier    ├─ Social Media  ├─ Notion
    ├─ Coleções          ├─ Shopify API ├─ Gmail     ├─ SEO           ├─ Slack
    ├─ Checkout          └─ Integrações └─ Google Ads└─ Ads Pagos    └─ Google Cal
    └─ Pagamentos                          └─ Klaviyo  └─ A/B Testing


Team:
└─ Filipe Azevedo (Fundador/Gestor)
└─ Claude AI (Automação & Suporte)
```

## Tecnologias Utilizadas

### Plataforma Principal
- **Shopify** - Plataforma de e-commerce

### Automação & Backend
- **Python** - Scripts de automação
- **Claude AI** - Inteligência artificial para automação
- **Shopify API** - Integração com a loja
- **Zapier** - Automação de workflows

### Supply Chain & Produtos
- **CJ Dropshipping** - Fornecedor de produtos
- **Gmail** - Comunicações
- **GoDaddy** - Domínio

### Marketing & Vendas
- **Email Marketing** - Comunicação com clientes
- **Social Media** - Presença nas redes sociais
- **Google Ads** - Publicidade paga
- **Facebook Ads** - Publicidade paga
- **Klaviyo** - Email marketing avançado
- **SEO** - Otimização de search engines

### Gestão & Produtividade
- **Notion** - Base de dados e documentação
- **Slack** - Comunicação
- **Google Calendar** - Agenda

## Instruções de Setup Rápido

### 1. Acesso à Loja
```bash
# URL de administração
https://gadget-hub-72955.myshopify.com/admin

# Repositório
git clone https://github.com/filipea9021/gadget-hub
cd gadget-hub
```

### 2. Dependências Python
```bash
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
```bash
cp .env.example .env
# Configurar: SHOPIFY_API_KEY, SHOPIFY_PASSWORD, CJ_API_KEY, etc.
```

### 4. Executar Automações
```bash
python main.py
```

## Links Importantes

| Recurso | Link |
|---------|------|
| Loja Principal | https://gadget-hub-72955.myshopify.com |
| Admin Shopify | https://gadget-hub-72955.myshopify.com/admin |
| Repositório GitHub | https://github.com/filipea9021/gadget-hub |
| CJ Dropshipping | https://www.cjdropshipping.com |
| Zapier | https://zapier.com |
| Notion Base | [Link da Base] |

## Estrutura do Projeto

```
gadget-hub/
├── docs/                          # Documentação
│   ├── README-PROJETO.md         # Este arquivo
│   ├── ROADMAP.md                # Roteiro de fases
│   └── CHANGELOG.md              # Histórico de alterações
├── src/                           # Código-fonte
│   ├── shopify_api.py            # Integração Shopify
│   ├── cj_importer.py            # Importador de produtos CJ
│   ├── claude_automation.py       # Integrações Claude AI
│   └── utils.py                  # Utilitários
├── config/                        # Ficheiros de configuração
│   ├── .env                      # Variáveis de ambiente
│   └── settings.json             # Configurações
├── data/                          # Dados
│   ├── products/                 # Catálogo de produtos
│   └── analytics/                # Dados de análise
├── scripts/                       # Scripts de automação
│   ├── import_products.py        # Importar produtos
│   ├── update_inventory.py       # Atualizar inventário
│   └── sync_emails.py            # Sincronizar emails
├── tests/                         # Testes
│   └── test_api.py               # Testes de API
├── requirements.txt              # Dependências Python
├── main.py                       # Ponto de entrada principal
├── .gitignore                    # Ficheiros ignorados
└── README.md                     # Documentação principal (inglês)
```

## Team

### Fundador & Gestor
- **Filipe Azevedo** - Fundador, estratégia, gestão geral

### Automação & Suporte
- **Claude AI** - Automação, criação de conteúdo, análise, suporte

## Fases do Projeto

Consulte [ROADMAP.md](./ROADMAP.md) para detalhes completos sobre:
- Fase 1: MVP (Concluído - Março 2026)
- Fase 2: Automação (Concluído - Março-Abril 2026)
- Fase 3: Expansão (Atual - Abril-Maio 2026)
- Fase 4: Escala (Junho-Agosto 2026)
- Fase 5: Private Label (Setembro 2026+)

## Histórico de Mudanças

Consulte [CHANGELOG.md](./CHANGELOG.md) para o histórico completo de todas as alterações realizadas no projeto.

## Contato & Suporte

Para questões relacionadas com o projeto:
- Email: [email de contato]
- Slack: #gadget-hub-projeto
- Notion: [Link da Base de Dados]

---

**Última atualização:** 6 de abril de 2026
