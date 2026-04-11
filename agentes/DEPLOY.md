# Gadget Hub — Guia de Deploy

## 🚀 Sistema de Agentes Autônomos para Shopify + CJ Dropshipping

---

## 📋 Requisitos

- **Node.js** 18+ 
- **SQLite** (incluído)
- **Conta Shopify** (opcional para testes)
- **Conta CJ Dropshipping** (opcional para testes)

---

## 🔧 Instalação

```bash
# 1. Navegar para pasta agentes
cd agentes

# 2. Instalar dependências
npm install

# 3. Configurar ambiente
node setup-env.js
```

---

## ⚙️ Configuração

Edite o arquivo `.env`:

```env
# Modo: manual | semi | autonomo
MODO=semi

# Shopify (obter em: Admin → Apps → Develop apps)
SHOPIFY_SHOP_DOMAIN=sua-loja.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxx

# CJ Dropshipping (obter em: Authorization → API)
CJ_API_KEY=sua_api_key
CJ_EMAIL=seu@email.com

# Dashboard
DASHBOARD_PORT=3001

# Notificações (opcional)
WEBHOOK_URL=https://hooks.slack.com/services/xxxxx
NOTIFICATION_EMAIL=admin@loja.com
```

---

## 🧪 Testes

### Testar Database
```bash
node test-database.js
```

### Testar CJ API (se configurado)
```bash
node test-cj-api.js
```

### Testar Pipeline de Importação
```bash
node test-pipeline.js
```

### Modo Demonstração (sem APIs)
```bash
node demo.js
```

---

## ▶️ Execução

### Modo CLI
```bash
# Modo semi-autônomo (recomendado)
node main.js

# Modo autônomo
MODO=autonomo node main.js

# Modo manual
MODO=manual node main.js
```

Comandos disponíveis (modo semi):
- `status()` — Ver status dos agentes
- `executar('cj-dropshipping')` — Executar agente específico
- `iniciar()` — Iniciar execução contínua
- `parar()` — Parar todos os agentes

### Modo Dashboard Web
```bash
npm run dashboard
# ou
node dashboard/server.js
```

Acesse: http://localhost:3001

---

## 📁 Estrutura do Projeto

```
agentes/
├── core/
│   ├── database.js          # SQLite
│   ├── agente-base.js       # Classe base
│   ├── manager-agentes.js   # Orquestrador
│   └── notificador.js       # Notificações
├── cj-dropshipping/
│   └── agente-cj.js         # Integração CJ
├── shopify/
│   └── agente-shopify.js    # Integração Shopify
├── estoque/
│   └── agente-estoque.js    # Monitoramento
├── pricing/
│   └── agente-precos.js     # Ajuste de preços
├── marketing/
│   └── agente-marketing.js   # Campanhas
├── dashboard/
│   ├── server.js            # Servidor WebSocket
│   └── public/
│       └── index.html       # Interface
├── pipeline-importacao.js    # Pipeline CJ→Shopify
├── main.js                  # Entry point
└── .env                     # Configurações
```

---

## 🤖 Agentes

| Agente | Função | Intervalo |
|--------|--------|-----------|
| **CJ** | Buscar produtos, validar | 60 min |
| **Shopify** | Criar/atualizar produtos | 30 min |
| **Estoque** | Monitorar, alertar | 30 min |
| **Preços** | Ajustar margens | 120 min |
| **Marketing** | Campanhas, copy | 180 min |

---

## 🔌 API Endpoints

### Dashboard API
```
GET  /api/status        → Status do sistema
GET  /api/produtos      → Lista produtos
GET  /api/logs          → Logs recentes
GET  /api/metricas      → Métricas/gráficos
GET  /api/operacoes     → Operações pendentes

POST /api/agente/:id/executar
POST /api/agentes/iniciar
POST /api/agentes/parar
```

### WebSocket
Conecte em `ws://localhost:3001` para atualizações em tempo real.

---

## 📊 Monitoramento

### Logs
- Arquivo: `data/gadgethub.db` (SQLite)
- Console: visualização em tempo real
- Dashboard: http://localhost:3001

### Métricas
- Produtos importados por dia
- Execuções por agente
- Logs por nível (info/aviso/erro)

---

## 🔔 Notificações

Configure no `.env`:

```env
# Slack/Discord webhook
WEBHOOK_URL=https://hooks.slack.com/services/T000/B000/XXXX

# Email
NOTIFICATION_EMAIL=admin@loja.com
```

Eventos notificados:
- ✅ Produto importado
- 🛒 Produto criado na Shopify
- ⚠️ Estoque baixo
- 💰 Preço alterado
- ❌ Erros no sistema
- 🤖 Execução de agentes

---

## 🚀 Deploy em Produção

### Recomendado: Railway/Render

```bash
# 1. Criar conta em railway.app ou render.com

# 2. Conectar repositório GitHub

# 3. Configurar variáveis de ambiente:
#    - SHOPIFY_ACCESS_TOKEN
#    - CJ_API_KEY
#    - CJ_EMAIL
#    - WEBHOOK_URL (opcional)

# 4. Deploy automático
```

### Docker (opcional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["node", "dashboard/server.js"]
```

---

## ⚠️ Troubleshooting

### Erro: "CJ_API_KEY não configurada"
- Execute `node setup-env.js`
- Ou edite `.env` manualmente

### Erro: "Invalid API key or access token"
- Verifique se a API key CJ está ativa no dashboard
- Aguarde alguns minutos após criar a API key

### Erro: "SHOPIFY_ACCESS_TOKEN não configurada"
- Sistema funciona em modo demonstração sem Shopify
- Configure token para importar produtos reais

### Porta 3001 em uso
```bash
# Linux/Mac
lsof -ti:3001 | xargs kill -9

# Windows
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

---

## 📝 Comandos Úteis

```bash
# Ver status
node -e "const s=require('./main.js'); s.inicializarSistema().then(x=>console.log(x.manager.getStatusCompleto()))"

# Backup database
cp data/gadgethub.db data/backup-$(date +%Y%m%d).db

# Reset database
rm data/gadgethub.db
node test-database.js

# Logs em tempo real
tail -f data/gadgethub.db  # (não aplicável para SQLite)
```

---

## 🎯 Próximos Passos

1. ✅ Configurar `.env` com credenciais
2. ✅ Testar com `node test-pipeline.js`
3. ✅ Iniciar dashboard: `npm run dashboard`
4. ✅ Adicionar webhook para notificações
5. 🚀 Deploy para produção

---

## 📞 Suporte

- Documentação: `README.md`
- Issues: GitHub Issues
- Email: admin@gadget-hub.com

---

**Gadget Hub © 2026 — Automação para Dropshipping**
