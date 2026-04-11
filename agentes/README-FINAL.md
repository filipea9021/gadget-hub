// =====================================================
// README.md — Gadget Hub Agentes Autônomos
// =====================================================

# 🤖 Gadget Hub — Sistema de Agentes Autônomos

Sistema de automação para loja Shopify + CJ Dropshipping.

## ✅ Status do Sistema

| Componente | Status | Observação |
|------------|--------|------------|
| **Database SQLite** | ✅ Funcionando | Persistência completa |
| **Shopify API** | ✅ Configurada | Atualiza a cada 24h |
| **CJ API** | ⚠️ Modo Demo | Aguardando autenticação |
| **Dashboard Web** | ✅ Funcionando | http://localhost:3001 |
| **WebSocket** | ✅ Ativo | Atualizações em tempo real |
| **Pipeline Importação** | ✅ Pronto | CJ → Shopify |
| **Notificações** | ✅ Configurado | Webhook/Email/Console |

## 🚀 Quick Start

```bash
cd agentes

# Modo Dashboard (recomendado)
npm run dashboard
# Acesse: http://localhost:3001

# Modo CLI
node main.js
```

## 📁 Estrutura

```
agentes/
├── core/              # Database, agentes base, notificações
├── cj-dropshipping/  # Agente CJ (modo demo ativo)
├── shopify/          # Agente Shopify (✓ configurado)
├── estoque/          # Agente Estoque
├── pricing/          # Agente Preços
├── marketing/        # Agente Marketing
├── dashboard/        # Servidor web + WebSocket
├── pipeline-importacao.js  # Pipeline CJ → Shopify
└── .env              # Configurações
```

## ⚙️ Configuração Atual (.env)

```env
# ✅ Shopify (já configurado, atualiza a cada 24h)
SHOPIFY_SHOP_DOMAIN=gadget-hub.myshopify.com
SHOPIFY_ACCESS_TOKEN=... 

# ⚠️ CJ Dropshipping (modo demonstração)
CJ_API_KEY=CJ5298786@api@7ca4cd0efbda4ba491c0496638cc3d6b
CJ_EMAIL=filipeazevedo791@gmail.com
# Nota: API não autentica, sistema usa dados simulados

# Dashboard
DASHBOARD_PORT=3001
```

## 🔄 Fluxo de Trabalho

### Modo Demonstração (Atual)
1. Agente CJ gera produtos simulados
2. Valida critérios (margem 40%+, avaliação 4+)
3. Salva no SQLite
4. Agente Shopify processa fila
5. Dashboard mostra em tempo real

### Modo Produção (Quando CJ API ativar)
1. Sistema detecta API key válida automaticamente
2. Busca produtos reais do CJ
3. Mesmo fluxo de validação
4. Cria produtos na Shopify
5. Sincroniza estoque/preços

## 🧪 Testes

```bash
# Testar pipeline completo
node test-pipeline.js

# Testar conexões
node test-shopify.js      # ✅ Configurado
node test-cj-api.js       # ⚠️ Aguardando API

# Demonstração
node demo.js
```

## 📊 Dashboard

Funcionalidades:
- Stats em tempo real (WebSocket)
- Gráficos Chart.js (produtos, execuções, logs)
- Tabela de agentes com controles
- Lista de produtos importados
- Logs com atualização automática

## 🔔 Notificações

Eventos monitorados:
- ✅ Produto importado
- 🛒 Produto criado na Shopify
- ⚠️ Estoque baixo
- 💰 Preço alterado
- ❌ Erros no sistema
- 🤖 Execução de agentes

## 🎯 Próximos Passos

### 1. Resolver CJ API
Quando a API key estiver funcionando:
```bash
# Atualizar .env com nova key (se necessário)
# O sistema detecta automaticamente e usa dados reais
node test-cj-api.js  # Verificar conexão
```

### 2. Deploy (Opcional)
```bash
# Railway/Render
# 1. Subir código
# 2. Configurar variáveis de ambiente
# 3. Dashboard público
```

## 📞 Troubleshooting

### CJ API não autentica
- Sistema funciona automaticamente em modo demonstração
- Produtos simulados permitem testar todo o fluxo
- Quando API funcionar, dados reais substituem simulados

### Shopify não conecta
- Verificar se token está atualizado (sistema renova a cada 24h)
- Confirmar permissões do app: read_products, write_products

## 📝 Notas

- Sistema desenvolvido em: Node.js 18+, SQLite, Express, WebSocket
- Totalmente modular: cada agente é independente
- Event-driven: agentes se comunicam via EventEmitter
- Persistência: SQLite em `./data/gadgethub.db`
- Logs: estruturados com timestamp, agente, nível

---

**Gadget Hub © 2026 — Automação Inteligente para Dropshipping**
