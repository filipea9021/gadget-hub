// =====================================================
// DATABASE — Camada de persistência SQLite
// =====================================================
// Usa better-sqlite3 (síncrono, prebuilt, sem compilar)
// API mantém async para compatibilidade com os agentes
// =====================================================

import BetterSqlite3 from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import { config } from './config.js';

class Database {
    constructor() {
        this.db = null;
        this.dbPath = config.paths.database;
    }

    async conectar() {
        if (this.db) return this.db;

        // Garantir que a pasta data/ existe
        const dir = path.dirname(this.dbPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        this.db = new BetterSqlite3(this.dbPath);
        this.db.pragma('journal_mode = WAL');

        this._criarSchema();
        console.log('💾 Database conectado:', this.dbPath);
        return this.db;
    }

    _criarSchema() {
        // Estados dos agentes
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS agentes_estado (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                status TEXT DEFAULT 'parado',
                ultima_execucao TEXT,
                proxima_execucao TEXT,
                intervalo_minutos INTEGER DEFAULT 60,
                historico TEXT,
                configuracao TEXT,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Logs estruturados
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                agente_id TEXT,
                nivel TEXT CHECK(nivel IN ('info', 'aviso', 'erro', 'debug')),
                mensagem TEXT,
                dados TEXT
            )
        `);

        // Produtos rastreados
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS produtos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                sku TEXT,
                categoria TEXT,
                preco_custo REAL,
                preco_venda REAL,
                margem REAL,
                score INTEGER,
                avaliacao REAL,
                fornecedor TEXT,
                fornecedor_pid TEXT,
                shopify_product_id TEXT,
                estoque_atual INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ativo',
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Operações pendentes (fila)
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS operacoes_fila (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                status TEXT DEFAULT 'pendente',
                dados TEXT NOT NULL,
                resultado TEXT,
                erro TEXT,
                tentativas INTEGER DEFAULT 0,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                processado_em TEXT
            )
        `);

        // Preços histórico
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS precos_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id TEXT,
                preco_anterior REAL,
                preco_novo REAL,
                margem_anterior REAL,
                margem_nova REAL,
                motivo TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Campanhas de marketing
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS campanhas (
                id TEXT PRIMARY KEY,
                nome TEXT,
                produto_id TEXT,
                canais TEXT,
                orcamento_diario REAL,
                status TEXT DEFAULT 'ativa',
                roas REAL,
                conversoes INTEGER DEFAULT 0,
                gasto_total REAL DEFAULT 0,
                criada_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Eventos entre agentes
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origem TEXT,
                destino TEXT,
                evento TEXT,
                dados TEXT,
                processado BOOLEAN DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Índices para performance
        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_logs_agente ON logs(agente_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_produtos_fornecedor ON produtos(fornecedor_pid);
            CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);
            CREATE INDEX IF NOT EXISTS idx_fila_status ON operacoes_fila(status);
            CREATE INDEX IF NOT EXISTS idx_eventos_processado ON eventos(processado, timestamp);
        `);
    }

    // ============ OPERAÇÕES AGENTES ============

    async salvarEstadoAgente(agente) {
        const historicoJSON = JSON.stringify(agente.historico || []);
        const configJSON = JSON.stringify({ intervaloMinutos: agente.intervaloMinutos });

        this.db.prepare(`
            INSERT INTO agentes_estado (id, nome, status, ultima_execucao, proxima_execucao,
                intervalo_minutos, historico, configuracao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                ultima_execucao = excluded.ultima_execucao,
                proxima_execucao = excluded.proxima_execucao,
                historico = excluded.historico,
                configuracao = excluded.configuracao,
                atualizado_em = CURRENT_TIMESTAMP
        `).run(agente.id, agente.nome, agente.status, agente.ultimaExecucao,
            agente.proximaExecucao, agente.intervaloMinutos, historicoJSON, configJSON);
    }

    async carregarEstadoAgente(agenteId) {
        const row = this.db.prepare('SELECT * FROM agentes_estado WHERE id = ?').get(agenteId);
        if (!row) return null;

        return {
            ...row,
            historico: JSON.parse(row.historico || '[]'),
            configuracao: JSON.parse(row.configuracao || '{}')
        };
    }

    // ============ LOGS ============

    async adicionarLog(agenteId, nivel, mensagem, dados = null) {
        this.db.prepare(`
            INSERT INTO logs (agente_id, nivel, mensagem, dados)
            VALUES (?, ?, ?, ?)
        `).run(agenteId, nivel, mensagem, dados ? JSON.stringify(dados) : null);
    }

    async getLogs(agenteId, limite = 100) {
        if (agenteId) {
            return this.db.prepare(`
                SELECT * FROM logs WHERE agente_id = ? ORDER BY timestamp DESC LIMIT ?
            `).all(agenteId, limite);
        }
        return this.db.prepare(`
            SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?
        `).all(limite);
    }

    // ============ PRODUTOS ============

    async salvarProduto(produto) {
        this.db.prepare(`
            INSERT INTO produtos (id, nome, sku, categoria, preco_custo, preco_venda,
                margem, score, avaliacao, fornecedor, fornecedor_pid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nome = excluded.nome,
                preco_custo = excluded.preco_custo,
                preco_venda = excluded.preco_venda,
                margem = excluded.margem,
                score = excluded.score,
                avaliacao = excluded.avaliacao,
                atualizado_em = CURRENT_TIMESTAMP
        `).run(produto.id || produto.pid, produto.nome, produto.sku, produto.categoria,
            produto.precoCusto, produto.precoVenda, produto.margem, produto.score,
            produto.avaliacao, produto.fornecedor, produto.pid);
    }

    async getProdutos(filtros = {}, limite = 50) {
        let query = 'SELECT * FROM produtos WHERE 1=1';
        const params = [];

        if (filtros.status) {
            query += ' AND status = ?';
            params.push(filtros.status);
        }
        if (filtros.fornecedor) {
            query += ' AND fornecedor = ?';
            params.push(filtros.fornecedor);
        }
        if (filtros.categoria) {
            query += ' AND categoria = ?';
            params.push(filtros.categoria);
        }
        if (filtros.scoreMinimo) {
            query += ' AND score >= ?';
            params.push(filtros.scoreMinimo);
        }

        query += ' ORDER BY score DESC LIMIT ?';
        params.push(limite);

        return this.db.prepare(query).all(...params);
    }

    async atualizarShopifyProductId(pid, shopifyId) {
        this.db.prepare(
            'UPDATE produtos SET shopify_product_id = ? WHERE fornecedor_pid = ?'
        ).run(shopifyId, pid);
    }

    // ============ FILA DE OPERAÇÕES ============

    async adicionarOperacao(tipo, dados) {
        const result = this.db.prepare(`
            INSERT INTO operacoes_fila (tipo, dados) VALUES (?, ?)
        `).run(tipo, JSON.stringify(dados));
        return result.lastInsertRowid;
    }

    async getOperacoesPendentes(limite = 10) {
        return this.db.prepare(`
            SELECT * FROM operacoes_fila
            WHERE status = 'pendente' AND tentativas < 3
            ORDER BY criado_em ASC LIMIT ?
        `).all(limite);
    }

    async atualizarOperacao(id, status, resultado = null, erro = null) {
        this.db.prepare(`
            UPDATE operacoes_fila
            SET status = ?, resultado = ?, erro = ?,
                tentativas = tentativas + 1,
                processado_em = CASE WHEN ? IN ('concluido', 'erro') THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        `).run(status, resultado ? JSON.stringify(resultado) : null, erro, status, id);
    }

    // ============ PREÇOS ============

    async registrarMudancaPreco(produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo) {
        this.db.prepare(`
            INSERT INTO precos_historico
            (produto_id, preco_anterior, preco_novo, margem_anterior, margem_nova, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
        `).run(produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo);
    }

    async getHistoricoPrecos(produtoId, dias = 30) {
        return this.db.prepare(`
            SELECT * FROM precos_historico
            WHERE produto_id = ? AND timestamp > datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        `).all(produtoId, dias);
    }

    // ============ EVENTOS ============

    async registrarEvento(origem, destino, evento, dados) {
        this.db.prepare(`
            INSERT INTO eventos (origem, destino, evento, dados)
            VALUES (?, ?, ?, ?)
        `).run(origem, destino, evento, JSON.stringify(dados));
    }

    async getEventosPendentes(destino = null) {
        if (destino) {
            return this.db.prepare(
                'SELECT * FROM eventos WHERE processado = 0 AND (destino = ? OR destino IS NULL) ORDER BY timestamp ASC'
            ).all(destino);
        }
        return this.db.prepare(
            'SELECT * FROM eventos WHERE processado = 0 ORDER BY timestamp ASC'
        ).all();
    }

    async marcarEventoProcessado(id) {
        this.db.prepare('UPDATE eventos SET processado = 1 WHERE id = ?').run(id);
    }

    // ============ ANÁLISE ============

    async getResumoSistema() {
        const agentes = this.db.prepare('SELECT COUNT(*) as total FROM agentes_estado').get();
        const produtos = this.db.prepare('SELECT COUNT(*) as total FROM produtos').get();
        const ativos = this.db.prepare("SELECT COUNT(*) as total FROM produtos WHERE status = 'ativo'").get();
        const fila = this.db.prepare("SELECT COUNT(*) as total FROM operacoes_fila WHERE status = 'pendente'").get();
        const logsHoje = this.db.prepare(
            "SELECT COUNT(*) as total FROM logs WHERE date(timestamp) = date('now')"
        ).get();

        return {
            agentes: agentes.total,
            produtos: { total: produtos.total, ativos: ativos.total },
            operacoesPendentes: fila.total,
            logsHoje: logsHoje.total
        };
    }

    async fechar() {
        if (this.db) {
            this.db.close();
            this.db = null;
        }
    }
}

// Singleton
let instancia = null;

export async function getDatabase() {
    if (!instancia) {
        instancia = new Database();
        await instancia.conectar();
    }
    return instancia;
}

export { Database };
