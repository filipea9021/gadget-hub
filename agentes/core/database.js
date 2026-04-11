// =====================================================
// DATABASE — Gadget Hub (estende Shared Database)
// =====================================================
// Adiciona tabelas específicas do e-commerce:
// produtos, precos_historico, campanhas.
// Mantém a mesma API que antes para retrocompatibilidade.
// =====================================================

import { SharedDatabase } from '../../../shared/core/database.js';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

class GadgetHubDatabase extends SharedDatabase {
    constructor() {
        const dbPath = resolve(__dirname, '..', '..', 'data', 'gadgethub.db');
        super(dbPath);
    }

    conectar() {
        super.conectar();
        this._criarSchemaGadgetHub();
        return this.db;
    }

    _criarSchemaGadgetHub() {
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
                criado_em TEXT DEFAULT (datetime('now')),
                atualizado_em TEXT DEFAULT (datetime('now'))
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
                timestamp TEXT DEFAULT (datetime('now'))
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
                criada_em TEXT DEFAULT (datetime('now'))
            )
        `);

        // Índices específicos
        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_produtos_fornecedor ON produtos(fornecedor_pid);
            CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);
        `);
    }

    // ============ PRODUTOS ============

    salvarProduto(produto) {
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
                atualizado_em = datetime('now')
        `).run(
            produto.id || produto.pid, produto.nome, produto.sku, produto.categoria,
            produto.precoCusto, produto.precoVenda, produto.margem, produto.score,
            produto.avaliacao, produto.fornecedor, produto.pid
        );
    }

    getProdutos(filtros = {}) {
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
        return this.db.prepare(query).all(...params);
    }

    atualizarShopifyProductId(pid, shopifyId) {
        this.db.prepare(
            'UPDATE produtos SET shopify_product_id = ? WHERE fornecedor_pid = ?'
        ).run(shopifyId, pid);
    }

    // ============ PREÇOS ============

    registrarMudancaPreco(produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo) {
        this.db.prepare(`
            INSERT INTO precos_historico
            (produto_id, preco_anterior, preco_novo, margem_anterior, margem_nova, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
        `).run(produtoId, precoAnterior, precoNovo, margemAnterior, margemNova, motivo);
    }

    getHistoricoPrecos(produtoId, dias = 30) {
        return this.db.prepare(`
            SELECT * FROM precos_historico
            WHERE produto_id = ? AND timestamp > datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        `).all(produtoId, dias);
    }

    // Override do resumo para incluir dados específicos
    getResumoSistema() {
        const base = super.getResumoSistema();
        const produtos = this.db.prepare('SELECT COUNT(*) as total FROM produtos').get();
        const ativos = this.db.prepare("SELECT COUNT(*) as total FROM produtos WHERE status = 'ativo'").get();

        return {
            ...base,
            produtos: { total: produtos.total, ativos: ativos.total }
        };
    }
}

// Singleton
let instancia = null;

function getDatabase() {
    if (!instancia) {
        instancia = new GadgetHubDatabase();
        instancia.conectar();
    }
    return instancia;
}

export { getDatabase, GadgetHubDatabase };
export default getDatabase;
