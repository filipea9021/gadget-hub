// =====================================================
// MANUAL-OPERACAO.md — Guia da Equipe
// =====================================================

# 📘 Manual de Operação — Gadget Hub Agentes

## 🎯 O que o sistema faz?

O sistema gerencia automaticamente sua loja Shopify:

1. **Busca produtos** (CJ Dropshipping)
2. **Valida critérios** (margem 40%+, avaliação 4+, estoque)
3. **Cria na Shopify** (título, descrição, preço, imagens)
4. **Ajusta preços** (automático baseado em margem)
5. **Monitora estoque** (alerta quando baixo)
6. **Gera relatórios** (vendas, produtos, lucros)

---

## 🚀 Como colocar pra rodar?

### 1. Iniciar Sistema

```bash
cd agentes

# Modo Produção (recomendado)
npm run producao

# Ou modo manual
node main.js
```

### 2. Acompanhar Dashboard

Abra no navegador:
```
http://localhost:3001
```

O que você verá:
- **Stats Cards**: Agentes ativos, produtos, operações pendentes
- **Gráficos**: Produtos por dia, execuções por agente, logs
- **Tabela de Agentes**: Status, última execução, controles
- **Produtos Recentes**: Lista dos últimos importados
- **Logs em Tempo Real**: Tudo que o sistema está fazendo

---

## ⏱️ O que acontece automaticamente?

| Quando | O que faz | Agente |
|--------|-----------|--------|
| A cada 60 min | Busca novos produtos no CJ | Agente CJ |
| A cada 30 min | Cria produtos na Shopify | Agente Shopify |
| A cada 30 min | Atualiza estoque | Agente Estoque |
| A cada 2 horas | Ajusta preços | Agente Preços |
| A cada 3 horas | Gera campanhas marketing | Agente Marketing |

---

## 📦 Fluxo de Importação

```
CJ Dropshipping → Validação → Shopify
     ↓              ↓           ↓
  Busca produto  Score 85+   Produto criado
  Preço: $10     Margem 50%  Preço: $24.90
  Estoque: 100   OK!         Venda ativa
```

### Critérios de Validação

Produto só é importado se:
- ✅ Margem mínima: **40%**
- ✅ Avaliação mínima: **4.0 estrelas**
- ✅ Pedidos mínimos: **100 vendas**
- ✅ Estoque mínimo: **10 unidades**
- ✅ Score final: **70+ pontos**

---

## 🎮 Comandos do Sistema

### Modo Semi-Autônomo (quando iniciar `node main.js`)

```javascript
// Ver status de todos os agentes
status()

// Executar agente específico
executar('cj-dropshipping')     // Buscar produtos CJ
executar('shopify')             // Processar fila Shopify
executar('estoque')             // Verificar estoque
executar('precos')            // Ajustar preços
executar('marketing')         // Gerar campanhas

// Iniciar execução contínua
iniciar()

// Parar todos os agentes
parar()
```

### Dashboard Web

Botões disponíveis:
- **"Iniciar Todos"** → Começa execução automática
- **"Parar Todos"** → Pausa todos os agentes
- **"Executar"** (por agente) → Roda manualmente
- **"Atualizar"** (produtos/logs) → Recarrega dados

---

## 📊 Configurações Importantes

### Arquivo `.env`

```env
# Modo de operação
MODO=autonomo           # autonomo | semi | manual

# Shopify (já configurado)
SHOPIFY_SHOP_DOMAIN=gadget-hub.myshopify.com
SHOPIFY_ACCESS_TOKEN=seu_token_aqui

# CJ (modo demonstração até API funcionar)
CJ_API_KEY=CJ5298786@api@...
CJ_EMAIL=filipeazevedo791@gmail.com

# Dashboard
DASHBOARD_PORT=3001

# Notificações (opcional)
WEBHOOK_URL=https://hooks.slack.com/...
NOTIFICATION_EMAIL=admin@gadget-hub.com
```

### Ajustar Critérios

No arquivo `main.js`, altere `CONFIG.limites`:

```javascript
limites: {
    margemMinima: 40,      // % mínima de lucro
    estoqueMinimo: 5,      // alerta quando estoque < 5
    roasMinimo: 2.0       // retorno sobre investimento
}
```

---

## 🔧 Troubleshooting

### "CJ_API_KEY não configurada"
- Normal! Sistema funciona em modo demonstração
- Quando API funcionar, usará dados reais automaticamente

### "Credenciais Shopify não configuradas"
- Verificar se token está atualizado no `.env`
- Token Shopify renova a cada 24h

### "Erro ao criar produto"
- Verificar logs no dashboard
- Produto pode já existir (mesmo SKU)

### Dashboard não abre
```bash
# Verificar se porta 3001 está livre
lsof -ti:3001 | xargs kill -9

# Ou mudar porta no .env
DASHBOARD_PORT=3002
```

---

## 📈 Métricas Importantes

### Produto Ideal
- Score: **85+**
- Margem: **50%+**
- Avaliação: **4.5+**
- Pedidos: **1000+**

### Alertas
- **Estoque baixo** (< 5 unidades)
- **Margem baixa** (< 40%)
- **Preço alterado** pelo fornecedor

---

## 🔔 Notificações

Configure no `.env` para receber alertas:

- ✅ Produto importado
- 🛒 Produto criado na Shopify
- ⚠️ Estoque baixo
- 💰 Preço alterado
- ❌ Erros no sistema

---

## 🚀 Deploy (Subir pra Nuvem)

### Railway/Render (Recomendado)

1. Criar conta em railway.app
2. Conectar repositório GitHub
3. Configurar variáveis de ambiente
4. Deploy automático

```bash
# Variáveis necessárias:
SHOPIFY_ACCESS_TOKEN
CJ_API_KEY
CJ_EMAIL
WEBHOOK_URL (opcional)
```

---

## 💡 Dicas da Equipe

### Para maximizar vendas:
1. **Ajuste margem**: 40% mínimo, mas ideal 60%+
2. **Verifique estoque**: Produtos sem estoque não vendem
3. **Monitore preços**: Concorrencia muda preços
4. **Avalie score**: Produtos 90+ vendem mais

### Para evitar erros:
1. Sempre verifique logs no dashboard
2. Não delete produtos manualmente no Shopify
3. Mantenha token Shopify atualizado
4. Backup do banco: `data/gadgethub.db`

---

## 📞 Contato

- Documentação completa: `DEPLOY.md`
- Logs: `./logs/sistema-*.log`
- Banco de dados: `./data/gadgethub.db`

---

**Sistema criado por:** Gadget Hub Team  
**Última atualização:** 2026-04-05  
**Versão:** 1.0.0
