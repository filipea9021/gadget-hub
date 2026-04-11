// =====================================================
// API SERVER — Servidor REST + WebSocket unificado
// =====================================================
// Endpoints organizados:
//   /api/status      — Status geral do sistema
//   /api/agentes     — Controlo de agentes
//   /api/produtos    — CRUD de produtos
//   /api/brain       — Comandos AI (linguagem natural)
//   /api/automacao   — FAQs, webhooks, hashtags
//   /api/blender     — Renders e fila
//   /api/logs        — Logs do sistema
//   /api/metricas    — Métricas e gráficos
// =====================================================

import express from 'express';
import { WebSocketServer } from 'ws';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import { config } from '../core/config.js';
import { criarLogger } from '../core/logger.js';
import { getDatabase } from '../core/database.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const log = criarLogger('api');
const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });
const clients = new Set();

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'dashboard', 'public')));

// =====================================================
// ESTADO — Injetado pelo main.js ao iniciar
// =====================================================
let _manager = null;
let _agentes = null;
let _aiRouter = null;

function injetarSistema(manager, agentes, aiRouter) {
    _manager = manager;
    _agentes = agentes;
    _aiRouter = aiRouter;
    log.ok('Sistema injetado no servidor API');
}

// =====================================================
// WEBSOCKET
// =====================================================

wss.on('connection', (ws) => {
    log.info('WebSocket: cliente conectado');
    clients.add(ws);
    enviarStatus(ws);

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);

            if (data.action === 'executar' && data.agenteId && _manager) {
                const resultado = await _manager.executarAgente(data.agenteId);
                broadcast({ tipo: 'execucao', agente: data.agenteId, resultado });
            }
            if (data.action === 'iniciarTodos' && _manager) {
                _manager.iniciarTodos();
                broadcast({ tipo: 'sistema', mensagem: 'Agentes iniciados' });
            }
            if (data.action === 'pararTodos' && _manager) {
                _manager.pararTodos();
                broadcast({ tipo: 'sistema', mensagem: 'Agentes parados' });
            }
            if (data.action === 'brain' && data.texto && _aiRouter) {
                const resultado = await _aiRouter.processar(data.texto);
                ws.send(JSON.stringify({ tipo: 'brain', resultado }));
            }
        } catch (erro) {
            log.error('WebSocket erro', erro.message);
        }
    });

    ws.on('close', () => {
        clients.delete(ws);
    });
});

async function enviarStatus(ws) {
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        ws.send(JSON.stringify({ tipo: 'status', data: resumo, timestamp: new Date().toISOString() }));
    } catch (erro) {
        log.error('Erro ao enviar status', erro.message);
    }
}

function broadcast(data) {
    const message = JSON.stringify(data);
    for (const client of clients) {
        if (client.readyState === 1) client.send(message);
    }
}

// Auto-update periódico
setInterval(async () => {
    if (clients.size === 0) return;
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        broadcast({ tipo: 'update', data: resumo, timestamp: new Date().toISOString() });
    } catch (_) { /* silenciar */ }
}, 5000);

// =====================================================
// /api/status — Status geral
// =====================================================

app.get('/api/status', async (req, res) => {
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        const agentesStatus = _manager ? _manager.getStatusCompleto() : { agentes: [] };

        res.json({
            sucesso: true,
            timestamp: new Date().toISOString(),
            modo: config.mode,
            isDemo: config.isDemo,
            database: resumo,
            agentes: agentesStatus.agentes.map(a => ({
                id: a.id, nome: a.nome, status: a.status,
                ultimaExecucao: a.ultimaExecucao,
                proximaExecucao: a.proximaExecucao,
            })),
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// =====================================================
// /api/agentes — Controlo de agentes
// =====================================================

app.post('/api/agentes/:id/executar', async (req, res) => {
    try {
        if (!_manager) return res.status(503).json({ sucesso: false, erro: 'Sistema não inicializado' });
        const resultado = await _manager.executarAgente(req.params.id);
        res.json({ sucesso: true, agente: req.params.id, resultado });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

app.post('/api/agentes/iniciar', async (req, res) => {
    try {
        if (!_manager) return res.status(503).json({ sucesso: false, erro: 'Sistema não inicializado' });
        _manager.iniciarTodos();
        res.json({ sucesso: true, mensagem: 'Agentes iniciados' });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

app.post('/api/agentes/parar', async (req, res) => {
    try {
        if (!_manager) return res.status(503).json({ sucesso: false, erro: 'Sistema não inicializado' });
        _manager.pararTodos();
        res.json({ sucesso: true, mensagem: 'Agentes parados' });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// =====================================================
// /api/brain — Comandos AI em linguagem natural
// =====================================================

app.post('/api/brain', async (req, res) => {
    try {
        if (!_aiRouter) return res.status(503).json({ sucesso: false, erro: 'Módulo AI não disponível' });
        const { texto } = req.body;
        if (!texto) return res.status(400).json({ sucesso: false, erro: 'Campo "texto" obrigatório' });

        const resultado = await _aiRouter.processar(texto);
        res.json({ sucesso: true, resultado });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

app.get('/api/brain/historico', (req, res) => {
    if (!_aiRouter) return res.status(503).json({ sucesso: false, erro: 'Módulo AI não disponível' });
    res.json({ sucesso: true, historico: _aiRouter.getHistorico() });
});

// =====================================================
// /api/automacao — FAQs, webhooks, hashtags
// =====================================================

app.post('/api/automacao/faq', (req, res) => {
    if (!_agentes?.automacao) return res.status(503).json({ sucesso: false, erro: 'Agente automação não disponível' });
    const { texto } = req.body;
    const resultado = _agentes.automacao.responderPergunta(texto || '');
    res.json({ sucesso: true, resultado });
});

app.post('/api/automacao/webhook', (req, res) => {
    if (!_agentes?.automacao) return res.status(503).json({ sucesso: false, erro: 'Agente automação não disponível' });
    const { evento, dados } = req.body;
    const resultado = _agentes.automacao.processarWebhook(evento, dados || {});
    res.json({ sucesso: true, resultado });
});

app.get('/api/automacao/hashtags/:categoria', (req, res) => {
    if (!_agentes?.automacao) return res.status(503).json({ sucesso: false, erro: 'Agente automação não disponível' });
    const hashtags = _agentes.automacao.getHashtags(req.params.categoria);
    res.json({ sucesso: true, categoria: req.params.categoria, hashtags });
});

app.get('/api/automacao/stats', (req, res) => {
    if (!_agentes?.automacao) return res.status(503).json({ sucesso: false, erro: 'Agente automação não disponível' });
    res.json({ sucesso: true, stats: _agentes.automacao.getStats() });
});

// =====================================================
// /api/blender — Renders e fila
// =====================================================

app.get('/api/blender/stats', (req, res) => {
    if (!_agentes?.blender) return res.status(503).json({ sucesso: false, erro: 'Agente Blender não disponível' });
    res.json({ sucesso: true, stats: _agentes.blender.getStats() });
});

app.get('/api/blender/templates', (req, res) => {
    if (!_agentes?.blender) return res.status(503).json({ sucesso: false, erro: 'Agente Blender não disponível' });
    res.json({ sucesso: true, templates: _agentes.blender.getTemplatesDisponiveis() });
});

app.post('/api/blender/render', async (req, res) => {
    if (!_agentes?.blender) return res.status(503).json({ sucesso: false, erro: 'Agente Blender não disponível' });
    const { produto, tipos } = req.body;
    const resultado = await _agentes.blender.solicitarRender(produto, tipos);
    res.json({ sucesso: true, resultado });
});

// =====================================================
// /api/produtos — CRUD
// =====================================================

app.get('/api/produtos', async (req, res) => {
    try {
        const db = await getDatabase();
        const { status, categoria, limit = 50 } = req.query;
        const filtros = {};
        if (status) filtros.status = status;
        if (categoria) filtros.categoria = categoria;
        const produtos = await db.getProdutos(filtros, parseInt(limit));
        res.json({ sucesso: true, total: produtos.length, produtos });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// =====================================================
// /api/logs
// =====================================================

app.get('/api/logs', async (req, res) => {
    try {
        const db = await getDatabase();
        const { agente, limit = 50 } = req.query;
        const logs = await db.getLogs(agente, parseInt(limit));
        res.json({ sucesso: true, total: logs.length, logs });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// =====================================================
// /api/metricas
// =====================================================

app.get('/api/metricas', async (req, res) => {
    try {
        const db = await getDatabase();
        // Dados virão do DB em produção
        const metricas = {
            produtosPorDia: [
                { dia: 'Seg', qtd: 2 }, { dia: 'Ter', qtd: 5 },
                { dia: 'Qua', qtd: 3 }, { dia: 'Qui', qtd: 8 },
                { dia: 'Sex', qtd: 12 }, { dia: 'Sab', qtd: 6 },
                { dia: 'Dom', qtd: 4 },
            ],
            execucoesPorAgente: _manager
                ? _manager.getStatusCompleto().agentes.map(a => ({ agente: a.nome, execucoes: 0 }))
                : [],
        };
        res.json({ sucesso: true, metricas });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// =====================================================
// PÁGINA PRINCIPAL
// =====================================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'dashboard', 'public', 'index.html'));
});

// =====================================================
// INICIAR SERVIDOR
// =====================================================

function iniciarServidor(porta = null) {
    const p = porta || config.server.port;
    server.listen(p, () => {
        log.ok(`API rodando em http://localhost:${p}`);
        log.info('Endpoints: /api/status, /api/agentes, /api/brain, /api/automacao, /api/blender, /api/produtos, /api/logs');
    });
}

export { app, server, broadcast, injetarSistema, iniciarServidor };
