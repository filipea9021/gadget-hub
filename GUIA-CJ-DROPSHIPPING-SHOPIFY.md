# Guia - Ligar CJ Dropshipping ao Shopify + Importar Produtos

> **Fornecedor:** CJ Dropshipping (conta ja criada)
> **Plataforma:** Shopify
> **Produtos a importar:** 12 produtos iniciais
> **Margem minima:** 40%
> **Data:** Abril 2026

---

## Pre-requisitos

- [x] Conta CJ Dropshipping criada
- [ ] Loja Shopify activa (plano Basic ou superior)
- [ ] Dominio gadget-hub.com conectado (ver `GUIA-DOMINIO-GODADDY-SHOPIFY.md`)

---

## PARTE 1 - Instalar a App CJ Dropshipping no Shopify

### Passo 1: Instalar a app

1. Acede ao **Shopify Admin** (admin.shopify.com)
2. Vai a **Apps** > **Shopify App Store**
3. Pesquisa por **"CJ Dropshipping"**
4. Clica em **Adicionar app** > **Instalar app**
5. Autoriza as permissoes solicitadas

### Passo 2: Ligar a tua conta CJ

1. Apos instalar, a app abre automaticamente
2. Clica em **Login** e usa as credenciais da tua conta CJ existente
3. Confirma a ligacao entre o CJ e a tua loja Shopify
4. No painel CJ, verifica que aparece o nome da tua loja em **My Shop**

> **Dica:** Se ja tinhas produtos favoritados no CJ antes de ligar ao Shopify, eles aparecem automaticamente na seccao "My Products" da app.

---

## PARTE 2 - Encontrar e Seleccionar Produtos

### Criterios de seleccao (definidos no projecto)

| Criterio | Valor minimo | Motivo |
|----------|-------------|--------|
| Avaliacao | 4.0+ estrelas | Qualidade garantida, menos devoluçoes |
| Margem | 40%+ | Lucro suficiente apos custos de marketing |
| Entrega | Max 15 dias | Aceitavel para mercado europeu |
| Pedidos | 100+ | Produto ja validado pelo mercado |
| Armazem | Europa (preferencial) | Entrega mais rapida para Portugal |

### Passo 3: Pesquisar produtos no CJ

1. Na app CJ no Shopify, vai a **Products** > **Search Products**
2. Usa os filtros:
   - **Category:** Electronics / Smart Home / Accessories
   - **Warehouse:** Selecciona **Europe** (DE, PL, CZ) para entregas mais rapidas
   - **Rating:** 4 estrelas ou mais
   - **Sort by:** Orders (mais vendidos primeiro)

### Produtos-alvo por categoria

O projecto define 12 produtos iniciais, distribuidos por 3 categorias:

| Categoria | Qtd | Exemplos |
|-----------|-----|----------|
| Smart Home | 4 | Smart Plug WiFi, Lampada LED Smart, Sensor de Temperatura, Camera WiFi |
| Audio & Wearables | 4 | Fones TWS Bluetooth 5.3, Smartwatch, Coluna Bluetooth, Headset Gaming |
| Acessorios Tech | 4 | Carregador Wireless 15W, Hub USB-C, Cabo Lightning/USB-C, Suporte Telemovel |

### Passo 4: Validar cada produto

Para cada produto, verifica antes de importar:

1. **Calcula a margem:**
   ```
   Margem = ((Preco de Venda - Preco CJ) / Preco de Venda) x 100
   ```

2. **Exemplo real do projecto:**

   | Produto | Preco CJ | Preco Venda | Margem |
   |---------|----------|-------------|--------|
   | Smart Plug WiFi 16A | 8.00 EUR | 29.90 EUR | 73.2% |
   | Fone TWS Bluetooth 5.3 | 18.00 EUR | 69.90 EUR | 74.2% |
   | Carregador Wireless 15W | 9.00 EUR | 34.90 EUR | 74.2% |

3. **Confirma:**
   - Avaliacao >= 4.0
   - Imagens de boa qualidade (fundo branco, varias angulos)
   - Descricao em ingles (vais traduzir/reescrever para PT)
   - Opcoes de envio para Europa disponiveis

---

## PARTE 3 - Importar Produtos para o Shopify

### Passo 5: Adicionar produtos a lista

1. Na pesquisa do CJ, clica no **icone de coracao** ou **"Add to My Products"** em cada produto escolhido
2. Repete para os 12 produtos

### Passo 6: Publicar na loja Shopify

1. Vai a **My Products** (ou "My List") na app CJ
2. Selecciona os produtos que queres publicar
3. Clica em **"Push to Shopify"** (ou "List to Store")
4. Os produtos aparecem no teu **Shopify Admin** > **Produtos**

### Passo 7: Personalizar cada produto no Shopify

Apos importar, edita cada produto no Shopify:

**Titulo:**
- Traduz para portugues
- Torna-o atractivo (ex: "Smart Plug WiFi 16A" -> "Tomada Inteligente WiFi - Controlo por App e Voz")

**Descricao:**
- Reescreve em portugues com copy persuasiva
- Usa bullet points para beneficios
- Inclui especificacoes tecnicas
- Adiciona informacao de envio

**Preco:**
- Define o preco de venda com margem minima de 40%
- Adiciona o "Compare at price" (preco riscado) com +30-50% para criar urgencia

**Imagens:**
- Usa as melhores imagens do CJ
- Reordena: imagem principal com fundo limpo primeiro
- Remove imagens com texto em chines se existirem

**SEO:**
- Edita o meta titulo e descricao
- Usa palavras-chave em portugues

**Coleccoes:**
- Atribui a coleccao correcta: Smart Home, Audio & Wearables, ou Acessorios Tech

---

## PARTE 4 - Configurar Precos e Margens

### Regra de precos do projecto

```
Preco minimo de venda = Preco CJ / (1 - 0.40) = Preco CJ / 0.60
```

Exemplo: Se o produto custa 10 EUR no CJ, o preco minimo de venda e 10/0.60 = 16.67 EUR.

### Tabela de precos sugerida

| Preco CJ (EUR) | Preco Minimo (40%) | Preco Sugerido | Preco Riscado |
|----------------|-------------------|----------------|---------------|
| 5 - 10 | 8.33 - 16.67 | 24.90 - 29.90 | 39.90 - 49.90 |
| 10 - 20 | 16.67 - 33.33 | 34.90 - 49.90 | 59.90 - 79.90 |
| 20 - 30 | 33.33 - 50.00 | 59.90 - 69.90 | 89.90 - 99.90 |

### Custos a considerar na margem

Nao esquecas de incluir nos calculos:
- Envio CJ -> cliente (se nao for gratis)
- Taxa Shopify (~2% por transaccao)
- Taxa do gateway de pagamento (~1.4% + 0.25 EUR)
- Custo de marketing por venda (objectivo: ~5-8 EUR)

---

## PARTE 5 - Fluxo Automatico de Pedidos

Apos tudo configurado, o fluxo funciona assim:

```
Cliente compra na loja (gadget-hub.com)
        |
Pedido aparece no Shopify + na app CJ automaticamente
        |
Tu confirmas o pedido na app CJ (ou configuras auto-confirm)
        |
CJ processa e envia o produto do armazem
        |
Codigo de rastreamento enviado ao Shopify automaticamente
        |
Cliente recebe email com rastreamento (via Shopify)
        |
Produto entregue ao cliente
```

### Configurar processamento automatico (opcional)

1. Na app CJ: **Settings** > **Order Settings**
2. Activa **Auto-process orders** se quiseres que os pedidos sejam enviados automaticamente
3. Define regras: ex. processar automaticamente pedidos abaixo de 50 EUR

> **Recomendacao:** Comeca com processamento manual nos primeiros 10-20 pedidos para garantir que tudo funciona bem. Depois activa o automatico.

---

## Checklist

- [ ] App CJ Dropshipping instalada no Shopify
- [ ] Conta CJ ligada a loja
- [ ] 12 produtos seleccionados com margem >= 40%
- [ ] Produtos importados para o Shopify ("Push to Shopify")
- [ ] Titulos traduzidos para portugues
- [ ] Descricoes reescritas com copy persuasiva
- [ ] Precos definidos (venda + preco riscado)
- [ ] Imagens organizadas e limpas
- [ ] Coleccoes criadas (Smart Home, Audio, Acessorios)
- [ ] Produto de teste: simular compra e verificar se aparece no CJ
- [ ] Modo de processamento definido (manual ou automatico)

---

## Proximos Passos

Apos importar os produtos:
1. Configurar pagamentos: Shopify Payments, MBWay, PayPal (ver `GUIA-APIs-E-PAGAMENTOS.md`)
2. Testar fluxo completo de compra
3. Lancar campanhas de marketing (TikTok/Meta)
