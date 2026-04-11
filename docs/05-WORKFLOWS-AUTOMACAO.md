# Automações Gadget Hub - Documentação Completa

**Data de Criação:** Abril de 2026
**Versão:** 1.0
**Responsável:** Equipa de Automação Gadget Hub

---

## Índice

1. [Introdução](#introdução)
2. [Workflows Zapier](#workflows-zapier)
3. [Google Calendar - Calendários de Trabalho](#google-calendar---calendários-de-trabalho)
4. [Templates de Email (Gmail)](#templates-de-email-gmail)
5. [Configuração Notion](#configuração-notion)
6. [Estrutura de Canais Slack](#estrutura-de-canais-slack)
7. [Checklist de Implementação](#checklist-de-implementação)

---

## Introdução

Este documento descreve os workflows de automação que permitem otimizar operações da Gadget Hub, incluindo gestão de encomendas, comunicação com clientes, gestão de stock e marketing.

**Conectores Disponíveis:**
- Gmail
- Notion
- GoDaddy
- Google Calendar
- Zapier
- Slack
- Google Drive

**Benefícios Esperados:**
- Redução de 70% no tempo de resposta a encomendas
- Automação de 100% de confirmações e notificações
- Rastreamento centralizado de stock
- Comunicação consistente com clientes
- Maior eficiência operacional

---

## Workflows Zapier

### 1. Nova Encomenda Shopify

**Objetivo:** Automatizar resposta a novas encomendas com confirmação personalizada, notificação interna e agendamento.

**Trigger:** Novo pedido criado em Shopify

**Sequência de Ações:**

1. **Receber dados da encomenda:**
   - ID do pedido
   - Nome e email do cliente
   - Produtos (nome, quantidade, preço)
   - Morada de entrega
   - Método de pagamento
   - Total da encomenda

2. **Ação 1 - Email Confirmação (Gmail)**
   - Template: "Confirmação de Encomenda"
   - Recipiente: Email do cliente
   - Personalizações: {{customer_name}}, {{order_number}}, {{order_total}}
   - Delay: Imediato (0 segundos)

3. **Ação 2 - Notificação Slack**
   - Canal: #vendas
   - Mensagem: "Nova encomenda #{{order_number}} de {{customer_name}} - €{{order_total}}"
   - Formato: Com link para ordem em Shopify

4. **Ação 3 - Criar Evento no Google Calendar**
   - Calendário: "Encomendas Gadget Hub"
   - Título: "Processar Encomenda #{{order_number}}"
   - Data/Hora: Data de receção + 1 dia (horário 09:00)
   - Descrição: Inclui cliente, produtos e total
   - Notificação: 1 dia antes

**Configuração Zapier:**
```
Trigger: Shopify > New Order
├─ Action 1: Gmail > Send Email
├─ Action 2: Slack > Send Channel Message
└─ Action 3: Google Calendar > Create Event
```

**Resultado Esperado:**
- Cliente recebe confirmação em menos de 1 minuto
- Equipa é notificada no Slack
- Evento criado no calendário para processamento

---

### 2. Novo Produto Adicionado

**Objetivo:** Publicar automaticamente novos produtos nas redes sociais e registar no Notion.

**Trigger:** Novo produto adicionado ao Shopify

**Sequência de Ações:**

1. **Receber dados do produto:**
   - Nome do produto
   - Descrição
   - Preço
   - Imagem principal
   - Categoria
   - SKU

2. **Ação 1 - Postar em Redes Sociais**
   - Plataformas: Facebook, Instagram (via Zapier integração)
   - Mensagem: "Novo gadget à chegada! 🎉 [nome_produto] - Só {{preço}}€ - Descobre em [link]"
   - Imagem: Imagem do produto
   - Hashtags: #GadgetHub #NovosProdutos #Tecnologia

3. **Ação 2 - Adicionar ao Notion Database**
   - Base de Dados: "Produtos Gadget Hub"
   - Campos a preencher:
     - Nome: {{product_name}}
     - Categoria: {{product_category}}
     - Preço Venda: {{product_price}}
     - Descrição: {{product_description}}
     - SKU: {{product_sku}}
     - Estado: "Ativo"
     - Data de Criação: {{current_date}}

**Configuração Zapier:**
```
Trigger: Shopify > New Product
├─ Action 1: Social Media > Create Post (Facebook/Instagram)
└─ Action 2: Notion > Create Database Item
```

**Resultado Esperado:**
- Produto publicado automaticamente em redes sociais
- Entrada criada na base de dados Notion
- Histórico centralizado de todos os produtos

---

### 3. Stock Abaixo de 5 Unidades

**Objetivo:** Alertar imediatamente quando stock cai criticamente.

**Trigger:** Quantity em Shopify desce abaixo de 5 unidades

**Sequência de Ações:**

1. **Ação 1 - Email de Alerta**
   - Recipiente: email@gadeathub.pt, gestor@gadethub.pt
   - Assunto: "ALERTA: Stock Crítico - {{product_name}}"
   - Corpo: Inclui nome do produto, quantidade atual, SKU, fornecedor
   - Prioridade: Alta

2. **Ação 2 - Mensagem Slack**
   - Canal: #alertas
   - Mensagem: "🚨 ALERTA STOCK: {{product_name}} apenas {{quantity}} unidades restantes!"
   - Formato: Mensagem destacada com cores
   - Menção: @gerente-loja

**Configuração Zapier:**
```
Trigger: Shopify > Product Inventory Change (when quantity < 5)
├─ Action 1: Gmail > Send Email
└─ Action 2: Slack > Send Channel Message
```

**Resultado Esperado:**
- Alerta imediato na chegada ao limite crítico
- Equipa notificada para reposição de stock
- Histórico de alertas mantido

---

### 4. Nova Review de Cliente

**Objetivo:** Agradecer automaticamente reviews e partilhar nas redes sociais.

**Trigger:** Novo review de cliente no Shopify

**Sequência de Ações:**

1. **Validar informações:**
   - Nome do cliente
   - Classificação (1-5 estrelas)
   - Texto da review
   - Produto avaliado

2. **Ação 1 - Notificação Slack**
   - Canal: #vendas
   - Mensagem: "⭐ Nova review de {{customer_name}}: {{rating}} estrelas - {{product_name}}"
   - Incluir: Texto completo da review
   - Condicional: Apenas se rating >= 4 estrelas (para reviews positivas)

3. **Ação 2 - Email de Agradecimento**
   - Template: "Agradecimento por Review"
   - Recipiente: {{customer_email}}
   - Personalização: Nome do cliente, produto, oferta de desconto (10%) para próxima compra
   - Delay: 1 hora após review

**Configuração Zapier:**
```
Trigger: Shopify > New Review
├─ Filter: rating >= 4
├─ Action 1: Slack > Send Channel Message
└─ Action 2: Gmail > Send Email
```

**Resultado Esperado:**
- Reviews positivas partilhadas internamente
- Clientes recebem agradecimento personalizado
- Incentivo para futuras compras

---

### 5. Carrinho Abandonado - Email Recovery Sequence

**Objetivo:** Recuperar vendas através de email sequence automática.

**Trigger:** Cliente abandona carrinho por mais de 10 minutos (Shopify)

**Sequência de Ações:**

**Email 1 - Após 1 hora:**
- Template: "Carrinho Abandonado - Primeira Lembrança"
- Recipiente: {{customer_email}}
- Conteúdo: Imagens dos produtos, preço total, link direto para carrinho
- CTA: "Completar Compra"
- Delay: Exatamente 1 hora

**Email 2 - Após 24 horas:**
- Template: "Esqueceu-se de algo?"
- Recipiente: {{customer_email}}
- Conteúdo: Reforço dos benefícios dos produtos, avaliações de clientes
- Incentivo: Desconto de 5% na encomenda
- CTA: "Recuperar Carrinho"
- Delay: 24 horas da primeira lembrança

**Email 3 - Após 72 horas:**
- Template: "Última Oportunidade!"
- Recipiente: {{customer_email}}
- Conteúdo: Urgência ("Ofertas terminam em 24h"), depoimentos de clientes
- Incentivo: Desconto de 10% (maior)
- CTA: "Finalizar Pedido Agora"
- Delay: 72 horas da primeira lembrança

**Configuração Zapier:**
```
Trigger: Shopify > Abandoned Cart
├─ Delay: 1 hour
├─ Action 1: Gmail > Send Email (Template 1)
├─ Delay: 24 hours
├─ Action 2: Gmail > Send Email (Template 2)
├─ Delay: 72 hours
└─ Action 3: Gmail > Send Email (Template 3)
```

**Condicional:** Se cliente completar compra, parar sequence

**Resultado Esperado:**
- Recuperação estimada de 15-20% de carrinhos abandonados
- Aumento de receita sem esforço manual
- Dados de comportamento do cliente capturados

---

### 6. Nova Subscrição Newsletter - Welcome Series

**Objetivo:** Onboarding automatizado de novos subscribers com série de boas-vindas.

**Trigger:** Novo email subscrito na newsletter (via Shopify/Website)

**Sequência de Ações:**

**Email 1 - Imediato:**
- Template: "Bem-vindo à Gadget Hub!"
- Assunto: "{{name}}, bem-vindo à comunidade Gadget Hub 🎉"
- Conteúdo: Boas-vindas, história da loja, benefícios de ser subscriber
- Incentivo: Desconto de 15% na primeira compra
- CTA: "Descobrir Produtos"

**Email 2 - Após 2 dias:**
- Template: "Gadgets mais Populares"
- Conteúdo: 5 produtos mais vendidos com imagens e links
- Personalização: Baseado em categoria de interesse (se disponível)

**Email 3 - Após 5 dias:**
- Template: "Guia do Gadget Hub"
- Conteúdo: Como navegar a loja, garantias, política de devolução, contacto
- CTA: "Ver Políticas Completas"

**Ação Paralela - Adicionar ao Notion CRM:**
- Base de Dados: "CRM Clientes"
- Campos:
  - Email: {{email}}
  - Nome: {{name}}
  - Data de Subscrição: {{current_date}}
  - Status: "Subscriber"
  - Fonte: "Newsletter"
  - Última Atividade: {{current_date}}
  - Tags: "Newsletter, Novo Subscriber"

**Configuração Zapier:**
```
Trigger: Website Form > New Email Subscription
├─ Action A: Notion > Create Database Item (CRM)
├─ Email 1: Delay 0min > Gmail > Send Email
├─ Email 2: Delay 2 days > Gmail > Send Email
└─ Email 3: Delay 5 days > Gmail > Send Email
```

**Resultado Esperado:**
- Nova base de contactos centralizada no Notion
- Primeiro contacto com cliente otimizado
- Aumento de 25-30% em conversão de subscribers para clientes
- Histórico de interação com cliente mantido

---

## Google Calendar - Calendários de Trabalho

### Calendário 1: Editorial Content Calendar

**Nome:** "Calendário Editorial - Gadget Hub"
**Cor:** Azul
**Público:** Equipa de Marketing, Conteúdo e Redes Sociais

**Estrutura Mensal Padrão:**

**Semana 1 - Conteúdo Corporativo:**
- **Terça-feira:** Post Blog (09:00 - 11:00)
  - Descrição: Escrever e publicar artigo no blog
  - Responsável: Equipa de Conteúdo
  - Checklist: Pesquisa, redação, revisão, publicação

- **Quinta-feira:** Email Newsletter (14:00 - 15:00)
  - Descrição: Preparar e agendar newsletter semanal
  - Tipo: Conteúdo curatorial, dicas, promoções

**Semana 2 - Redes Sociais:**
- **Segunda-feira:** Planeamento Social Media (10:00 - 11:30)
  - Descrição: Definir conteúdo para a semana
  - Plataformas: Instagram, Facebook, LinkedIn

- **Quarta-feira:** Publicação Social Media (09:00)
  - Descrição: Publicar posts agendados
  - Conteúdo: Mix de educativo, promocional, entretenimento

- **Sexta-feira:** Análise & Engagement (15:00 - 16:30)
  - Descrição: Responder comentários, analisar métricas

**Semana 3 - Campanhas Temáticas:**
- Varia conforme o mês (ver abaixo)

**Semana 4 - Review & Planeamento:**
- **Segunda-feira:** Análise de Desempenho (10:00 - 11:00)
  - Descrição: Revisar métricas do mês, ROI de campanhas

- **Quarta-feira:** Planeamento do Próximo Mês (14:00 - 15:30)
  - Descrição: Definir temas, campanhas, conteúdos

---

### Calendário 2: Promoções e Eventos Especiais

**Nome:** "Calendário de Promoções - Gadget Hub"
**Cor:** Vermelho
**Público:** Equipa de Marketing, Vendas, Gestão

**Eventos Anuais Fixos:**

**Janeiro - Liquidação Pós-Natal:**
- Datas: 2-31 de Janeiro
- Desconto: 15-40% em categorias selecionadas
- Eventos:
  - 1 Janeiro: Configurar promoção em Shopify
  - 2 Janeiro: Publicar anúncio redes sociais
  - 15 Janeiro: Publicar email lembrança (ofertas a acabar)
  - 29 Janeiro: Último dia - email urgência

**Fevereiro - Dia dos Namorados:**
- Data: 14 de Fevereiro
- Desconto: 10% em produtos selecionados (acessórios, gadgets presentes)
- Eventos:
  - 3 Fevereiro: Design de campanhas
  - 7 Fevereiro: Publicar anúncios
  - 10 Fevereiro: Email principal
  - 13 Fevereiro: Última lembrança
  - 14 Fevereiro: Email "Última Chance"

**Março - Páscoa:**
- Data: Varia (calendário lunar) - ~16 Março 2026
- Desconto: 12% em produtos família
- Eventos:
  - 20 dias antes: Planeamento
  - 10 dias antes: Publicação redes sociais
  - 7 dias antes: Email principal
  - 1 dia antes: Email lembrança

**Abril a Maio - Dia da Terra / Verão:**
- Data: 22 de Abril + Primavera (21 Março - 20 Junho)
- Desconto: 10% em produtos eco-friendly
- Temas: Sustentabilidade, gadgets outdoor

**Junho/Julho - Black Friday (Preparação):**
- Data: Preparação em Junho para Julho
- Eventos: Análise de fornecedores, negociação de preços

**Agosto - Back to School:**
- Data: Última semana Agosto (22-31)
- Desconto: 15% em gadgets educacionais, presentes
- Targets: Estudantes, pais
- Eventos:
  - 15 Agosto: Início da campanha
  - 22 Agosto: Peak campaign
  - 28 Agosto: Última lembrança

**Setembro - Aniversário Gadget Hub:**
- Data: 15 de Setembro (customizar conforme datas reais)
- Desconto: 20% especial aniversário
- Eventos:
  - Mês anterior: Planeamento de mega-campanha
  - 1 Setembro: Teaser nos sociais
  - 10 Setembro: Anúncio oficial
  - 15 Setembro: Pico de promossão
  - 22 Setembro: Final da promoção

**Outubro - Halloween:**
- Data: 31 de Outubro
- Desconto: 10% em gadgets "assustadores" ou temáticos
- Estilo: Lúdico, criativo nas redes sociais

**Novembro - Black Friday (Principal):**
- Data: 28 de Novembro 2026 (último sexta-feira de Novembro)
- Desconto: Até 50% em categorias selecionadas
- Eventos:
  - 1 Novembro: Preparar site/inventory
  - 15 Novembro: Email teaser
  - 21 Novembro: Início de campanhas agressivas
  - 27 Novembro: Último email antes
  - 28 Novembro: Black Friday em direto
  - 29-30 Novembro: Cyber Monday continuação

**Dezembro - Natal:**
- Datas: 1-24 de Dezembro
- Desconto: 15-25% conforme semana
- Eventos:
  - 1 Dezembro: Calendário do Advento nos sociais
  - 1-15 Dezembro: Campanhas crescentes
  - 15-20 Dezembro: Urgência (entrega até Natal)
  - 21-24 Dezembro: Última chance
  - 25-26 Dezembro: Agradecimentos

**Lembretes Semanais no Calendário:**
- Cada terça-feira: "Revisão de Promoções Ativas"
- Cada sexta-feira: "Análise de Conversão da Semana"

---

### Calendário 3: Lembretes de Restock

**Nome:** "Lembretes de Restock - Gadget Hub"
**Cor:** Verde
**Público:** Gestor de Inventário, Compras

**Estrutura:**

**Verificações Semanais:**
- **Cada Segunda-feira 09:00** - "Revisão Stock Crítico"
  - Verificar produtos com menos de 10 unidades
  - Contactar fornecedores se necessário
  - Duração: 1 hora

- **Cada Quarta-feira 14:00** - "Análise de Rotatividade"
  - Verificar quais produtos se vendem mais
  - Priorizar restock dos best-sellers
  - Duração: 1 hora

- **Cada Sexta-feira 10:00** - "Planeamento de Encomendas"
  - Consolidar encomendas a fornecedores
  - Verificar ETA de entregas anteriores
  - Duração: 1,5 horas

**Verificações Mensais:**
- **Primeiro Dia do Mês 09:00** - "Auditoria Completa de Stock"
  - Conferir todas as quantidades
  - Identificar produtos com baixo movimento
  - Duração: 2 horas

- **Dia 15 do Mês 14:00** - "Projeção de Stock Próximo Mês"
  - Analisar tendências de vendas
  - Prever necessidades para campanhas (promoções agendadas)
  - Duração: 1,5 horas

**Eventos Sazonais:**
- **Julho**: Preparação para Black Friday (restock massivo)
- **Outubro**: Preparação para Natal (restock massivo)
- **Maio**: Limpeza de stock low-moving items (preparar espaço)

**Notificações:**
- Alerta automático 24 horas antes de cada evento
- Lembretes: 1 dia antes (email Slack no #alertas)

---

## Templates de Email (Gmail)

### Template 1: Confirmação de Encomenda

**Assunto:** "Obrigado por sua encomenda, {{customer_first_name}}! Encomenda #{{order_number}}"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Obrigado por sua encomenda na Gadget Hub! 🎉

Estamos delighted a processar seu pedido. Aqui está um resumo:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 DETALHES DA ENCOMENDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Número de Encomenda: #{{order_number}}
Data do Pedido: {{order_date}}
Status: Confirmado ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PRODUTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{#items}}
• {{item_name}} (Quantidade: {{item_quantity}})
  Preço: €{{item_price}} x {{item_quantity}} = €{{item_total}}
{{/items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 RESUMO FINANCEIRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subtotal: €{{subtotal}}
Portes de Envio: €{{shipping_cost}}
{{#discount}}Desconto: -€{{discount_amount}}{{/discount}}
─────────────────────
TOTAL: €{{order_total}}

Método de Pagamento: {{payment_method}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 MORADA DE ENTREGA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{shipping_name}}
{{shipping_address}}
{{shipping_city}}, {{shipping_postal_code}}
{{shipping_country}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Próximos Passos:
1. Sua encomenda está a ser processada
2. Em breve, receberá um email com o número de rastreamento
3. Pode acompanhar seu envio em tempo real

Se tem dúvidas sobre sua encomenda, responda a este email ou contacte-nos em support@gadethub.pt

Obrigado por escolher Gadget Hub! 💚

Atenciosamente,
Equipa Gadget Hub
www.gadethub.pt
```

**Configuração:**
- From: noreply@gadethub.pt
- Sender Name: Gadget Hub
- Reply-To: support@gadethub.pt
- Categoria: Transacional
- Integração Zapier: Gmail > Send Email

---

### Template 2: Envio Realizado (Com Tracking)

**Assunto:** "Sua encomenda saiu! Rastreie seu pedido #{{order_number}}"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Excelentes notícias! 📦 Sua encomenda acaba de sair do nosso armazém!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 RASTREAMENTO DO ENVIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Número de Rastreamento: {{tracking_number}}
Transportadora: {{carrier_name}}
Data de Envio: {{shipment_date}}

[👉 ACOMPANHE SEU ENVIO AQUI 👈]
{{tracking_url}}

Tempo Estimado de Entrega: {{estimated_delivery_date}}
(Pode variar consoante localização e condições externas)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RESUMO DA ENCOMENDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Número de Encomenda: #{{order_number}}

Produtos Enviados:
{{#items}}
✓ {{item_name}} ({{item_quantity}}x)
{{/items}}

Morada de Entrega:
{{shipping_name}}
{{shipping_address}}
{{shipping_city}}, {{shipping_postal_code}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 DICAS ÚTEIS:
• Acompanhe seu envio clicando no link de rastreamento
• Certifique-se que alguém está presente na morada de entrega
• Guarde o número de rastreamento para futuras referências
• Inspecione a embalagem quando receber

❓ PERGUNTAS?
Se tem problemas com o rastreamento ou o envio, não hesite em contactar-nos:
📧 support@gadethub.pt
📞 +351 XXX XXX XXX
🕐 Segunda a Sexta, 09:00-17:00 CET

Obrigado por escolher Gadget Hub!

Atenciosamente,
Equipa Gadget Hub
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Shopify > Fulfillment (quando tracking está disponível)
- Envio Automático: Imediato após preenchimento de tracking

---

### Template 3: Follow-up Pós-Compra (7 Dias Depois)

**Assunto:** "Como correu com seu pedido, {{customer_first_name}}? Sua opinião importa!"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Espero que tenha recebido sua encomenda #{{order_number}} em boas condições! 📦

Já teve oportunidade de testar os produtos? Gostaríamos de saber sua opinião!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ DEIXE SUA AVALIAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sua feedback é extremamente importante para nós! Ajuda-nos a melhorar.

[👉 AVALIAR MINHA ENCOMENDA 👈]
{{review_url}}

Leva apenas 2 minutos! ⏱️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 AGRADECIMENTO ESPECIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Como agradecimento por sua compra, oferecemos-lhe um desconto de 10%
para sua próxima compra!

Código de Desconto: GADGET10{{customer_id}}
Válido por 30 dias
Aplicar no checkout: www.gadethub.pt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 TEVE ALGUM PROBLEMA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se o produto não correspondia ao esperado, temos uma política de devolução
de 30 dias, sem perguntas. Basta contactar-nos:

📧 support@gadethub.pt
📞 +351 XXX XXX XXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Obrigado por ser parte da comunidade Gadget Hub! 💚

Atenciosamente,
Equipa Gadget Hub
www.gadethub.pt
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Shopify > Fulfillment + 7 dias delay
- Condicional: Apenas se cliente não deixou review ainda

---

### Template 4: Welcome Email (Nova Subscrição Newsletter)

**Assunto:** "{{customer_first_name}}, bem-vindo à Gadget Hub! 🎉 Desconto exclusivo espera por ti"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Bem-vindo à Gadget Hub! 🎉

Estamos deliciados por ter-se juntado à nossa comunidade de 10.000+ amantes de gadgets!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 PRESENTE DE BOAS-VINDAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apenas para si, novo membro, oferecemos:

💚 15% de DESCONTO na sua primeira compra!

Código: BEMVINDO15
Válido por 30 dias em toda a loja

[👉 APROVEITAR DESCONTO 👈]
https://www.gadethub.pt/?code=BEMVINDO15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ QUEM SOMOS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gadget Hub é sua loja online de referência para os melhores gadgets,
tecnologia e acessórios inovadores. Desde 2018, ajudamos clientes em toda
Portugal a descobrir produtos que transformam suas vidas.

✓ +5.000 produtos em stock
✓ Entrega em 24-48h em Portugal
✓ Garantia em todos os produtos
✓ Devoluções fáceis (30 dias)
✓ Apoio ao cliente 5 dias por semana

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 PRÓXIMAS NO SEU EMAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enquanto subscriber, receberá:

📧 Newsletter Semanal
   → Dicas de produtos, tutoriais, novidades

💰 Oferta Exclusivas
   → Descontos apenas para subscribers

🎯 Conteúdo Curatorial
   → Análises, reviews, guias de compra

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 PRODUTOS EM DESTAQUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{#featured_products}}
• {{product_name}} - €{{product_price}}
  {{product_description}}
  [Ver Produto]
{{/featured_products}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Siga-nos também nas redes sociais:
🔗 Facebook: facebook.com/gadethub.pt
📷 Instagram: instagram.com/gadethub.pt
🐦 Twitter: twitter.com/gadethub_pt

Obrigado por escolher Gadget Hub!

Atenciosamente,
João Silva
CEO & Fundador, Gadget Hub
```

**Configuração:**
- From: marketing@gadethub.pt
- Sender Name: Gadget Hub
- Trigger: Website Form > New Newsletter Subscription
- Envio: Imediato após subscrição
- Adicionar Tags: newsletter, new-subscriber

---

### Template 5a: Carrinho Abandonado - Email 1 (Após 1 hora)

**Assunto:** "Esqueceu seu carrinho? Os produtos ainda estão à espera! 🛒"

**Corpo (HTML):**

```
Olá,

Notamos que deixou alguns gadgets incríveis no seu carrinho!

Não se preocupe - ainda estão reservados para si pelos próximos 24 horas.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛒 SEUS PRODUTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{#items}}
📦 {{product_name}}
   Preço: €{{product_price}}
   Quantidade: {{quantity}}
{{/items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 TOTAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subtotal: €{{cart_subtotal}}
Portes: €{{shipping_cost}} (grátis acima de €50)
Total: €{{cart_total}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[👉 COMPLETAR MEU CARRINHO 👈]
{{cart_recovery_url}}

Compre agora com confiança:
✓ Entrega rápida (24-48h)
✓ Garantia total dos produtos
✓ Devoluções fáceis

Até breve! 😊

Gadget Hub
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Shopify > Abandoned Cart
- Delay: 1 hora exata
- Condicional: Cart value > €10

---

### Template 5b: Carrinho Abandonado - Email 2 (Após 24 horas)

**Assunto:** "Espera - oferecemos 5% de DESCONTO para completar sua encomenda!"

**Corpo (HTML):**

```
Olá,

Ainda está pensando nos produtos que deixou no seu carrinho?

Temos uma surpresa para si! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💚 5% DE DESCONTO - SÓ PARA VOCÊ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Código: CARRINHO5
Válido por 24 horas

PREÇO ORIGINAL: €{{cart_total}}
COM DESCONTO: €{{cart_total_discount}}
ECONOMIA: €{{discount_amount}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ POR QUE ESCOLHER ESTES PRODUTOS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{#items}}
{{product_name}}
⭐⭐⭐⭐⭐ ({{review_count}} avaliações)
"{{customer_review_snippet}}"

{{/items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[👉 COMPRAR COM 5% DESCONTO 👈]
{{cart_recovery_url_with_code}}

Entregaremos em 24-48 horas!

Abç,
Gadget Hub
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Email 1 enviado + 24 horas
- Condicional: Se cliente ainda não completou compra
- Desconto: Código de 5% gerado automaticamente

---

### Template 5c: Carrinho Abandonado - Email 3 (Após 72 horas)

**Assunto:** "⏰ ÚLTIMA OPORTUNIDADE - 10% desconto termina em 24h!"

**Corpo (HTML):**

```
Olá,

⏰ Esta é sua ÚLTIMA CHANCE!

O desconto especial de 10% que reservamos apenas para si vence em 24 horas.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 DESCONTO DE 10% - HOJE É O ÚLTIMO DIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Código: GANHE10
Válido até hoje à meia-noite (00:00)

PREÇO ORIGINAL: €{{cart_total}}
COM 10% DESCONTO: €{{cart_total_discount_10}}
ECONOMIZA: €{{discount_amount_10}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ NÃO PERCA TEMPO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[👉 FINALIZAR COMPRA AGORA 👈]
{{cart_recovery_url_with_discount_code}}

{{#items}}
✓ {{product_name}}
{{/items}}

Garantia completa - Devolução em 30 dias se não ficar satisfeito.

Ação rápida! ⚡

Gadget Hub
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Email 2 enviado + 48 horas
- Condicional: Se cliente ainda não completou compra
- Desconto: Código de 10% (maior incentivo)
- Prioridade: Alta (pode incluir emoji urgência)

---

### Template 6: Resposta Genérica a Dúvidas

**Assunto:** "Respondemos à sua pergunta sobre {{topic}}"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Obrigado por nos contactar! 😊

Recebemos sua pergunta sobre {{topic}} e aqui está a resposta:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SUA PERGUNTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"{{customer_question}}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 NOSSA RESPOSTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{support_response}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 RECURSOS ÚTEIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Guia de Devolução: https://www.gadethub.pt/returns
• Políticas de Envio: https://www.gadethub.pt/shipping
• Garantia: https://www.gadethub.pt/warranty
• FAQ: https://www.gadethub.pt/faq

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ficou com mais dúvidas? Responda a este email e teremos prazer em ajudar!

Atenciosamente,
Equipa de Apoio ao Cliente - Gadget Hub
📧 support@gadethub.pt
📞 +351 XXX XXX XXX
🕐 Segunda a Sexta, 09:00-17:00 CET
```

**Configuração:**
- From: support@gadethub.pt
- Tipo: Template com campos personalizáveis
- Uso: Resposta a emails via Help Desk/Formulário de Contacto
- Variáveis: {{customer_first_name}}, {{topic}}, {{customer_question}}, {{support_response}}

---

### Template 7: Contacto com Fornecedores

**Assunto:** "Gadget Hub - Pedido de Restock / Informação de Produto"

**Corpo (English):**

```
Dear {{supplier_name}},

We hope this message finds you well!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 REQUEST DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Request Type: {{request_type}} (Restock/Product Info/Quote/Other)
Date: {{current_date}}
Reference: {{reference_code}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 PRODUCTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{#items}}
Product: {{product_sku}} - {{product_name}}
Quantity Requested: {{quantity_requested}}
Preferred Delivery: {{preferred_delivery_date}}
{{/items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 CONTACT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Company: Gadget Hub, Lda.
Contact: {{contact_person}}
Email: {{sender_email}}
Phone: {{sender_phone}}
Address: {{sender_address}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please confirm availability and provide pricing and estimated delivery date.

Thank you for your partnership!

Best regards,

{{sender_name}}
Gadget Hub Procurement Team
procurement@gadethub.pt
```

**Configuração:**
- From: procurement@gadethub.pt
- Tipo: Manual (envio ad-hoc)
- Destinatário: Email do fornecedor
- Campos obrigatórios: {{supplier_name}}, {{request_type}}, {{items}}

---

### Template 8: Pedido de Review/Avaliação

**Assunto:** "Sua opinião é valiosa! Avalie {{product_name}} 🌟"

**Corpo (HTML):**

```
Olá {{customer_first_name}},

Já tem a sua encomenda #{{order_number}}? Esperamos que esteja muito feliz! 😊

{{#product_purchased}}
Gostaria de pedir um pequeno favor: avalie {{product_name}} para ajudar outros clientes.

Suas avaliações genuínas ajudam-nos a melhorar e ajudam outros clientes a tomar as melhores decisões.

[👉 DEIXAR AVALIAÇÃO EM 30 SEGUNDOS 👈]
{{review_url}}

Prêmio: Cada review deixa o seu nome numa rifa mensal para ganhar €50 em crédito!
{{/product_purchased}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ COMO AVALIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Clique no link acima
2. Deixe uma classificação (1-5 estrelas)
3. Escreva sua opinião (opcional, mas muito apreciado)
4. Submeta

Leva menos de 1 minuto!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Obrigado por apoiar Gadget Hub! 💚

Atenciosamente,
Equipa Gadget Hub
```

**Configuração:**
- From: noreply@gadethub.pt
- Trigger: Shopify > Order + 14 dias
- Condicional: Apenas se cliente não deixou review
- Frequência: Uma única vez por encomenda

---

## Configuração Notion

### Dashboard Principal - Gadget Hub

**Nome:** "Dashboard Gadget Hub"
**Tipo:** Database com múltiplas Views e widgets

**Estrutura do Dashboard:**

```
GADGET HUB - DASHBOARD EXECUTIVO

┌─────────────────────────────────────────────────────┐
│ 📊 MÉTRICAS DO MÊS                                  │
├─────────────────────────────────────────────────────┤
│ Receita: €45.234                                    │
│ Encomendas: 234                                     │
│ Ticket Médio: €193                                  │
│ Taxa Conversão: 2.8%                                │
│ Clientes Novos: 45                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🔴 ALERTAS CRÍTICOS                                 │
├─────────────────────────────────────────────────────┤
│ ⚠️  5 produtos com stock < 5 unidades              │
│ ⚠️  2 fornecedores com atraso                      │
│ ⚠️  Newsletter: taxa abertura em queda             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📅 PRÓXIMAS CAMPANHAS                               │
├─────────────────────────────────────────────────────┤
│ 15/04 - Dia da Terra (desconto 10%)                │
│ 22/05 - Verão (liquidação stock)                   │
│ 15/09 - Aniversário Loja (desconto 20%)            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🎯 TAREFAS EM PROGRESSO                             │
├─────────────────────────────────────────────────────┤
│ [Em Progresso] Implementar checkout one-click      │
│ [Em Progresso] Expandir categoria de acessórios    │
│ [A Começar] Integração com fornecedor novo        │
└─────────────────────────────────────────────────────┘
```

---

### Base de Dados de Produtos

**Nome:** "Produtos Gadget Hub"
**Tipo:** Database Notion

**Campos:**

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| Nome | Title | Nome do produto | Apple AirPods Pro |
| SKU | Text | Código único | SKU-2024-001 |
| Categoria | Select | Categoria do produto | Áudio, Wearables, Smart Home, etc. |
| Fornecedor | Relation | Link para DB Fornecedores | Supplier Tech |
| Preço Custo | Currency | Custo de compra | €100 |
| Preço Venda | Currency | Preço venda ao público | €199 |
| Margem | Formula | (Venda-Custo)/Venda×100 | 49.7% |
| Stock Atual | Number | Quantidade em stock | 15 |
| Stock Mínimo | Number | Nível para alerta | 5 |
| Estado | Select | Ativo/Inativo/Descontinuado | Ativo |
| Data de Criação | Created Time | Data adição | 2024-04-01 |
| Última Atualização | Last Edited Time | Última modificação | 2024-04-06 |
| Descrição Curta | Text | Descrição para loja | "Auriculares premium com ANC" |
| Imagem | File | Imagem do produto | [file] |
| URL Shopify | URL | Link para produto | https://gadethub.pt/products/... |
| Avaliação Média | Number | Rating 1-5 | 4.8 |
| Reviews | Number | Quantidade de reviews | 156 |
| Peso (kg) | Number | Para cálculo portes | 0.25 |
| Dimensões | Text | Embalagem | 15x10x5 cm |
| Notas | Text | Anotações internas | "Best seller, fazer restock urgente" |

**Views Recomendadas:**

1. **Todos os Produtos** (Table view)
   - Sortido por: Categoria, depois Preço Venda
   - Filtro: Estado = "Ativo"

2. **Stock Crítico** (List view)
   - Filtro: Stock Atual < Stock Mínimo
   - Destaque: Vermelho para urgência

3. **Best Sellers** (Gallery view)
   - Filtro: Reviews > 50 & Avaliação >= 4.5
   - Ordenado por: Reviews DESC

4. **Margem de Lucro** (Table view)
   - Ordenado por: Margem DESC
   - Cálculo automático

---

### Calendário Editorial - Notion

**Nome:** "Calendário Editorial - Gadget Hub"
**Tipo:** Database com Calendar view

**Campos:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Título | Title | Título do conteúdo |
| Data | Date | Data de publicação |
| Tipo | Select | Blog Post, Social Media, Email, Video, Infographic |
| Plataformas | Multi-select | Facebook, Instagram, LinkedIn, Blog, Email |
| Status | Select | Ideação, Rascunho, Revisão, Agendado, Publicado, Arquivado |
| Autor | Person | Quem criou |
| Editor | Person | Quem revê |
| Descrição | Text | Conteúdo/outline |
| Tags | Multi-select | Tecnologia, Dicas, Oferta, Educacional, Entretenimento |
| URL Publicado | URL | Link para conteúdo publicado |
| Métricas | Text | Engagement, views, clicks |
| Observações | Text | Notas internas |

**Estrutura Mensal:**

```
ABRIL 2026 - CALENDÁRIO EDITORIAL

Semana 1:
├─ 02/04 (Terça) - Blog Post: "Guia de Compra - Auriculares 2024"
├─ 04/04 (Quinta) - Email Newsletter: "Destaques da Semana"
└─ 05/04 (Sexta) - Social: "Tips para limpar gadgets"

Semana 2:
├─ 08/04 (Seg) - Social: Planeamento semanal
├─ 10/04 (Qua) - Social: Posts diários agendados
├─ 12/04 (Sexta) - Email: Black Friday Teaser
└─ 13/04 (Sáb) - Video: Unboxing novo produto

Semana 3:
├─ 15/04 (Seg) - Dia da Terra - Campanha tema
├─ 17/04 (Qua) - Blog: "Gadgets Eco-Friendly"
└─ 20/04 (Sáb) - Social: Promoção finaliza

Semana 4:
├─ 22/04 (Seg) - Análise de desempenho
├─ 24/04 (Qua) - Planeamento Maio
└─ 26/04 (Sexta) - Email: Review mensal
```

---

### CRM de Clientes - Notion

**Nome:** "CRM Clientes - Gadget Hub"
**Tipo:** Database com múltiplas views

**Campos:**

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| Nome | Title | Nome completo | João Silva |
| Email | Email | Email principal | joao@example.com |
| Telefone | Phone | Contacto telefónico | +351 912 345 678 |
| Data de Subscrição | Date | Quando aderiu | 2024-03-15 |
| Fonte | Select | Como nos encontrou | Google, Redes Sociais, Recomendação, Direto |
| Status | Select | Ativo, Inativo, VIP, Bloqueado | Ativo |
| Total Gasto | Currency | Valor total compras | €450 |
| Número Compras | Number | Histórico de encomendas | 5 |
| Ticket Médio | Formula | Total Gasto / Nº Compras | €90 |
| Última Compra | Date | Quando comprou por último | 2024-04-01 |
| Dias Sem Comprar | Formula | Dias desde última compra | 5 |
| Interesses | Multi-select | Categorias de interesse | Áudio, Smart Home, Wearables |
| Tags | Multi-select | Markers internos | Newsletter, VIP, Reclamante, Influencer |
| Notas | Text | Observações CRM | "Cliente premium, aberto a promos" |
| Risco de Churn | Select | Baixo, Médio, Alto | Baixo |
| Newsletter | Checkbox | Subscrito a newsletter? | ✓ |
| Restock Reminders | Checkbox | Notificações de restock | ✓ |
| Última Atualização | Last Edited Time | Quando foi atualizado | 2024-04-06 |

**Views Recomendadas:**

1. **Clientes Ativos** (Table)
   - Filtro: Status = "Ativo"
   - Ordenado por: Total Gasto DESC

2. **VIPs** (Table)
   - Filtro: Status = "VIP" | Total Gasto > €500
   - Destaque especial

3. **Em Risco de Perda** (List)
   - Filtro: Dias Sem Comprar > 90 & Total Gasto > €100
   - Ação: Email re-engagement

4. **Newsletter Subscribers** (Table)
   - Filtro: Newsletter = ✓
   - Rastreamento de engajamento

---

## Estrutura de Canais Slack

### Canais Recomendados

#### 1. #vendas

**Propósito:** Notificações de vendas, encomendas e relacionamento com cliente

**Triggers Automáticos:**
- Nova encomenda criada
- Ordem processada
- Entrega confirmada
- Nova review positiva
- Cliente fez compra recorrente

**Formato de Mensagem:**
```
📦 Nova Encomenda #12345
Cliente: João Silva (joao@example.com)
Produtos: AirPods Pro (1x), Carregador Rápido (2x)
Total: €298,50
Status: Confirmado ✓
🔗 Processar em Shopify
```

**Membros:** Gestor de vendas, equipa de fulfillment, gerente loja

**Notificações:** Ativas (som)

---

#### 2. #alertas

**Propósito:** Alertas críticos de sistema, stock, erros

**Triggers Automáticos:**
- Stock abaixo de limite crítico
- Fornecedor com atraso
- Erro de pagamento
- Falha em automação Zapier
- Taxa de devolução elevada

**Formato de Mensagem:**
```
🚨 ALERTA STOCK CRÍTICO
Produto: iPhone 15 Pro Max
Quantidade: 3 unidades
Fornecedor: TechImports PT
Status: Restock urgente necessário
🔗 Ver em Notion
```

**Membros:** Gestor inventário, gestor loja, CTO

**Notificações:** Ativas com menção @channel

---

#### 3. #marketing

**Propósito:** Campanhas, métricas, estratégia de marketing

**Triggers Automáticos:**
- Campanha iniciada/finalizada
- Métricas de newsletter
- Desempenho de redes sociais
- Novo conteúdo publicado
- A/B test resultados

**Formato de Mensagem:**
```
📊 Relatório Newsletter - Semana 1-7 Abril
Assunto: "Bem-vindo à Gadget Hub"
Taxa Abertura: 32% (vs média 22%)
Taxa Clique: 8.5% (vs média 5%)
Conversão: 12 novas compras (+€2.340)
✅ Campanha super bem-sucedida!
```

**Membros:** Marketing manager, copywriter, social media, designer

**Notificações:** Padrão

---

#### 4. #geral

**Propósito:** Comunicação geral da equipa, anúncios, social

**Conteúdo:**
- Anúncios de empresa
- Comunicados de políticas
- Celebrações e marcos
- Discussões gerais

**Membros:** Todos

**Notificações:** Padrão

---

#### 5. #operacoes (Opcional)

**Propósito:** Fulfillment, logística, operações

**Triggers Automáticos:**
- Encomenda pronta para envio
- Rastreamento atualizado
- Devolução recebida
- Problema de fulfillment

**Membros:** Equipa fulfillment, logística, warehouse

---

### Bots Slack Recomendados

1. **Zapier Bot** - Para notificações automáticas
2. **Notion Bot** - Para integração de databases
3. **Google Calendar Bot** - Para lembretes de eventos
4. **Custom Bot** - Para alertas de Shopify

---

## Checklist de Implementação

### Fase 1: Preparação (Semana 1)

- [ ] **Gmail Setup**
  - [ ] Criar conta Gmail corporativa (noreply@gadethub.pt)
  - [ ] Configurar assinatura de email padrão
  - [ ] Criar conta support@gadethub.pt
  - [ ] Criar conta marketing@gadethub.pt

- [ ] **Notion Setup**
  - [ ] Criar workspace Gadget Hub
  - [ ] Convidar membros da equipa
  - [ ] Criar databases principais (Produtos, Clientes, Editorial)
  - [ ] Criar Dashboard executivo
  - [ ] Testar permissões de acesso

- [ ] **Slack Setup**
  - [ ] Criar workspace Gadget Hub
  - [ ] Criar canais (#vendas, #alertas, #marketing, #geral)
  - [ ] Configurar notificações
  - [ ] Testar integração Zapier

### Fase 2: Integração Zapier (Semana 2)

- [ ] **Workflow 1: Nova Encomenda**
  - [ ] Conectar Shopify a Zapier
  - [ ] Configurar trigger (New Order)
  - [ ] Testar Gmail action
  - [ ] Testar Slack action
  - [ ] Testar Google Calendar action
  - [ ] Ativar workflow

- [ ] **Workflow 2: Novo Produto**
  - [ ] Configurar trigger (New Product)
  - [ ] Testar Social Media posting
  - [ ] Testar Notion database entry
  - [ ] Ativar workflow

- [ ] **Workflow 3: Stock Crítico**
  - [ ] Configurar trigger (Inventory < 5)
  - [ ] Testar Email alerta
  - [ ] Testar Slack alerta
  - [ ] Ativar workflow

- [ ] **Workflow 4: Review de Cliente**
  - [ ] Configurar trigger (New Review)
  - [ ] Testar Slack notification
  - [ ] Testar Email agradecimento
  - [ ] Ativar workflow

### Fase 3: Email & Communication (Semana 3)

- [ ] **Templates Gmail**
  - [ ] Criar Template 1 - Confirmação Encomenda
  - [ ] Criar Template 2 - Envio com Tracking
  - [ ] Criar Template 3 - Follow-up 7 dias
  - [ ] Criar Template 4 - Welcome Newsletter
  - [ ] Criar Templates 5a/5b/5c - Carrinho Abandonado
  - [ ] Criar Template 6 - Resposta Genérica
  - [ ] Criar Template 7 - Contacto Fornecedores
  - [ ] Criar Template 8 - Pedido Review

- [ ] **Workflow 5: Carrinho Abandonado**
  - [ ] Configurar 3 emails com delays (1h, 24h, 72h)
  - [ ] Testar sequence completa
  - [ ] Ativar workflow

- [ ] **Workflow 6: Newsletter Subscribers**
  - [ ] Configurar welcome series (3 emails)
  - [ ] Testar Notion CRM entry
  - [ ] Ativar workflow

### Fase 4: Google Calendar (Semana 4)

- [ ] **Calendário Editorial**
  - [ ] Criar calendário em Google Calendar
  - [ ] Adicionar eventos fixos (posts, newsletters)
  - [ ] Configurar notificações (1 dia antes)
  - [ ] Compartilhar com equipa de marketing

- [ ] **Calendário de Promoções**
  - [ ] Criar calendário Google Calendar
  - [ ] Adicionar todos os eventos sazonais
  - [ ] Vincular com Notion Editorial Calendar
  - [ ] Configurar lembretes automáticos

- [ ] **Calendário de Restock**
  - [ ] Criar calendário Google Calendar
  - [ ] Adicionar verificações semanais
  - [ ] Configurar lembretes automáticos
  - [ ] Compartilhar com gestor inventário

### Fase 5: Testes e Otimização (Semana 5-6)

- [ ] **Testes de Ponta a Ponta**
  - [ ] Fazer teste de compra completo
  - [ ] Verificar todos os emails recebidos
  - [ ] Verificar notificações Slack
  - [ ] Verificar Google Calendar entries
  - [ ] Verificar Notion updates

- [ ] **Otimizações**
  - [ ] Ajustar templates baseado em feedback
  - [ ] Calibrar delays de email
  - [ ] Otimizar formatação de mensagens Slack
  - [ ] Testar em diferentes dispositivos/clientes email

- [ ] **Documentação**
  - [ ] Documentar passwords/tokens de forma segura
  - [ ] Criar guia de troubleshooting
  - [ ] Treinar equipa em workflows
  - [ ] Criar plano de manutenção mensal

### Fase 6: Monitoramento Contínuo

- [ ] **Métricas a Rastrear**
  - [ ] Taxa de abertura de emails (>20%)
  - [ ] Taxa de conversão de carrinho abandonado (>10%)
  - [ ] Tempo de resposta a clientes (<4h)
  - [ ] Satisfação com automações (feedback equipa)

- [ ] **Manutenção Mensal**
  - [ ] Revisar e atualizar templates
  - [ ] Ajustar datas de campanhas sazonais
  - [ ] Analisar métricas de automações
  - [ ] Otimizar sequências com base em dados

---

## Notas Importantes

### Segurança e Compliance

1. **GDPR & Lei Proteção Dados:**
   - Todos os emails devem incluir opção de unsubscribe
   - Guardar apenas dados necessários em Notion
   - Implementar política de retenção de dados

2. **Senhas e Credenciais:**
   - Armazenar em local seguro (não em Notion público)
   - Usar autenticação 2FA em todas as contas
   - Rotar passwords regularmente

3. **Email Compliance:**
   - Sempre incluir morada física da loja
   - Footer com opção de unsubscribe
   - Responder a emails dentro de 24h

### Escalabilidade

- Estrutura Notion e Zapier é escalável até 10.000+ clientes
- Para volumes maiores, considerar integrações adicionais
- Backup mensal recomendado de Notion databases

### Suporte

- Documentação centralizada em Notion
- Equipa treinada em cada workflow
- Responsável de on-call para troubleshooting

---

**Versão:** 1.0
**Última Atualização:** Abril 2026
**Próxima Revisão:** Julho 2026
