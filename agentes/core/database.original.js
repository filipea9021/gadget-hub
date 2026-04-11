// =====================================================
// DATABASE — Camada de persistência SQLite
// =====================================================
// Responsabilidades:
// - Gerenciar conexão SQLite
// - Criar/atualizar schema
// - CRUD para todos os agentes
// - Queries analíticas
// =====================================================

import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';

class Database {
    constructor() {
        this.db = null;
        // Caminho relativo à pasta agentes (onde o processo roda)
        this.dbPath = './data/gadgethub.db';
    }

    async conectar() {
        if (this.db) return this.db;

        this.db = await open({
            filename: this.dbPath,
            driver: sqlite3.Database
        });

        await this._criarSchema();
        console.log('💾 Database conectado:', this.dbPath);
        return this.db;
    }

    async _criarSchema() {
        // Estados dos agentes
        await this.db.exec(`
            CREATE TABLE IF NOT EXISTS agentes_estado (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                status TEXT DEFAULT 'parado',
                ultima_execucao TEXT,
                proxima_execucao TEXT,
                intervalo_minutos INTEGER DEFAULT 60,
                historico TEXT, -- JSON array
                configuracao TEXT, -- JSON object
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Logs estruturados
        await this.db.exec(`
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                agente_id TEXT,
                nivel TEXT CHECK(nivel IN ('info', 'aviso', 'erro', 'debug')),
                mensagem TEXT,
                dados TEXT -- JSON opcional
            )
        `);

        // Produtos rastreados
        await this.db.exec(`
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
                status TEXT DEFAULT 'ativo', -- ativo, pausado, sem_estoque
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Operações pendentes (fila)
        await this.db.exec(`
            CREATE TABLE IF NOT EXISTS operacoes_fila (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL, -- criar_produto, atualizar_preco, etc
                status TEXT DEFAULT 'pendente', -- pendente, processando, concluido, erro
                dados TEXT NOT NULL, -- JSON com parâmetros
                resultado TEXT, -- JSON com resultado
                erro TEXT,
                tentativas INTEGER DEFAULT 0,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                processado_em TEXT
            )
        `);

        // Preços histórico
        await this.db.exec(`
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
        await this.db.exec(`
            CREATE TABLE IF NOT EXISTS campanhas (
                id TEXT PRIMARY KEY,
                nome TEXT,
                produto_id TEXT,
                canais TEXT, -- JSON array
                orcamento_diario REAL,
                status TEXT DEFAULT 'ativa', -- ativa, pausada, concluida
                roas REAL,
                conversoes INTEGER DEFAULT 0,
                gasto_total REAL DEFAULT 0,
                criada_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Eventos entre agentes
        await this.db.exec(`
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
        await this.db.exec(`
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

        await this.db.run(`
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
        `, [agente.id, agente.nome, agente.status, agente.ultimaExecucao, 
            agente.proximaExecucao, agente.intervaloMinutos, historicoJSON, configJSON]);
    }

    async carregarEstadoAgente(agenteId) {
        const row = await this.db.get(
            'SELECT * FROM agentes_estado WHERE id = ?', 
            [agenteId]
        );
        
        if (!row) return null;

        return {
            ...row,
            historico: JSON.parse(row.historico || '[]'),
            configuracao: JSON.parse(row.configuracao || '{}')
        };
    }

    // ============ LOGS ============

    async adicionarLog(agenteId, nivel, mensagem, dados = null) {
        await this.db.run(`
            INSERT INTO logs (agente_id, nivel, mensagem, dados)
            VALUES (?, ?, ?, ?)
        `, [agenteId, nivel, mensagem, dados ? JSON.stringify(dados) : null]);
    }

    async getLogs(agenteId, limite = 100) {
        return await this.db.all(`
            SELECT * FROM logs 
            WHERE agente_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        `, [agenteId, limite]);
    }

    // ============ PRODUTOS ============

    async salvarProduto(produto) {
        await this.db.run(`
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
        `, [produto.id || produto.pid, produto.nome, produto.sku, produto.categoria,
            produto.precoCusto, produto.precoVenda, produto.margem, produto.score,
            produto.avaliacao, produto.fornecedor, produto.pid]);
    }

    async getProdutos(filtros = {}) {
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
        if (filtros.scoreMinimo) {
            query += ' AND score >= ?';
            params.push(filtros.scoreMinimo);
        }

        query += ' ORDER BY score DESC';
        return await this.db.all(query, params);
    }

    async atualizarShopifyProductId(pid, shopifyId) {
        await this.db.run(
            'UPDATE produtos SET shopify_product_id = ? WHERE fornecedor_pid = ?',
            [shopifyId, pid]
        );
    }

    // ============ FILA DE OPERAÇÕES ============

    async adicionarOperacao(tipo, dados) {
        const result = await this.db.run(`
            INSERT INTO operacoes_fila (tipo, dados)
            VALUES (?, ?)
        `, [tipo, JSON.stringify(dados)]);
        
        return result.lastID;
    }

    async getOperacoesPendentes(limite = 10) {
        return await this.db.all(`
            SELECT * FROM operacoes_fila 
            WHERE status = 'pendente' AND tentativas < 3
            ORDER BY criado_em ASC
            LIMIT ?
        `, [limite]);
    }

    async atualizarOperacao(id, status, resultado = null, erro = null) {
        await this.db.run(`
            UPDATE operacoes_fila 
            SET status = ?, resultado = ?, erro = ?, 
                tentativas = tentativas + 1,
                processado_em = CASE WHEN ? IN ('concluido', 'erro') THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        `, [status, resultado ? JSON.stringify(resultado) : null, erro, status, id]);
    }

    // ============ PREÇOS ============

    async registrarMudancaPreco(produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo) {
        await this.db.run(`
            INSERT INTO precos_historico 
            (produto_id, preco_anterior, preco_novo, margem_anterior, margem_nova, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
        `, [produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo]);
    }

    async getHistoricoPrecos(produtoId, dias = 30) {
        return await this.db.all(`
            SELECT * FROM precos_historico
            WHERE produto_id = ? AND timestamp > datetime('now', '-${dias} days')
            ORDER BY timestamp DESC
        `, [produtoId]);
    }

    // ============ EVENTOS ============

    async registrarEvento(origem, destino, evento, dados) {
        await this.db.run(`
            INSERT INTO eventos (origem, destino, evento, dados)
            VALUES (?, ?, ?, ?)
        `, [origem, destino, evento, JSON.stringify(dados)]);
    }

    async getEventosPendentes(destino = null) {
        let query = 'SELECT * FROM eventos WHERE processado = 0';
        const params = [];
        
        if (destino) {
            query += ' AND (destino = ? OR destino IS NULL)';
            params.push(destino);
        }
        
        query += ' ORDER BY timestamp ASC';
        return await this.db.all(query, params);
    }

    async marcarEventoProcessado(id) {
        await this.db.run(
            'UPDATE eventos SET processado = 1 WHERE id = ?',
            [id]
        );
    }

    // ============ ANÁLISE ============

    async getResumoSistema() {
        const agentes = await this.db.get('SELECT COUNT(*) as total FROM agentes_estado');
        const produtos = await this.db.get('SELECT COUNT(*) as total FROM produtos');
        const ativos = await this.db.get("SELECT COUNT(*) as total FROM produtos WHERE status = 'ativo'");
        const fila = await this.db.get("SELECT COUNT(*) as total FROM operacoes_fila WHERE status = 'pendente'");
        const logsHoje = await this.db.get(
            "SELECT COUNT(*) as total FROM logs WHERE date(timestamp) = date('now')"
        );

        return {
            agentes: agentes.total,
            produtos: { total: produtos.total, ativos: ativos.total },
            operacoesPendentes: fila.total,
            logsHoje: logsHoje.total
        };
    }

    async fechar() {
        if (this.db) {
            await this.db.close();
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
