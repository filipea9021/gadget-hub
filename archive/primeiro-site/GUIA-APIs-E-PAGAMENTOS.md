# Guia de Configuração — APIs de Fornecedores + Pagamentos no Shopify

## Visão Geral da Arquitetura

Como o site vai rodar no **Shopify**, a estrutura fica muito mais simples. O Shopify já tem loja de apps com integrações directas para fornecedores e pagamentos. Não precisas de codar APIs do zero — usas apps oficiais que fazem a ponte.

```
[Cliente] → [Loja Shopify] → [App CJ Dropshipping] → [Fornecedor envia]
                ↓
         [Shopify Payments]
         (Cartão, Multibanco, MBWay, PayPal)
```

---

## PARTE A — Fornecedor: CJ Dropshipping

Tu já tens conta no CJ. Agora é ligar ao Shopify.

### Passo 1: Instalar a App do CJ no Shopify

1. Acede ao painel do Shopify → **Apps** → **Shopify App Store**
2. Pesquisa por **"CJ Dropshipping"** (app oficial)
3. Clica em **Instalar** e autoriza a conexão
4. Faz login com a tua conta CJ existente

### Passo 2: Conectar as contas

1. Dentro da app CJ no Shopify, clica em **"Autorizar"**
2. Isto vai ligar a tua loja Shopify à tua conta CJ automaticamente
3. A app usa a API do CJ por trás — tu não precisas de mexer em código

### Passo 3: Importar produtos

1. Na app CJ, vai a **"Produtos"** → pesquisa pelo que queres (ex: "headset gamer")
2. Usa os filtros:
   - Avaliação: 4 estrelas ou mais
   - Armazém: Selecciona armazéns na Europa (PT/ES) para entrega mais rápida
   - Preço: Define o range desejado
3. Clica em **"Adicionar à lista"** nos produtos que quiseres
4. Vai à tua **"Lista de Produtos"** → clica **"Publicar na loja"**
5. O produto aparece automaticamente na tua loja Shopify com fotos, título e descrição

### Passo 4: Configurar preços e margens

1. Na app CJ, antes de publicar, edita cada produto:
   - **Preço de venda**: coloca o teu preço (ex: se o CJ cobra R$45, vende por R$189,90)
   - **Comparar com preço**: preço "riscado" para mostrar desconto (ex: R$249,90)
   - **Variantes**: tamanho, cor, etc.
2. O Shopify calcula automaticamente a margem para ti

### Passo 5: Fluxo automático de pedidos

Quando um cliente compra na tua loja:

1. O pedido aparece no Shopify E na app CJ automaticamente
2. Tu (ou automaticamente) clicas **"Encomendar"** na app CJ
3. O CJ processa, embala e envia o produto
4. O código de rastreamento é enviado de volta ao Shopify
5. O cliente recebe e-mail automático com rastreamento

**Para automatizar 100%:** Nas configurações da app CJ → activa **"Auto-order"**. Assim nem precisas de aprovar manualmente cada pedido.

---

## PARTE B — Outros Fornecedores (AliExpress + Zendrop)

### AliExpress via DSers

O AliExpress não tem app directa boa no Shopify. A melhor forma é usar o **DSers** — a app oficial recomendada pelo AliExpress para Shopify.

1. Shopify App Store → pesquisa **"DSers"** → Instalar
2. Cria conta DSers e liga ao AliExpress
3. Importa produtos do AliExpress directamente
4. Funciona igual ao CJ: cliente compra → DSers faz pedido no AliExpress → produto enviado

**Nota:** AliExpress tem entregas mais lentas (15-30 dias da China). Usa principalmente para produtos que não encontras no CJ.

### Zendrop

1. Shopify App Store → pesquisa **"Zendrop"** → Instalar
2. Cria conta (plano gratuito para começar)
3. Importa produtos e publica na loja
4. Mesmo fluxo automático de pedidos

### Recomendação de prioridade

| Prioridade | Fornecedor | Porquê |
|------------|-----------|--------|
| 1o | CJ Dropshipping | Já tens conta, armazéns na Europa, API robusta |
| 2o | Zendrop | Bom catálogo, fácil de usar, branding |
| 3o | AliExpress (via DSers) | Maior variedade, mas entrega lenta |

---

## PARTE C — Pagamentos no Shopify

### Passo 1: Activar Shopify Payments

O Shopify Payments é o sistema de pagamento nativo. Aceita cartões de crédito/débito automaticamente.

1. Shopify Admin → **Configurações** → **Pagamentos**
2. Clica em **"Activar Shopify Payments"**
3. Preenche os dados da empresa (NIF, IBAN, morada)
4. Após verificação (1-2 dias), já aceitas cartões

**Métodos incluídos no Shopify Payments:**
- Visa, Mastercard, Amex
- Apple Pay, Google Pay
- Multibanco (disponível para Portugal!)
- Bancontact, iDEAL (se expandires para Europa)

### Passo 2: Adicionar MBWay

O MBWay para Shopify é feito através de apps de pagamento portuguesas:

1. Shopify App Store → pesquisa **"EuPago"** ou **"ifthenpay"**
2. Instalar a app escolhida
3. Criar conta na EuPago/ifthenpay (são gateways portugueses)
4. Preencher dados bancários e fiscais
5. Activar MBWay, Multibanco e Referência Bancária

**EuPago vs ifthenpay:**
| | EuPago | ifthenpay |
|--|--------|-----------|
| MBWay | Sim | Sim |
| Multibanco | Sim | Sim |
| Taxa por transação | ~1% | ~0.8% |
| Setup | Mais rápido | Mais barato |

### Passo 3: Adicionar PayPal

1. Shopify Admin → **Configurações** → **Pagamentos**
2. Na secção "Pagamentos adicionais" → clica **"PayPal"**
3. Liga a tua conta PayPal Business (se não tens, cria uma em paypal.com)
4. Autoriza a conexão → pronto!

### Passo 4: Transferência Bancária (manual)

1. Shopify Admin → **Configurações** → **Pagamentos**
2. Secção "Pagamentos manuais" → **"Transferência bancária"**
3. Adiciona o teu IBAN e instruções de pagamento
4. O cliente vê os dados bancários no checkout e faz transferência
5. Tu confirmas manualmente quando o dinheiro cai na conta

---

## PARTE D — Resumo: O que precisas criar/configurar

### Contas necessárias (checklist)

- [x] CJ Dropshipping (já tens!)
- [ ] Loja Shopify (shopify.com → plano Basic, ~$39/mês ou trial gratuito de 3 dias)
- [ ] EuPago ou ifthenpay (para MBWay + Multibanco PT)
- [ ] PayPal Business (paypal.com)
- [ ] DSers (se quiseres usar AliExpress)
- [ ] Zendrop (se quiseres como fornecedor adicional)

### Ordem recomendada de configuração

| Passo | O que fazer | Tempo estimado |
|-------|------------|----------------|
| 1 | Criar loja Shopify e escolher tema | 1-2 horas |
| 2 | Instalar app CJ Dropshipping e ligar conta | 15 minutos |
| 3 | Importar 10-15 produtos do CJ para a loja | 1 hora |
| 4 | Activar Shopify Payments (cartões) | 30 minutos |
| 5 | Criar conta EuPago e activar MBWay | 1-2 dias (verificação) |
| 6 | Ligar PayPal | 15 minutos |
| 7 | Personalizar tema, logo, cores (estilo TechZone) | 2-3 horas |
| 8 | Configurar e-mails automáticos | 30 minutos |
| 9 | Testar compra completa | 30 minutos |

---

## PARTE E — E o código que já fizemos?

O HTML/CSS/JS que criámos serve como **protótipo visual e referência de design**. No Shopify, vais usar esse design como base para:

1. **Personalizar o tema Shopify** — aplicar as cores (#0a0a0f, #7c3aed, #00d4ff), o estilo dark, e o layout
2. **Seções customizadas** — as seções "Como Funciona", "Problemas do Mercado", "Referências" podem ser adicionadas como secções Liquid no Shopify
3. **Sistema de Skills** — os arquivos da pasta `sistema/` servem como documentação da lógica de negócio. O score de produto e os gatilhos de marketing podem ser implementados como metafields no Shopify
4. **Chatbot** — pode ser adicionado via app Shopify (ex: Tidio, Gorgias, ou custom com o código que já temos)

**Nada se perde!** O protótipo que fizemos é o blueprint visual e lógico. O Shopify é a plataforma que vai hospedar e operar tudo.

---

## PARTE F — API Keys e Segurança

Quando tiveres as contas criadas, as API keys ficam assim:

| Serviço | Onde encontrar a API Key | Onde usar |
|---------|--------------------------|-----------|
| CJ Dropshipping | Painel CJ → Settings → API | App CJ no Shopify (automático) |
| Shopify | Admin → Apps → Develop apps | Só se fizeres custom development |
| EuPago | Backoffice EuPago → Integrações | App EuPago no Shopify |
| PayPal | developer.paypal.com → Credentials | Configuração de pagamentos Shopify |
| Stripe | dashboard.stripe.com → API Keys | Shopify Payments (automático) |

**IMPORTANTE:** Nunca coloques API keys directamente no código HTML/JS visível ao público. No Shopify, as apps tratam disso automaticamente de forma segura.
