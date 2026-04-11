# 🤖 Gadget Hub — Sistema de Agentes Autônomos

Sistema de automação inteligente para operação autônoma da loja Shopify com integração CJ Dropshipping.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAGER DE AGENTES                        │
│                   (Orquestração Central)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Agente CJ    │   │ Agente Shopify│   │ Agente Preços │
│  Dropshipping │◄──┤               │◄──┤               │
│               │   │               │   │               │
│ • Sourcing    │   │ • Produtos    │   │ • Monitoramento│
│ • Estoque     │   │ • Preços      │   │ • Ajuste       │
│ • Fulfillment │   │ • Pedidos     │   │ • Margem 40%+  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        │              ┌──────┴──────┐              │
        │              │             │              │
        │              ▼             ▼              │
        │      ┌───────────────┐ ┌───────────────┐ │
        └─────►│ Agente Estoque│ │Agente Marketing│◄┘
               │               │ │               │
               │ • Alertas     │ │ • Campanhas   │
               │ • Previsões   │ │ • Copy        │
               │ • Sync        │ │ • ROAS        │
               └───────────────┘ └───────────────┘
```

---

## 📁 Estrutura

```
agentes/
├── core/
│   ├── agente-base.js          # Classe base para todos os agentes
│   └── manager-agentes.js      # Orquestrador central
│
├── shopify/
│   └── agente-shopify.js       # Gestão da loja Shopify
│
├── cj-dropshipping/
│   └── agente-cj.js             # Integração CJ Dropshipping
│
├── pricing/
│   └── agente-precos.js         # Monitoramento de preços
│
├── marketing/
│   └── agente-marketing.js      # Automação de campanhas
│
├── estoque/
│   └── agente-estoque.js        # Gestão de inventário
│
├── main.js                      # Ponto de entrada
├── .env.example                 # Configuração de ambiente
└── README.md                    # Este arquivo
```

---

## 🚀 Inicialização

### 1. Instalar Dependências

```bash
cd agentes
npm init -y
npm install node-fetch
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Executar

**Modo Semi-Autônomo (Recomendado):**
```bash
node main.js
```

Comandos disponíveis:
- `status()` — Ver estado de todos os agentes
- `executar('shopify')` — Executar agente específico
- `iniciar()` — Iniciar execução contínua
- `parar()` — Parar todos os agentes

**Modo Autônomo:**
```bash
MODO=autonomo node main.js
```

---

## 🔄 Fluxo Autônomo Completo

```
┌──────────────────────────────────────────────────────────┐
│  CICLO 1: Sourcing (Agente CJ)                           │
│  ├── Pesquisar produtos em categorias alvo             │
│  ├── Validar (score, margem 40%, avaliação)              │
│  └── Notificar: "novos_produtos_validados"               │
│                         │                                │
│                         ▼                                │
│  CICLO 2: Importação (Agente Shopify)                    │
│  ├── Receber notificação de novos produtos               │
│  ├── Criar produtos na loja                            │
│  ├── Definir preços e imagens                            │
│  └── Notificar: "produto_criado"                         │
│                         │                                │
│                         ▼                                │
│  CICLO 3: Monitoramento (Agente Estoque)                 │
│  ├── Registrar produto para monitoramento              │
│  ├── Verificar estoque CJ periodicamente                 │
│  └── Alertar se estoque < 5 unidades                     │
│                         │                                │
│                         ▼                                │
│  CICLO 4: Pricing (Agente Preços)                        │
│  ├── Monitorar preços da concorrência                  │
│  ├── Ajustar preços (margem 40-70%)                      │
│  └── Notificar: "preco_ajustado"                         │
│                         │                                │
│                         ▼                                │
│  CICLO 5: Marketing (Agente Marketing)                   │
│  ├── Criar campanhas para produtos de alto score         │
│  ├── Gerar copy automático                               │
│  ├── Otimizar ROAS                                       │
│  └── Pausar campanhas se estoque crítico               │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Comunicação entre Agentes

Os agentes se comunicam via **EventEmitter**:

```javascript
// Agente CJ notifica novos produtos
agenteCJ.notificar('novos_produtos_validados', { produtos });

// Agente Shopify escuta e processa
agenteShopify.onNotificacao((notificacao) => {
    if (notificacao.evento === 'novos_produtos_validados') {
        // Adicionar à fila de importação
    }
});
```

### Eventos Principais

| Evento | Origem | Destino | Ação |
|--------|--------|---------|------|
| `novos_produtos_validados` | CJ | Shopify | Criar produtos na loja |
| `produto_na_fila` | Shopify | Estoque | Registrar monitoramento |
| `ajustar_preco` | Preços | Shopify | Atualizar preço na loja |
| `estoque_alerta` | Estoque | Marketing | Pausar campanhas |
| `campanha_criada` | Marketing | Manager | Registrar atividade |

---

## ⚙️ Configuração

### Módulos de Agente

```javascript
// Personalizar intervalo de execução
const agente = new AgenteShopify({
    intervaloMinutos: 30  // Executa a cada 30 minutos
});
```

### Regras de Negócio

```javascript
// Agente de Preços
agente.atualizarRegras({
    margemMinima: 40,
    margemAlvo: 50,
    ajusteMaximo: 10  // % máximo de alteração
});

// Agente de Estoque
agente.atualizarLimites({
    estoqueMinimo: 5,
    estoqueCritico: 2
});
```

---

## 📈 Monitoramento

### Dashboard de Status

```javascript
const status = manager.getStatusCompleto();
console.table(status.agentes);
```

Saída:
```
┌─────────────────┬──────────┬────────────────┬────────────────┐
│ Agente          │ Status   │ Última Execução│ Próxima        │
├─────────────────┼──────────┼────────────────┼────────────────┤
│ Agente Shopify  │ pronto   │ 14:32:15       │ 15:02:15       │
│ Agente CJ       │ executando│ 14:45:00      │ 15:45:00       │
│ Agente Preços   │ pronto   │ 12:00:00       │ 14:00:00       │
└─────────────────┴──────────┴────────────────┴────────────────┘
```

### Relatórios Automáticos

```javascript
// Exportar relatório a cada hora
setInterval(async () => {
    const arquivo = await manager.exportarRelatorio();
    console.log(`Relatório: ${arquivo}`);
}, 3600000);
```

---

## 🛡️ Segurança

- **Nunca commitar** o arquivo `.env`
- Usar variáveis de ambiente para todas as credenciais
- Rotacionar tokens periodicamente
- Logs não devem conter dados sensíveis

---

## 📝 Próximos Passos

1. ✅ Arquitetura base implementada
2. ⏳ Integrar APIs reais (Shopify GraphQL, CJ REST)
3. ⏳ Implementar persistência de estado (SQLite/PostgreSQL)
4. ⏳ Criar dashboard web de monitoramento
5. ⏳ Adicionar agente de análise de tendências

---

## 🎯 Roadmap para Autonomia Total

| Fase | Capacidade | Timeline |
|------|-----------|----------|
| **V1** | Sistema de skills manual | ✅ Completo |
| **V2** | Agentes semi-autônomos | ✅ Arquitetura criada |
| **V3** | Integrações API funcionando | ⏳ 2 semanas |
| **V4** | Automação completa (modo autônomo) | ⏳ 1 mês |
| **V5** | Agentes com aprendizado (ML) | ⏳ 3 meses |

---

**Sistema criado para operação autônoma da Gadget Hub.**
