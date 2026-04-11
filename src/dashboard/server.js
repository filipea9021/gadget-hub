// =====================================================
// DASHBOARD SERVER — Servidor web com WebSocket
// =====================================================
// Features:
// - REST API para dados
// - WebSocket para atualizações em tempo real
// - Broadcast de eventos dos agentes
// =====================================================

import express from 'express';
import { WebSocketServer } from 'ws';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import { getDatabase } from '../core/database.js';
// import será resolvido quando o novo main.js estiver pronto
// import { inicializarSistema } from '../../main.js';
import { config } from '../core/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.DASHBOARD_PORT || 3001;

// Criar servidor HTTP
const server = http.createServer(app);

// WebSocket Server
const wss = new WebSocketServer({ server });

// Clientes conectados
const clients = new Set();

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Sistema de agentes (inicializado na primeira requisição)
let sistema = null;

async function getSistema() {
    if (!sistema) {
        console.log('🚀 Inicializando sistema de agentes...');
        sistema = await inicializarSistema();
    }
    return sistema;
}

// =====================================================
// WEBSOCKET
// =====================================================

wss.on('connection', (ws) => {
    console.log('🔌 Novo cliente conectado');
    clients.add(ws);
    
    // Enviar status inicial
    enviarStatus(ws);
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.action === 'executar' && data.agenteId) {
                const sys = await getSistema();
                const resultado = await sys.manager.executarAgente(data.agenteId);
                broadcast({ tipo: 'execucao', agente: data.agenteId, resultado });
            }
            
            if (data.action === 'iniciarTodos') {
                const sys = await getSistema();
                sys.manager.iniciarTodos();
                broadcast({ tipo: 'sistema', mensagem: 'Todos os agentes iniciados' });
            }
            
            if (data.action === 'pararTodos') {
                const sys = await getSistema();
                sys.manager.pararTodos();
                broadcast({ tipo: 'sistema', mensagem: 'Todos os agentes parados' });
            }
        } catch (erro) {
            console.error('Erro WebSocket:', erro);
        }
    });
    
    ws.on('close', () => {
        console.log('🔌 Cliente desconectado');
        clients.delete(ws);
    });
});

// Enviar mensagem para cliente específico
async function enviarStatus(ws) {
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        
        ws.send(JSON.stringify({
            tipo: 'status',
            data: resumo,
            timestamp: new Date().toISOString()
        }));
    } catch (erro) {
        console.error('Erro ao enviar status:', erro);
    }
}

// Broadcast para todos os clientes
function broadcast(data) {
    const message = JSON.stringify(data);
    clients.forEach(client => {
        if (client.readyState === 1) { // WebSocket.OPEN
            client.send(message);
        }
    });
}

// Loop de atualização periódica
setInterval(async () => {
    if (clients.size === 0) return;
    
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        
        broadcast({
            tipo: 'update',
            data: resumo,
            timestamp: new Date().toISOString()
        });
    } catch (erro) {
        console.error('Erro no broadcast:', erro);
    }
}, 3000); // A cada 3 segundos

// =====================================================
// API ENDPOINTS
// =====================================================

// Status geral do sistema
app.get('/api/status', async (req, res) => {
    try {
        const db = await getDatabase();
        const resumo = await db.getResumoSistema();
        
        const sys = await getSistema();
        const agentesStatus = sys.manager.getStatusCompleto();
        
        res.json({
            sucesso: true,
            timestamp: new Date().toISOString(),
            modo: CONFIG.modo,
            database: resumo,
            agentes: agentesStatus.agentes.map(a => ({
                id: a.id,
                nome: a.nome,
                status: a.status,
                ultimaExecucao: a.ultimaExecucao,
                proximaExecucao: a.proximaExecucao,
                intervaloMinutos: a.intervaloMinutos
            }))
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Lista de produtos
app.get('/api/produtos', async (req, res) => {
    try {
        const db = await getDatabase();
        const { status, categoria, limit = 50 } = req.query;
        
        const filtros = {};
        if (status) filtros.status = status;
        if (categoria) filtros.categoria = categoria;
        
        const produtos = await db.getProdutos(filtros, parseInt(limit));
        
        res.json({
            sucesso: true,
            total: produtos.length,
            produtos
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Logs recentes
app.get('/api/logs', async (req, res) => {
    try {
        const db = await getDatabase();
        const { agente, limit = 50 } = req.query;
        
        const logs = await db.getLogs(agente, parseInt(limit));
        
        res.json({
            sucesso: true,
            total: logs.length,
            logs
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Operações pendentes
app.get('/api/operacoes', async (req, res) => {
    try {
        const db = await getDatabase();
        const operacoes = await db.getOperacoesPendentes();
        
        res.json({
            sucesso: true,
            total: operacoes.length,
            operacoes
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Métricas para gráficos
app.get('/api/metricas', async (req, res) => {
    try {
        const db = await getDatabase();
        
        // Dados simulados por enquanto (em produção viriam do banco)
        const metricas = {
            produtosPorDia: [
                { dia: 'Seg', quantidade: 2 },
                { dia: 'Ter', quantidade: 5 },
                { dia: 'Qua', quantidade: 3 },
                { dia: 'Qui', quantidade: 8 },
                { dia: 'Sex', quantidade: 12 },
                { dia: 'Sab', quantidade: 6 },
                { dia: 'Dom', quantidade: 4 }
            ],
            execucoesPorAgente: [
                { agente: 'CJ', execucoes: 45 },
                { agente: 'Shopify', execucoes: 38 },
                { agente: 'Preços', execucoes: 21 },
                { agente: 'Estoque', execucoes: 52 },
                { agente: 'Marketing', execucoes: 15 }
            ],
            logsPorNivel: [
                { nivel: 'info', count: 156 },
                { nivel: 'aviso', count: 23 },
                { nivel: 'erro', count: 8 }
            ]
        };
        
        res.json({ sucesso: true, metricas });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Executar agente específico
app.post('/api/agente/:id/executar', async (req, res) => {
    try {
        const { id } = req.params;
        const sys = await getSistema();
        
        const resultado = await sys.manager.executarAgente(id);
        
        res.json({
            sucesso: true,
            agente: id,
            resultado
        });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Iniciar todos os agentes
app.post('/api/agentes/iniciar', async (req, res) => {
    try {
        const sys = await getSistema();
        sys.manager.iniciarTodos();
        
        res.json({ sucesso: true, mensagem: 'Todos os agentes iniciados' });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Parar todos os agentes
app.post('/api/agentes/parar', async (req, res) => {
    try {
        const sys = await getSistema();
        sys.manager.pararTodos();
        
        res.json({ sucesso: true, mensagem: 'Todos os agentes parados' });
    } catch (erro) {
        res.status(500).json({ sucesso: false, erro: erro.message });
    }
});

// Página principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// =====================================================
// INICIALIZAR SERVIDOR
// =====================================================

server.listen(PORT, () => {
    console.log('╔════════════════════════════════════════════════════╗');
    console.log('║     📊 GADGET HUB — Dashboard                      ║');
    console.log('║     WebSocket + API REST + Gráficos                ║');
    console.log('╚════════════════════════════════════════════════════╝');
    console.log(`\n🌐 Acesse: http://localhost:${PORT}`);
    console.log(`\nEndpoints disponíveis:`);
    console.log(`  • GET  /api/status     → Status do sistema`);
    console.log(`  • GET  /api/produtos   → Lista de produtos`);
    console.log(`  • GET  /api/logs       → Logs recentes`);
    console.log(`  • GET  /api/metricas   → Métricas (novo!)`);
    console.log(`\n🔌 WebSocket ativo na porta ${PORT}`);
    console.log(`\nPressione Ctrl+C para parar\n`);
});

export { app, server, broadcast };
