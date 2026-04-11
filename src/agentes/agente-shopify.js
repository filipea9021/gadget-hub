// =====================================================
// AGENTE SHOPIFY — Gerencia a loja via Admin API
// =====================================================
// Capacidades:
// - Sincronizar produtos (criar, atualizar, deletar)
// - Gerenciar coleções e categorias
// - Ajustar preços e inventário
// - Processar pedidos
// - Gerar relatórios de vendas
// =====================================================

import { AgenteBase } from '../core/agente-base.js';
import { getDatabase } from '../core/database.js';

class AgenteShopify extends AgenteBase {
    constructor(config) {
        super({
            id: 'shopify',
            nome: 'Agente Shopify',
            descricao: 'Gerencia produtos, preços e pedidos na loja Shopify',
            intervaloMinutos: 30, // Executa a cada 30 minutos
            ...config
        });

        this.shopifyConfig = {
            shopDomain: process.env.SHOPIFY_SHOP_DOMAIN,
            accessToken: process.env.SHOPIFY_ACCESS_TOKEN,
            apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01'
        };

        this.ultimoSyncProdutos = null;
    }

    async _tarefa() {
        const acoes = [];
        const resultados = {
            produtosSync: 0,
            precosAtualizados: 0,
            pedidosProcessados: 0,
            erros: []
        };

        try {
            // Garantir que database está inicializado
            if (!this.db) {
                this.db = await getDatabase();
            }

            // 1. Processar fila de operações pendentes do SQLite
            const operacoesProcessadas = await this._processarFilaSQLite();
            acoes.push(...operacoesProcessadas);

            // 2. Verificar produtos que precisam de atualização
            const produtosAtualizados = await this._syncProdutosPendentes();
            if (produtosAtualizados.length > 0) {
                resultados.produtosSync = produtosAtualizados.length;
                acoes.push('produtos_sync');
            }

            // 3. Verificar e ajustar preços competitivos
            const precosAjustados = await this._verificarPrecos();
            if (precosAjustados.length > 0) {
                resultados.precosAtualizados = precosAjustados.length;
                acoes.push('precos_ajustados');
            }

            // 4. Processar pedidos pendentes (se houver integração CJ)
            const pedidos = await this._processarPedidos();
            if (pedidos.length > 0) {
                resultados.pedidosProcessados = pedidos.length;
                acoes.push('pedidos_processados');
            }

            this.ultimoSyncProdutos = new Date().toISOString();

            return {
                sucesso: resultados.erros.length === 0,
                acoes,
                dados: resultados,
                mensagem: `Sync completo: ${resultados.produtosSync} produtos, ${resultados.precosAtualizados} preços ajustados`
            };

        } catch (erro) {
            resultados.erros.push(erro.message);
            return {
                sucesso: false,
                acoes,
                dados: resultados,
                mensagem: `Erro no sync: ${erro.message}`
            };
        }
    }

    // ============ OPERAÇÕES DE PRODUTOS (APIs REAIS) ============

    async criarProduto(dadosProduto) {
        // Verificar se já existe produto com mesmo SKU
        const existente = await this._buscarProdutoPorSKU(dadosProduto.sku);
        if (existente) {
            this._log('aviso', `Produto com SKU ${dadosProduto.sku} já existe: ${existente.id}`);
            return { sucesso: false, produtoExistente: true, data: existente };
        }

        const mutation = `
            mutation productCreate($input: ProductInput!) {
                productCreate(input: $input) {
                    product {
                        id
                        title
                        handle
                        status
                        variants(first: 1) {
                            edges {
                                node {
                                    id
                                    sku
                                }
                            }
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
        `;

        const variaveis = {
            input: {
                title: dadosProduto.nome,
                descriptionHtml: dadosProduto.descricao || `<p>${dadosProduto.nome}</p>`,
                vendor: dadosProduto.fornecedor || 'Gadget Hub',
                productType: this._mapearCategoria(dadosProduto.categoria),
                tags: dadosProduto.tags || [dadosProduto.categoria, 'cj-dropshipping'],
                status: 'ACTIVE',
                variants: [{
                    price: dadosProduto.precoVenda.toFixed(2),
                    compareAtPrice: dadosProduto.precoCompare ? dadosProduto.precoCompare.toFixed(2) : null,
                    inventoryManagement: 'SHOPIFY',
                    inventoryPolicy: 'DENY',
                    sku: dadosProduto.sku,
                    weight: dadosProduto.peso || 0.5,
                    weightUnit: 'KILOGRAMS',
                    requiresShipping: true,
                    taxable: true
                }],
                images: dadosProduto.imagens?.map(url => ({ src: url })) || []
            }
        };

        try {
            const resultado = await this._graphql(mutation, variaveis);
            
            if (resultado.data?.productCreate?.userErrors?.length > 0) {
                const erros = resultado.data.productCreate.userErrors;
                throw new Error(erros.map(e => e.message).join(', '));
            }

            const produto = resultado.data?.productCreate?.product;
            
            if (produto) {
                // Salvar no SQLite
                await this.db.salvarProduto({
                    id: produto.id,
                    nome: produto.title,
                    sku: dadosProduto.sku,
                    categoria: dadosProduto.categoria,
                    precoCusto: dadosProduto.precoCusto,
                    precoVenda: dadosProduto.precoVenda,
                    margem: dadosProduto.margem,
                    score: dadosProduto.score,
                    avaliacao: dadosProduto.avaliacao,
                    fornecedor: dadosProduto.fornecedor,
                    fornecedor_pid: dadosProduto.pid
                });

                await this.db.atualizarShopifyProductId(dadosProduto.pid, produto.id);

                this._log('info', `Produto criado na Shopify: ${produto.title} (${produto.id})`);
                return { sucesso: true, data: produto };
            }

            throw new Error('Resposta inesperada da API Shopify');

        } catch (erro) {
            this._log('erro', `Falha ao criar produto: ${erro.message}`);
            throw erro;
        }
    }

    async atualizarPreco(productId, novoPreco, compareAtPrice = null) {
        const mutation = `
            mutation productVariantUpdate($input: ProductVariantInput!) {
                productVariantUpdate(input: $input) {
                    productVariant {
                        id
                        price
                        compareAtPrice
                        product {
                            id
                            title
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
        `;

        const variaveis = {
            input: {
                id: productId,
                price: novoPreco.toFixed(2),
                ...(compareAtPrice && { compareAtPrice: compareAtPrice.toFixed(2) })
            }
        };

        try {
            const resultado = await this._graphql(mutation, variaveis);
            
            if (resultado.data?.productVariantUpdate?.userErrors?.length > 0) {
                throw new Error(resultado.data.productVariantUpdate.userErrors[0].message);
            }

            const variant = resultado.data?.productVariantUpdate?.productVariant;
            this._log('info', `Preço atualizado: ${variant?.product?.title} → ${novoPreco}€`);
            
            return { sucesso: true, data: variant };
        } catch (erro) {
            this._log('erro', `Falha ao atualizar preço: ${erro.message}`);
            throw erro;
        }
    }

    async atualizarEstoque(variantId, quantidade) {
        const mutation = `
            mutation inventoryAdjustQuantity($input: InventoryAdjustQuantityInput!) {
                inventoryAdjustQuantity(input: $input) {
                    inventoryLevel {
                        available
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
        `;

        const variaveis = {
            input: {
                inventoryLevelId: variantId,
                availableDelta: quantidade
            }
        };

        return await this._graphql(mutation, variaveis);
    }

    async listarProdutos(limit = 50) {
        const query = `
            query getProducts($first: Int!) {
                products(first: $first) {
                    edges {
                        node {
                            id
                            title
                            handle
                            status
                            totalInventory
                            variants(first: 1) {
                                edges {
                                    node {
                                        id
                                        price
                                        compareAtPrice
                                        sku
                                        inventoryQuantity
                                    }
                                }
                            }
                        }
                    }
                }
            }
        `;

        return await this._graphql(query, { first: limit });
    }

    // ============ MÉTODOS INTERNOS ============

    async _syncProdutosPendentes() {
        // Buscar operações pendentes do SQLite
        const operacoes = await this.db.getOperacoesPendentes(5);
        const resultados = [];

        for (const op of operacoes) {
            try {
                const dados = JSON.parse(op.dados);
                
                if (op.tipo === 'criar_produto') {
                    const resultado = await this.criarProduto(dados);
                    await this.db.atualizarOperacao(op.id, 'concluido', resultado);
                    resultados.push(resultado);
                }
            } catch (erro) {
                await this.db.atualizarOperacao(op.id, 'erro', null, erro.message);
                this._log('erro', `Falha na operação ${op.id}: ${erro.message}`);
            }
        }

        return resultados;
    }

    async _verificarPrecos() {
        // Lógica para verificar e ajustar preços baseada em regras
        const produtos = await this.listarProdutos(100);
        const ajustados = [];

        // Implementar lógica de pricing dinâmico aqui
        // Exemplo: ajustar preços baseado em margem mínima de 40%

        return ajustados;
    }

    async _processarPedidos() {
        // Integração com CJ Dropshipping para fulfillment automático
        return [];
    }

    async _processarFilaSQLite() {
        const operacoes = await this.db.getOperacoesPendentes(10);
        const acoes = [];

        for (const op of operacoes) {
            try {
                const dados = JSON.parse(op.dados);
                
                switch (op.tipo) {
                    case 'criar_produto':
                        await this.criarProduto(dados);
                        await this.db.atualizarOperacao(op.id, 'concluido');
                        acoes.push('produto_criado');
                        break;
                    case 'atualizar_preco':
                        await this.atualizarPreco(dados.productId, dados.novoPreco, dados.compareAtPrice);
                        await this.db.atualizarOperacao(op.id, 'concluido');
                        acoes.push('preco_atualizado');
                        break;
                    default:
                        this._log('aviso', `Tipo de operação desconhecido: ${op.tipo}`);
                }
            } catch (erro) {
                await this.db.atualizarOperacao(op.id, 'erro', null, erro.message);
                this._log('erro', `Falha na operação ${op.id}: ${erro.message}`);
            }
        }

        return acoes;
    }

    // ============ API HELPERS ============

    async _graphql(query, variaveis = {}) {
        if (!this.shopifyConfig.shopDomain || !this.shopifyConfig.accessToken) {
            throw new Error('Credenciais Shopify não configuradas');
        }

        const url = `https://${this.shopifyConfig.shopDomain}/admin/api/${this.shopifyConfig.apiVersion}/graphql.json`;
        
        try {
            const response = await this.fetchComRetry(url, {
                method: 'POST',
                headers: {
                    'X-Shopify-Access-Token': this.shopifyConfig.accessToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, variables: variaveis })
            });

            // Verificar erros de GraphQL
            if (response.errors) {
                const mensagens = response.errors.map(e => e.message).join(', ');
                throw new Error(`GraphQL Error: ${mensagens}`);
            }

            return response;
        } catch (erro) {
            this._log('erro', `GraphQL request failed: ${erro.message}`);
            throw erro;
        }
    }

    async _rest(endpoint, method = 'GET', body = null) {
        const url = `https://${this.shopifyConfig.shopDomain}/admin/api/${this.shopifyConfig.apiVersion}${endpoint}`;
        
        const options = {
            method,
            headers: {
                'X-Shopify-Access-Token': this.shopifyConfig.accessToken
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        return await this.fetchComRetry(url, options);
    }

    // ============ HELPERS ============

    async _buscarProdutoPorSKU(sku) {
        const query = `
            query getProductBySKU($query: String!) {
                products(first: 1, query: $query) {
                    edges {
                        node {
                            id
                            title
                            variants(first: 1) {
                                edges {
                                    node {
                                        id
                                        sku
                                        price
                                    }
                                }
                            }
                        }
                    }
                }
            }
        `;

        try {
            const resultado = await this._graphql(query, { query: `sku:${sku}` });
            const edges = resultado.data?.products?.edges;
            
            if (edges && edges.length > 0) {
                return edges[0].node;
            }
            return null;
        } catch (erro) {
            this._log('aviso', `Erro ao buscar SKU ${sku}: ${erro.message}`);
            return null;
        }
    }

    _mapearCategoria(categoria) {
        const mapa = {
            'smart-home': 'Casa Inteligente',
            'audio': 'Áudio',
            'acessorios': 'Acessórios Tech',
            'eletronicos': 'Eletrônicos',
            'gaming': 'Gaming',
            'wearables': 'Wearables',
            'cameras': 'Câmeras'
        };
        return mapa[categoria] || 'Eletrônicos';
    }

    // ============ INTERFACE PÚBLICA ============

    async adicionarProdutoFila(dadosProduto) {
        const operacaoId = await this.db.adicionarOperacao('criar_produto', dadosProduto);
        
        this._log('info', `Produto "${dadosProduto.nome}" adicionado à fila (op #${operacaoId})`);
        
        // Notificar outros agentes
        this.notificar('produto_na_fila', { 
            nome: dadosProduto.nome, 
            preco: dadosProduto.precoVenda,
            operacaoId 
        });
        
        return operacaoId;
    }

    async listarProdutosDB() {
        return await this.db.getProdutos({ status: 'ativo' });
    }
}

export { AgenteShopify };
