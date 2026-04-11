# 🚀 Gadget Hub — Guia Completo do Projecto

> **Loja:** gadget-hub.com
> **Nicho:** Eletrónicos, Casa Inteligente & Acessórios Tech
> **Plataforma:** Shopify
> **Fornecedor principal:** CJ Dropshipping
> **Data:** Abril 2026

---

## ⚙️ PARTE 5 — Tecnologia e Stack Técnica

### Stack Real Adoptada (Shopify)

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Loja / Frontend | Shopify | Tudo-em-um, sem servidor próprio |
| Produtos / Backend | CJ Dropshipping App | Sincronização automática de stock e pedidos |
| Pagamentos PT | Shopify Payments + EuPago/ifthenpay | Cartão, MBWay, Multibanco |
| Pagamentos Global | PayPal | Compradores internacionais |
| Domínio | gadget-hub.com (GoDaddy) | Domínio .com registado |
| Email Transacional | Shopify Email (nativo) | Confirmações, rastreamento |
| Protótipo Visual | HTML/CSS/JS (ficheiros locais) | Blueprint de design para o Shopify |

### Utilização de IA no Projecto

| Função | O que faz | Quando |
|--------|-----------|--------|
| Descrições de produto | Gera texto persuasivo automaticamente | Na importação do produto (CJ → Shopify) |
| Score de produto | Calcula pontuação com base em métricas reais | A cada novo produto adicionado |
| Deteção de tendências | Identifica produtos com potencial viral | Semanal (pesquisa manual no CJ) |
| Atendimento ao cliente | Responde FAQs via chatbot | Em tempo real |
| Copy de anúncios | Gera textos para TikTok/Meta | Sob demanda |

### Segurança
- HTTPS automático via Shopify (certificado SSL incluído)
- Pagamentos 100% via Shopify Payments / EuPago (PCI compliant)
- Proteção contra fraude nativa do Shopify
- Política de Privacidade conforme RGPD (obrigatório em PT)
- Backups automáticos do Shopify

---

## 🤖 PARTE 7 — Automação do Pipeline

### Arquitectura do Pipeline (Estado Actual)

```
Comando inicial (ex: "adicionar produto de smart home")
        ↓
[Skill 1 — Pesquisa] Pesquisa no CJ Dropshipping
        ↓
[Skill 2 — Site] Valida e importa produto para o Shopify
        ↓
[Skill 3 — Marketing] Gera copy e estratégia de anúncio
        ↓
[Skill 4 — Automação] Configura fluxos de email e rastreamento
        ↓
Produto ao vivo na loja
```

### Ficheiros do Sistema (já criados)

| Ficheiro | Função |
|----------|--------|
| `sistema/orquestrador.js` | Orquestra e encaminha comandos entre skills |
| `sistema/skills/skill1-produtos.js` | Pesquisa e validação de produtos (score, margem) |
| `sistema/skills/skill2-site.js` | Criação e gestão de páginas da loja |
| `sistema/skills/skill3-marketing.js` | Estratégia de marketing e copy de anúncios |
| `sistema/skills/skill4-automacao.js` | Chatbot, rastreamento e notificações |
| `sistema/app.js` | Ponto de entrada principal do sistema |

### Evolução Planeada

| Fase | Capacidade | Quando |
|------|-----------|--------|
| V1 — Actual | Sistema de skills manual (protótipo HTML) | Agora |
| V2 | Shopify live + CJ Dropshipping integrado | Mês 1 |
| V3 | Painel de controlo com botões por skill | Mês 3 |
| V4 | Automatização completa com IA | Mês 6+ |

---

## 💰 PARTE 8 — Modelo de Receita

### Fontes de Receita

| Fonte | Descrição | Margem Estimada |
|-------|-----------|----------------|
| Margem do produto | Preço de venda − custo CJ Dropshipping | 40–70% |
| Upsell / Cross-sell | Produtos complementares sugeridos | +15–25% por pedido |
| Kits / Combos | Ex: Smart Plug + Lâmpada RGB em pack | +20–30% margem |
| Marca própria (futuro) | Produtos com etiqueta Gadget Hub | 50–70% |

### Estratégia de Preço
- Margem mínima de **40%** por produto
- Preço psicológico: 29,90€ em vez de 30€
- Envio "grátis" embutido no preço do produto
- Cupão de **10% off** na primeira compra para aumentar conversão
- Comparar sempre com Amazon PT e FNAC antes de definir preço

### Projecção de Crescimento (Gadget Hub)

| Métrica | Mês 1 | Mês 3 | Mês 6 | Mês 12 |
|---------|-------|-------|-------|--------|
| Produtos no catálogo | 12 | 30 | 60 | 100+ |
| Visitantes/mês | 300 | 2.000 | 8.000 | 25.000+ |
| Taxa de conversão | 1% | 1,5% | 2% | 2,5% |
| Pedidos/mês | 3 | 30 | 160 | 625+ |
| Ticket médio | 35€ | 40€ | 45€ | 50€ |
| Receita bruta | ~105€ | ~1.200€ | ~7.200€ | ~31.000€+ |

> ⚠️ **Nota:** Projecções estimadas. Resultados reais dependem do investimento em marketing e qualidade dos produtos escolhidos.

---

## 🎯 PARTE 9 — MVP e Roadmap de Lançamento

### O que é o MVP da Gadget Hub

O MVP (Versão Mínima Viável) é a versão mais simples que permite **validar o negócio com clientes reais**.

**O MVP inclui:**
- ✅ Nicho definido: Eletrónicos, Casa Inteligente & Acessórios
- ✅ 12 produtos curados com score calculado
- ✅ Protótipo visual completo (index.html, produto.html, checkout.html)
- ✅ Sistema de skills (orquestrador + 4 módulos)
- ✅ Domínio registado: gadget-hub.com
- ⏳ Shopify configurado (próximo passo)
- ⏳ CJ Dropshipping ligado ao Shopify
- ⏳ Pagamentos activados (MBWay, Cartão, PayPal)
- ⏳ Primeiros anúncios (TikTok/Meta)

### Roadmap Semanal de Lançamento

| Semana | Tarefa | Estado |
|--------|--------|--------|
| 1 | Definir nicho e 12 produtos curados | ✅ Feito |
| 1 | Criar protótipo visual completo | ✅ Feito |
| 1 | Registar domínio gadget-hub.com | ✅ Feito |
| 2 | Criar conta Shopify e instalar tema | ⏳ Próximo |
| 2 | Instalar app CJ Dropshipping | ⏳ Próximo |
| 2 | Importar 12 produtos para o Shopify | ⏳ Próximo |
| 3 | Configurar pagamentos (MBWay, Cartão, PayPal) | ⏳ Próximo |
| 3 | Conectar domínio gadget-hub.com ao Shopify | ⏳ Próximo |
| 3 | Testar fluxo completo (compra → pagamento → email) | ⏳ Próximo |
| 4 | Criar conta TikTok Business e Meta Business | ⏳ Futuro |
| 4 | Lançar primeiros anúncios (orçamento: 10€/dia) | ⏳ Futuro |
| 5–6 | Optimizar com base em dados reais de visitas/vendas | ⏳ Futuro |

### ❌ O Que NÃO Fazer no Início
- Não tentar ter 100 produtos antes de validar o conceito
- Não gastar em features avançadas antes da primeira venda
- Não ignorar o mobile — mais de 70% do tráfego vem do telemóvel
- Não lançar sem políticas de privacidade e termos de uso
- Não copiar preços sem calcular a margem mínima de 40%

---

## 📈 PARTE 10 — Escala e Evolução Futura

### Fase 1 — Crescimento (Mês 3–6)
- Expandir catálogo para 50–100 produtos validados
- Aumentar orçamento de anúncios com dados reais de ROAS
- Implementar email marketing (sequências automáticas pós-compra)
- Adicionar sistema de avaliações com fotos de clientes reais
- A/B testing em páginas de produto e preços

### Fase 2 — Consolidação (Mês 6–12)
- Criar marca própria nos produtos mais vendidos (white label via CJ)
- Programa de fidelidade / pontos de desconto
- Expandir para sub-nichos: domótica, produtividade, áudio premium
- Chatbot inteligente com IA para suporte 24/7
- Explorar mercados: Espanha, Brasil, Reino Unido

### Fase 3 — Expansão (Ano 2+)
- Multi-fornecedores com sistema de comparação automático de preços
- App móvel nativa Gadget Hub
- Sistema de afiliados para influencers de tech
- "Gadget Hub Pro" — sistema de skills completamente autónomo
- Equipa dedicada: gestor de produtos, especialista de anúncios, suporte

### 🚀 Visão Final

> A **Gadget Hub** não é só uma loja de dropshipping.
> É um **marketplace inteligente de tecnologia para o dia-a-dia**,
> automatizado por IA, com marca forte e experiência de compra curada.
>
> **Cada skill funciona de forma independente mas coordenada:**
> pesquisa → site → marketing → automação
>
> O sistema evolui de manual → semi-automático → totalmente autónomo.
> O resultado: um **negócio escalável e diferenciado** no mercado português e ibérico.

---

## ✅ Checklist de Estado do Projecto

| Tarefa | Estado |
|--------|--------|
| Visão de negócio definida | ✅ |
| Nicho escolhido (Eletrónicos/Casa/Acessórios) | ✅ |
| Fluxo operacional documentado | ✅ |
| Referências de mercado analisadas | ✅ |
| Protótipo visual (index + produto + checkout) | ✅ |
| Sistema de skills (4 módulos + orquestrador) | ✅ |
| Diferencial competitivo definido | ✅ |
| Stack técnica definida (Shopify + CJ) | ✅ |
| Domínio registado (gadget-hub.com) | ✅ |
| Guia de APIs e pagamentos criado | ✅ |
| Conta CJ Dropshipping criada | ✅ |
| **Shopify — criar conta e configurar loja** | ⏳ |
| **Importar produtos via CJ Dropshipping app** | ⏳ |
| **Configurar pagamentos (MBWay, Cartão, PayPal)** | ⏳ |
| **Conectar domínio ao Shopify** | ⏳ |
| **Testar fluxo completo de compra** | ⏳ |
| **Lançar primeiros anúncios** | ⏳ |
