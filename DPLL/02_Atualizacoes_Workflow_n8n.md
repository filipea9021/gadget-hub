# Atualizações do Workflow n8n - Projeto DPLL

## 🔴 Placeholders que Precisam ser Preenchidos

### 1. Pesquisa de Produtos
**Placeholder:**
```
<__PLACEHOLDER_VALUE__URL da sua API Cerebro Centram (ex: http://localhost:8000/api/skills/pesquisa_produtos)__>
```

**Sugestões para Substituir:**
- **Opção 1 (Fornecedor Direto)**: `https://api.aliexpress.com/v1/products/search`
- **Opção 2 (Seu Backend)**: `http://seu-backend.com/api/pesquisa_produtos`
- **Opção 3 (Agregador)**: `https://api.spocket.com/v1/suppliers/products`

---

### 2. Gerar Conteúdo (LLM)
**Placeholder:**
```
<__PLACEHOLDER_VALUE__URL da API de geracao de conteudo (ex: http://localhost:8000/api/skills/content_generator)__>
```

**Sugestões para Substituir:**
- **OpenAI (ChatGPT)**: `https://api.openai.com/v1/chat/completions`
- **Seu Backend com Claude**: `http://seu-backend.com/api/gerar_descricao`
- **Anthropic Claude API**: `https://api.anthropic.com/v1/messages`

---

### 3. Gerar Imagem (Upsampler)
**Placeholder:**
```
<__PLACEHOLDER_VALUE__Bearer YOUR_UPSAMPLER_API_KEY__>
```

**Já tem:** `https://upsampler.com/api/v1/generate`

**Precisa:** Adicionar chave API de autenticação

---

### 4. Publicar no Shopify
**Placeholder:**
```
<__PLACEHOLDER_VALUE__URL da API Shopify (ex: http://localhost:8000/api/skills/shopify)__>
```

**Sugestões para Substituir:**
- **Shopify Admin API**: `https://seu-store.myshopify.com/admin/api/2024-01/graphql.json`
- **Seu Wrapper**: `http://seu-backend.com/api/shopify/criar_produto`

---

### 5. Campanha de Marketing
**Placeholder:**
```
<__PLACEHOLDER_VALUE__URL da API de marketing (ex: http://localhost:8000/api/skills/marketing)__>
```

**Sugestões para Substituir:**
- **Facebook Ads API**: `https://graph.facebook.com/v19.0/act_XXX/ads`
- **Google Ads API**: `https://googleads.googleapis.com/google.ads.googleads.v18`
- **Seu Wrapper**: `http://seu-backend.com/api/marketing/criar_campanha`

---

## 📋 Plano de Atualização (Ordem de Prioridade)

### FASE 1 - MVP (Essencial)
1. ✅ **Pesquisa de Produtos** → Integrar AliExpress ou Spocket
2. ✅ **Gerar Conteúdo** → Usar OpenAI ou Claude
3. ✅ **Publicar Shopify** → Conectar Shopify Admin API
4. ⚠️ **Gerar Imagem** → Já tem (Upsampler), só falta API Key

### FASE 2 - Crescimento
5. ✅ **Campanha Marketing** → Facebook/Google Ads
6. ✅ **Pagamentos** → Adicionar Stripe/PayPal (nova etapa)
7. ✅ **Email** → Adicionar SendGrid (nova etapa)

### FASE 3 - Escala
8. ✅ **Logística** → Adicionar CTT/DHL (nova etapa)
9. ✅ **CRM** → Adicionar HubSpot (nova etapa)

---

## 🔧 Próximos Passos

**Opção 1: Você preenche os placeholders**
- Dê-me as URLs/chaves das suas APIs
- Eu atualizo o workflow com os valores reais

**Opção 2: Eu crio um novo workflow otimizado**
- Baseado na estrutura DPLL completa
- Com todas as integrações desde o início
- Pronto para rodar teste completo

---

## 📌 Informações que Preciso de Você

Para atualizar o workflow, me diga:

1. **Pesquisa de Produtos**: Qual fornecedor quer usar? (AliExpress, Spocket, outro?)
2. **Gerar Conteúdo**: OpenAI, Claude, ou seu próprio backend?
3. **Shopify**: Tem loja Shopify? Qual é o domínio?
4. **Marketing**: Quer usar Facebook Ads, Google Ads, ou seu próprio sistema?
5. **API Keys**: Tem alguma chave já gerada?

---

**Me diz como quer proceder! 👉**
