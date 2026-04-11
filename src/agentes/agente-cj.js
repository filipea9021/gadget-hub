// =====================================================
// AGENTE CJ DROPSHIPPING — Integração com fornecedor
// =====================================================
// Capacidades:
// - Buscar produtos no catálogo CJ
// - Sincronizar estoque e preços
// - Calcular fretes
// - Processar pedidos (fulfillment automático)
// - Rastrear envios
// =====================================================

import { AgenteBase } from '../core/agente-base.js';
import { getDatabase } from '../core/database.js';

class AgenteCJ extends AgenteBase {
    constructor(config) {
        super({
            id: 'cj-dropshipping',
            nome: 'Agente CJ Dropshipping',
            descricao: 'Integração com CJ Dropshipping para sourcing e fulfillment',
            intervaloMinutos: 60, // Verifica a cada hora
            ...config
        });

        this.cjConfig = {
            apiKey: process.env.CJ_API_KEY,
            apiSecret: process.env.CJ_API_SECRET,
            email: process.env.CJ_EMAIL,
            baseUrl: 'https://developers.cjdropshipping.com/api2.0/v1'
        };

        // Verificar credenciais
        if (!this.cjConfig.apiKey) {
            console.warn('⚠️  CJ_API_KEY não configurada. Agente CJ não funcionará.');
        }

        this.produtosMonitorados = new Map();
        this.categoriasAlvo = [
            'smart plug', 'bluetooth earphone', 'wireless charger', 'led strip',
            'phone holder', 'car accessories', 'kitchen gadgets'
        ];
    }

    async _tarefa() {
        const acoes = [];
        const resultados = {
            produtosEncontrados: 0,
            produtosValidados: 0,
            sincronizacoes: 0,
            pedidosProcessados: 0,
            alertas: []
        };

        try {
            // 1. Pesquisar novos produtos em categorias alvo
            const novosProdutos = await this._pesquisarNovosProdutos();
            if (novosProdutos.length > 0) {
                resultados.produtosEncontrados = novosProdutos.length;
                acoes.push('pesquisa_concluida');
            }

            // 2. Validar produtos encontrados (score, margem, avaliação)
            const produtosValidados = await this._validarProdutos(novosProdutos);
            if (produtosValidados.length > 0) {
                resultados.produtosValidados = produtosValidados.length;
                resultados._produtosValidados = produtosValidados; // Para uso interno
                acoes.push('produtos_validados');
                
                // Notificar agente Shopify para criar produtos
                this.notificar('novos_produtos_validados', { produtos: produtosValidados });
            }

            // 3. Sincronizar estoque dos produtos monitorados
            const sincronizacao = await this._sincronizarEstoque();
            if (sincronizacao.atualizados > 0) {
                resultados.sincronizacoes = sincronizacao.atualizados;
                acoes.push('estoque_sync');
            }

            // 4. Processar pedidos pendentes de fulfillment
            const pedidos = await this._processarPedidosPendentes();
            if (pedidos.length > 0) {
                resultados.pedidosProcessados = pedidos.length;
                acoes.push('pedidos_fulfillment');
            }

            // 5. Verificar rastreamento de envios
            const rastreamentos = await this._atualizarRastreamentos();
            if (rastreamentos.length > 0) {
                acoes.push('rastreamento_atualizado');
            }

            return {
                sucesso: true,
                acoes,
                dados: resultados,
                mensagem: `${resultados.produtosValidados} produtos validados, ${resultados.sincronizacoes} sincronizações`
            };

        } catch (erro) {
            return {
                sucesso: false,
                acoes,
                dados: resultados,
                mensagem: `Erro na integração CJ: ${erro.message}`
            };
        }
    }

    // ============ PESQUISA DE PRODUTOS ============

    async pesquisarProdutos(query, filtros = {}) {
        if (!this.cjConfig.apiKey) {
            throw new Error('API Key CJ não configurada');
        }

        const params = new URLSearchParams({
            name: query,
            pageNum: (filtros.pagina || 1).toString(),
            pageSize: (filtros.limite || 20).toString(),
            ...(filtros.sort && { sort: filtros.sort }),
            ...(filtros.order && { order: filtros.order })
        });

        const url = `${this.cjConfig.baseUrl}/product/list?${params}`;
        
        try {
            const resposta = await this.fetchComRetry(url, {
                method: 'GET',
                headers: {
                    'CJ-Access-Token': this.cjConfig.apiKey
                }
            });

            if (resposta.result === false) {
                throw new Error(resposta.message || 'Erro na API CJ');
            }

            return resposta.data?.list || [];
        } catch (erro) {
            this._log('erro', `Falha na pesquisa CJ: ${erro.message}`);
            throw erro;
        }
    }

    async _pesquisarNovosProdutos() {
        // Se não há API key, retornar dados de demonstração
        if (!this.cjConfig.apiKey) {
            this._log('aviso', 'Modo demonstração: retornando produtos simulados');
            return this._produtosDemonstracao();
        }

        const todosProdutos = [];
        
        for (const categoria of this.categoriasAlvo.slice(0, 3)) { // Limitar para não exceder rate limits
            try {
                this._log('info', `Pesquisando categoria: ${categoria}`);
                
                const produtos = await this.pesquisarProdutos(categoria, {
                    sort: 'orders',
                    order: 'desc',
                    limite: 10
                });
                
                // Adicionar metadados de categoria
                produtos.forEach(p => {
                    p.categoriaPesquisada = categoria;
                    p.fontePesquisa = 'cj-api';
                });
                
                todosProdutos.push(...produtos);
                
                // Delay para não sobrecarregar API (rate limit: 1 req/segundo)
                await new Promise(r => setTimeout(r, 1100));
            } catch (erro) {
                this._log('aviso', `Falha na pesquisa de ${categoria}: ${erro.message}`);
            }
        }

        // Remover duplicados
        const vistos = new Set();
        const unicos = todosProdutos.filter(p => {
            if (vistos.has(p.pid)) return false;
            vistos.add(p.pid);
            return true;
        });

        this._log('info', `${unicos.length} produtos únicos encontrados no CJ`);
        return unicos;
    }

    _produtosDemonstracao() {
        // Produtos simulados para teste sem API key
        return [
            {
                pid: 'DEMO001',
                productNameEn: 'Smart Plug WiFi 16A',
                productDesc: 'Smart plug compatível com Alexa e Google Home',
                productImage: 'https://example.com/smartplug.jpg',
                productReviewsRate: 4.6,
                productOrders: 8200,
                categoriaPesquisada: 'smart plug',
                fontePesquisa: 'demo'
            },
            {
                pid: 'DEMO002',
                productNameEn: 'Fone TWS Bluetooth 5.3',
                productDesc: 'Fones sem fio com cancelamento de ruído',
                productImage: 'https://example.com/fone.jpg',
                productReviewsRate: 4.7,
                productOrders: 9100,
                categoriaPesquisada: 'bluetooth earphone',
                fontePesquisa: 'demo'
            }
        ];
    }

    // ============ VALIDAÇÃO ============

    async _validarProdutos(produtos) {
        const validados = [];
        
        for (const produto of produtos.slice(0, 10)) { // Limitar para não exceder rate limits
            try {
                // Buscar detalhes completos
                const detalhes = await this._buscarDetalhesProduto(produto.pid);
                
                // Buscar variações e preços
                const variantes = await this._buscarVariantes(produto.pid);
                if (!variantes.length) continue;

                const melhorVariante = variantes[0]; // Primeira variação
                
                // Calcular métricas
                const precoCusto = parseFloat(melhorVariante.variantPrice);
                const precoVenda = this._calcularPrecoVenda(precoCusto);
                const margem = ((precoVenda - precoCusto) / precoVenda) * 100;
                
                // Critérios de validação
                const criterios = {
                    avaliacaoOk: (produto.productReviewsRate || 0) >= 4.0,
                    pedidosOk: (produto.productOrders || 0) >= 100,
                    margemOk: margem >= 40,
                    estoqueOk: (melhorVariante.variantInventory || 0) >= 10
                };

                const score = this._calcularScore(produto, margem, criterios);

                if (Object.values(criterios).every(Boolean)) {
                    validados.push({
                        pid: produto.pid,
                        nome: produto.productNameEn,
                        descricao: produto.productDesc || '',
                        sku: melhorVariante.variantSku,
                        precoCusto,
                        precoVenda,
                        margem: margem.toFixed(1),
                        score,
                        avaliacao: produto.productReviewsRate || 4.0,
                        pedidos: produto.productOrders || 0,
                        estoque: melhorVariante.variantInventory,
                        imagens: produto.productImage?.split(',') || [],
                        categoria: produto.categoriaPesquisada,
                        peso: melhorVariante.variantWeight,
                        fornecedor: 'CJ Dropshipping'
                    });
                }
            } catch (erro) {
                this._log('aviso', `Falha na validação do produto ${produto.pid}: ${erro.message}`);
            }
        }

        return validados.sort((a, b) => b.score - a.score);
    }

    _calcularScore(produto, margem, criterios) {
        const avaliacaoPeso = ((produto.productReviewsRate || 4) / 5) * 25;
        const margemPeso = Math.min((margem / 80) * 25, 25);
        const pedidosPeso = Math.min(((produto.productOrders || 0) / 5000) * 25, 25);
        const criteriosPeso = Object.values(criterios).filter(Boolean).length * 6.25;
        
        return Math.round(avaliacaoPeso + margemPeso + pedidosPeso + criteriosPeso);
    }

    _calcularPrecoVenda(precoCusto) {
        // Preço psicológico com margem mínima de 40%
        const precoMinimo = precoCusto * 1.67; // 40% margem
        const precoPsicologico = Math.ceil(precoMinimo / 10) * 10 - 0.10;
        return precoPsicologico;
    }

    // ============ ESTOQUE E SINCRONIZAÇÃO ============

    async _sincronizarEstoque() {
        const atualizados = { count: 0, produtos: [] };
        
        for (const [pid, info] of this.produtosMonitorados) {
            try {
                const variantes = await this._buscarVariantes(pid);
                
                if (variantes.length > 0) {
                    const estoqueAtual = variantes[0].variantInventory;
                    
                    if (estoqueAtual !== info.ultimoEstoque) {
                        this.produtosMonitorados.set(pid, {
                            ...info,
                            ultimoEstoque: estoqueAtual,
                            ultimaVerificacao: new Date().toISOString()
                        });
                        
                        atualizados.count++;
                        atualizados.produtos.push({ pid, estoque: estoqueAtual });
                        
                        // Alertar se estoque baixo
                        if (estoqueAtual < 5) {
                            this.notificar('estoque_baixo', { pid, estoque: estoqueAtual });
                        }
                    }
                }
            } catch (erro) {
                this._log('aviso', `Falha ao sincronizar ${pid}: ${erro.message}`);
            }
        }

        return atualizados;
    }

    // ============ FULFILLMENT ============

    async criarPedido(dadosPedido) {
        const url = `${this.cjConfig.baseUrl}/shopping/order/createOrder`;
        
        const payload = {
            email: dadosPedido.email,
            name: dadosPedido.nomeCliente,
            country: dadosPedido.pais,
            province: dadosPedido.estado,
            city: dadosPedido.cidade,
            address: dadosPedido.endereco,
            zip: dadosPedido.cep,
            phone: dadosPedido.telefone,
            remark: `Pedido Shopify #${dadosPedido.shopifyOrderId}`,
            products: dadosPedido.produtos.map(p => ({
                vid: p.variantId,
                quantity: p.quantidade
            }))
        };

        return await this.fetchComRetry(url, {
            method: 'POST',
            headers: {
                'CJ-Access-Token': this.cjConfig.apiKey
            },
            body: JSON.stringify(payload)
        });
    }

    async _processarPedidosPendentes() {
        // Receber pedidos pendentes do agente Shopify
        // Implementar fulfillment automático
        return [];
    }

    async _atualizarRastreamentos() {
        const atualizacoes = [];
        
        // Buscar pedidos em trânsito
        // Atualizar status no Shopify
        
        return atualizacoes;
    }

    // ============ API HELPERS ============

    async _buscarDetalhesProduto(pid) {
        if (pid.startsWith('DEMO')) {
            return null; // Produtos de demonstração não têm detalhes
        }

        const url = `${this.cjConfig.baseUrl}/product/query?pid=${pid}`;
        
        try {
            const resposta = await this.fetchComRetry(url, {
                headers: { 'CJ-Access-Token': this.cjConfig.apiKey }
            });
            
            return resposta.data;
        } catch (erro) {
            this._log('aviso', `Erro ao buscar detalhes de ${pid}: ${erro.message}`);
            return null;
        }
    }

    async _buscarVariantes(pid) {
        if (pid.startsWith('DEMO')) {
            // Retornar variantes simuladas para produtos de demo
            return [{
                variantSku: `${pid}-001`,
                variantPrice: (Math.random() * 10 + 5).toFixed(2),
                variantInventory: Math.floor(Math.random() * 100) + 20,
                variantWeight: 0.3
            }];
        }

        const url = `${this.cjConfig.baseUrl}/product/variant/query?pid=${pid}`;
        
        try {
            const resposta = await this.fetchComRetry(url, {
                headers: { 'CJ-Access-Token': this.cjConfig.apiKey }
            });
            
            return resposta.data || [];
        } catch (erro) {
            this._log('aviso', `Erro ao buscar variantes de ${pid}: ${erro.message}`);
            return [];
        }
    }

    // ============ INTERFACE PÚBLICA ============

    async monitorarProduto(pid, shopifyProductId) {
        this.produtosMonitorados.set(pid, {
            shopifyProductId,
            pid,
            ultimoEstoque: null,
            ultimaVerificacao: null
        });

        // Também salvar no banco para persistência
        const produto = await this.db?.getProdutos({ fornecedor_pid: pid });
        if (produto && produto[0]) {
            await this.db.atualizarShopifyProductId(pid, shopifyProductId);
        }

        this._log('info', `Produto ${pid} adicionado ao monitoramento → Shopify ${shopifyProductId}`);
    }

    adicionarCategoria(categoria) {
        if (!this.categoriasAlvo.includes(categoria)) {
            this.categoriasAlvo.push(categoria);
        }
    }
}

export { AgenteCJ };
