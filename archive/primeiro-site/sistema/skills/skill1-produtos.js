// =====================================================
// SKILL 1 — PESQUISA DE PRODUTOS 🔍
// =====================================================
// Responsável EXCLUSIVAMENTE por encontrar e validar
// produtos para o catálogo. NÃO cria site. NÃO faz marketing.
// =====================================================

class SkillPesquisaProdutos {
    constructor() {
        this.nome = 'Pesquisa de Produtos';
        this.id = 'pesquisa_produtos';
        this.activa = true;

        // Critérios mínimos de validação (do plano no Notion)
        this.criterios = {
            avaliacaoMinima: 4.0,       // Estrelas mínimas (de 5)
            margemMinima: 40,           // Margem de lucro mínima (%)
            entregaMaxima: 15,          // Dias máximos de entrega
            pedidosMinimos: 100         // Pedidos mínimos do fornecedor
        };

        // Fontes de pesquisa configuradas
        this.fontes = ['AliExpress', 'CJ Dropshipping', 'Zendrop'];
    }

    // -------------------------------------------------
    // EXECUTAR: Ponto de entrada da skill
    // -------------------------------------------------
    async executar(comando, contexto = null) {
        console.log(`🔍 Skill 1 activada: ${comando}`);

        try {
            // Simular pesquisa de produtos (futuro: integrar com APIs reais)
            const produtosEncontrados = await this.pesquisarProdutos(comando);
            const produtosValidados = this.validarProdutos(produtosEncontrados);
            const produtosComScore = this.calcularScore(produtosValidados);

            return {
                status: 'sucesso',
                skill: this.id,
                dados: {
                    total_encontrados: produtosEncontrados.length,
                    total_validados: produtosComScore.length,
                    produtos: produtosComScore,
                    criterios_usados: this.criterios
                },
                proximo_passo: produtosComScore.length > 0 ? 'criacao_site' : null,
                timestamp: new Date().toISOString()
            };
        } catch (erro) {
            return {
                status: 'erro',
                skill: this.id,
                dados: null,
                mensagem: `Erro na pesquisa: ${erro.message}`,
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        }
    }

    // -------------------------------------------------
    // PESQUISAR: Buscar produtos nas fontes
    // -------------------------------------------------
    async pesquisarProdutos(query) {
        // TODO: Integrar com APIs reais (AliExpress, CJ, Zendrop)
        // Por agora, retorna dados de exemplo para testar o fluxo

        return [
            {
                nome: 'Headset Gamer RGB 7.1',
                precoFornecedor: 45.00,
                precoVenda: 189.90,
                avaliacao: 4.7,
                pedidos: 3200,
                tempoEntrega: 8,
                fonte: 'CJ Dropshipping',
                link: 'https://cjdropshipping.com/exemplo1',
                categoria: 'perifericos'
            },
            {
                nome: 'Mouse Gamer 12000 DPI',
                precoFornecedor: 28.00,
                precoVenda: 129.90,
                avaliacao: 4.5,
                pedidos: 5100,
                tempoEntrega: 10,
                fonte: 'AliExpress',
                link: 'https://aliexpress.com/exemplo2',
                categoria: 'perifericos'
            },
            {
                nome: 'Teclado Mecânico RGB',
                precoFornecedor: 62.00,
                precoVenda: 249.90,
                avaliacao: 4.3,
                pedidos: 1800,
                tempoEntrega: 12,
                fonte: 'CJ Dropshipping',
                link: 'https://cjdropshipping.com/exemplo3',
                categoria: 'perifericos'
            },
            {
                nome: 'Controle Wireless Pro',
                precoFornecedor: 55.00,
                precoVenda: 219.90,
                avaliacao: 4.6,
                pedidos: 2400,
                tempoEntrega: 7,
                fonte: 'Zendrop',
                link: 'https://zendrop.com/exemplo4',
                categoria: 'acessorios'
            },
            {
                nome: 'Webcam Full HD 1080p',
                precoFornecedor: 38.00,
                precoVenda: 159.90,
                avaliacao: 3.8,
                pedidos: 900,
                tempoEntrega: 18,
                fonte: 'AliExpress',
                link: 'https://aliexpress.com/exemplo5',
                categoria: 'perifericos'
            },
            {
                nome: 'Fone Bluetooth Barato',
                precoFornecedor: 15.00,
                precoVenda: 22.00,
                avaliacao: 3.2,
                pedidos: 50,
                tempoEntrega: 25,
                fonte: 'AliExpress',
                link: 'https://aliexpress.com/exemplo6',
                categoria: 'acessorios'
            }
        ];
    }

    // -------------------------------------------------
    // VALIDAR: Filtrar produtos pelos critérios mínimos
    // -------------------------------------------------
    validarProdutos(produtos) {
        return produtos.filter(produto => {
            const margem = this.calcularMargem(produto.precoFornecedor, produto.precoVenda);

            const avaliacaoOk = produto.avaliacao >= this.criterios.avaliacaoMinima;
            const margemOk = margem >= this.criterios.margemMinima;
            const entregaOk = produto.tempoEntrega <= this.criterios.entregaMaxima;
            const pedidosOk = produto.pedidos >= this.criterios.pedidosMinimos;

            if (!avaliacaoOk) console.log(`  ❌ ${produto.nome}: avaliação baixa (${produto.avaliacao})`);
            if (!margemOk) console.log(`  ❌ ${produto.nome}: margem baixa (${margem.toFixed(1)}%)`);
            if (!entregaOk) console.log(`  ❌ ${produto.nome}: entrega lenta (${produto.tempoEntrega} dias)`);
            if (!pedidosOk) console.log(`  ❌ ${produto.nome}: poucos pedidos (${produto.pedidos})`);

            return avaliacaoOk && margemOk && entregaOk && pedidosOk;
        });
    }

    // -------------------------------------------------
    // SCORE: Calcular pontuação de cada produto (0-100)
    // -------------------------------------------------
    calcularScore(produtos) {
        return produtos.map(produto => {
            const margem = this.calcularMargem(produto.precoFornecedor, produto.precoVenda);

            // Pesos: avaliação (30%), margem (30%), entrega (20%), pedidos (20%)
            const scoreAvaliacao = (produto.avaliacao / 5) * 30;
            const scoreMargem = Math.min((margem / 80) * 30, 30);
            const scoreEntrega = ((15 - produto.tempoEntrega) / 15) * 20;
            const scorePedidos = Math.min((produto.pedidos / 5000) * 20, 20);

            const scoreTotal = Math.round(scoreAvaliacao + scoreMargem + scoreEntrega + scorePedidos);

            return {
                ...produto,
                margem: margem.toFixed(1),
                score: scoreTotal
            };
        }).sort((a, b) => b.score - a.score); // Ordenar por score (maior primeiro)
    }

    // -------------------------------------------------
    // HELPER: Calcular margem de lucro (%)
    // -------------------------------------------------
    calcularMargem(precoFornecedor, precoVenda) {
        return ((precoVenda - precoFornecedor) / precoVenda) * 100;
    }
}

export { SkillPesquisaProdutos };
