// =====================================================
// SKILL 2 — CRIAÇÃO DO SITE 🏗️
// =====================================================
// Responsável EXCLUSIVAMENTE por desenvolver toda a
// estrutura do site. NÃO escolhe produtos. NÃO faz marketing.
// Foco: UX de conversão, mobile-first, design profissional.
// =====================================================

class SkillCriacaoSite {
    constructor() {
        this.nome = 'Criação do Site';
        this.id = 'criacao_site';
        this.activa = true;

        // Configurações do site
        this.config = {
            nomeLoja: 'TechZone',
            estilo: 'dark-tech',        // Tema visual
            focoMobile: true,            // Mobile-first
            moeda: 'BRL',               // Moeda padrão
            idioma: 'pt-BR'
        };

        // Páginas disponíveis no site
        this.paginas = {
            home: { status: 'concluido', arquivo: 'index.html' },
            produto: { status: 'pendente', arquivo: 'produto.html' },
            carrinho: { status: 'parcial', arquivo: 'index.html' },  // Sidebar já feita
            checkout: { status: 'pendente', arquivo: 'checkout.html' },
            conta: { status: 'pendente', arquivo: 'conta.html' },
            rastreamento: { status: 'pendente', arquivo: 'rastreamento.html' }
        };

        // Componentes reutilizáveis
        this.componentes = [
            'navbar', 'hero', 'catalogo', 'carrinho-sidebar',
            'filtro-categorias', 'card-produto', 'footer',
            'como-funciona', 'referencias-mercado',
            'problemas-mercado', 'oportunidade'
        ];
    }

    // -------------------------------------------------
    // EXECUTAR: Ponto de entrada da skill
    // -------------------------------------------------
    async executar(comando, contexto = null) {
        console.log(`🏗️ Skill 2 activada: ${comando}`);

        try {
            // Se recebeu produtos da Skill 1, gerar páginas para eles
            if (contexto && contexto.produtos) {
                const paginasGeradas = this.gerarPaginasProdutos(contexto.produtos);
                return {
                    status: 'sucesso',
                    skill: this.id,
                    dados: {
                        paginas_geradas: paginasGeradas,
                        total_paginas: paginasGeradas.length,
                        config: this.config
                    },
                    proximo_passo: 'marketing',
                    timestamp: new Date().toISOString()
                };
            }

            // Caso contrário, retornar status actual do site
            return {
                status: 'sucesso',
                skill: this.id,
                dados: {
                    paginas: this.paginas,
                    componentes: this.componentes,
                    config: this.config,
                    progresso: this.calcularProgresso()
                },
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        } catch (erro) {
            return {
                status: 'erro',
                skill: this.id,
                dados: null,
                mensagem: `Erro na criação do site: ${erro.message}`,
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        }
    }

    // -------------------------------------------------
    // GERAR PÁGINAS: Criar página individual por produto
    // -------------------------------------------------
    gerarPaginasProdutos(produtos) {
        return produtos.map(produto => ({
            nome: produto.nome,
            slug: this.criarSlug(produto.nome),
            template: 'produto.html',
            dados: {
                titulo: produto.nome,
                preco: produto.precoVenda,
                descricao: produto.nome,
                categoria: produto.categoria,
                score: produto.score,
                tempoEntrega: produto.tempoEntrega
            }
        }));
    }

    // -------------------------------------------------
    // PROGRESSO: Calcular % de conclusão do site
    // -------------------------------------------------
    calcularProgresso() {
        const total = Object.keys(this.paginas).length;
        const concluidas = Object.values(this.paginas)
            .filter(p => p.status === 'concluido').length;
        const parciais = Object.values(this.paginas)
            .filter(p => p.status === 'parcial').length;

        return {
            percentagem: Math.round(((concluidas + parciais * 0.5) / total) * 100),
            concluidas: concluidas,
            parciais: parciais,
            pendentes: total - concluidas - parciais,
            total: total
        };
    }

    // -------------------------------------------------
    // HELPER: Criar slug a partir do nome
    // -------------------------------------------------
    criarSlug(nome) {
        return nome
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')   // Remover acentos
            .replace(/[^a-z0-9]+/g, '-')        // Substituir espaços/especiais por -
            .replace(/(^-|-$)/g, '');            // Remover - no início/fim
    }
}

export { SkillCriacaoSite };
