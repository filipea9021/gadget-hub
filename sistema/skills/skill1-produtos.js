// =====================================================
// SKILL 1 — PESQUISA DE PRODUTOS
// =====================================================

class SkillPesquisaProdutos {
    constructor() {
        this.nome = 'Pesquisa de Produtos';
        this.id = 'pesquisa_produtos';
        this.activa = true;
        this.criterios = { avaliacaoMinima: 4.0, margemMinima: 40, entregaMaxima: 15, pedidosMinimos: 100 };
        this.fontes = ['AliExpress', 'CJ Dropshipping', 'Zendrop'];
    }

    async executar(comando, contexto = null) {
        try {
            const produtosEncontrados = await this.pesquisarProdutos(comando);
            const produtosValidados = this.validarProdutos(produtosEncontrados);
            const produtosComScore = this.calcularScore(produtosValidados);
            return { status: 'sucesso', skill: this.id, dados: { total_encontrados: produtosEncontrados.length, total_validados: produtosComScore.length, produtos: produtosComScore, criterios_usados: this.criterios }, proximo_passo: produtosComScore.length > 0 ? 'criacao_site' : null, timestamp: new Date().toISOString() };
        } catch (erro) {
            return { status: 'erro', skill: this.id, dados: null, mensagem: erro.message, proximo_passo: null, timestamp: new Date().toISOString() };
        }
    }

    async pesquisarProdutos(query) {
        return [
            { nome: 'Smart Plug WiFi 16A', precoFornecedor: 8.00, precoVenda: 29.90, avaliacao: 4.6, pedidos: 8200, tempoEntrega: 8, fonte: 'CJ Dropshipping', categoria: 'smart-home' },
            { nome: 'Fone TWS Bluetooth 5.3', precoFornecedor: 18.00, precoVenda: 69.90, avaliacao: 4.7, pedidos: 9100, tempoEntrega: 7, fonte: 'CJ Dropshipping', categoria: 'audio' },
            { nome: 'Carregador Wireless 15W', precoFornecedor: 9.00, precoVenda: 34.90, avaliacao: 4.6, pedidos: 7300, tempoEntrega: 7, fonte: 'CJ Dropshipping', categoria: 'acessorios' }
        ];
    }

    validarProdutos(produtos) {
        return produtos.filter(p => {
            const margem = this.calcularMargem(p.precoFornecedor, p.precoVenda);
            return p.avaliacao >= this.criterios.avaliacaoMinima && margem >= this.criterios.margemMinima && p.tempoEntrega <= this.criterios.entregaMaxima && p.pedidos >= this.criterios.pedidosMinimos;
        });
    }

    calcularScore(produtos) {
        return produtos.map(p => {
            const margem = this.calcularMargem(p.precoFornecedor, p.precoVenda);
            const score = Math.round((p.avaliacao / 5) * 30 + Math.min((margem / 80) * 30, 30) + ((15 - p.tempoEntrega) / 15) * 20 + Math.min((p.pedidos / 5000) * 20, 20));
            return { ...p, margem: margem.toFixed(1), score };
        }).sort((a, b) => b.score - a.score);
    }

    calcularMargem(precoFornecedor, precoVenda) {
        return ((precoVenda - precoFornecedor) / precoVenda) * 100;
    }
}

export { SkillPesquisaProdutos };
