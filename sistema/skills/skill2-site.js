// =====================================================
// SKILL 2 — CRIAÇÃO DO SITE
// =====================================================

class SkillCriacaoSite {
    constructor() {
        this.nome = 'Criação do Site';
        this.id = 'criacao_site';
        this.activa = true;
        this.config = { nomeLoja: 'Gadget Hub', estilo: 'dark-tech', focoMobile: true, moeda: 'EUR', idioma: 'pt-PT' };
        this.paginas = {
            home: { status: 'concluido', arquivo: 'index.html' },
            produto: { status: 'concluido', arquivo: 'produto.html' },
            checkout: { status: 'concluido', arquivo: 'checkout.html' }
        };
        this.componentes = ['navbar', 'hero', 'catalogo', 'carrinho-sidebar', 'filtro-categorias', 'card-produto', 'footer', 'chatbot'];
    }

    async executar(comando, contexto = null) {
        console.log('Skill 2 activada: ' + comando);
        try {
            if (contexto && contexto.produtos) {
                const paginasGeradas = this.gerarPaginasProdutos(contexto.produtos);
                return { status: 'sucesso', skill: this.id, dados: { paginas_geradas: paginasGeradas, total_paginas: paginasGeradas.length, config: this.config }, proximo_passo: 'marketing', timestamp: new Date().toISOString() };
            }
            return { status: 'sucesso', skill: this.id, dados: { paginas: this.paginas, componentes: this.componentes, config: this.config, progresso: this.calcularProgresso() }, proximo_passo: null, timestamp: new Date().toISOString() };
        } catch (erro) {
            return { status: 'erro', skill: this.id, dados: null, mensagem: erro.message, proximo_passo: null, timestamp: new Date().toISOString() };
        }
    }

    gerarPaginasProdutos(produtos) {
        return produtos.map(produto => ({ nome: produto.nome, slug: this.criarSlug(produto.nome), template: 'produto.html', dados: { titulo: produto.nome, preco: produto.precoVenda, categoria: produto.categoria, score: produto.score } }));
    }

    calcularProgresso() {
        const total = Object.keys(this.paginas).length;
        const concluidas = Object.values(this.paginas).filter(p => p.status === 'concluido').length;
        return { percentagem: Math.round((concluidas / total) * 100), concluidas, pendentes: total - concluidas, total };
    }

    criarSlug(nome) {
        return nome.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    }
}

export { SkillCriacaoSite };
