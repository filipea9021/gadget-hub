// =====================================================
// PIPELINE IMPORTAÇÃO — CJ → Shopify
// =====================================================
// Orquestra o fluxo completo de importação de produtos:
// 1. Buscar produtos no CJ
// 2. Validar critérios (margem, avaliação, estoque)
// 3. Salvar no banco de dados
// 4. Criar na Shopify
// 5. Monitorar estoque e preços
// =====================================================

import { getDatabase } from './core/database.js';
import { AgenteCJ } from './cj-dropshipping/agente-cj.js';
import { AgenteShopify } from './shopify/agente-shopify.js';

class PipelineImportacao {
    constructor() {
        this.db = null;
        this.agenteCJ = null;
        this.agenteShopify = null;
        this.config = {
            margemMinima: 40,
            avaliacaoMinima: 4.0,
            pedidosMinimos: 100,
            estoqueMinimo: 10,
            limiteProdutosPorExecucao: 5
        };
    }

    async inicializar() {
        this.db = await getDatabase();
        this.agenteCJ = new AgenteCJ({ intervaloMinutos: 60 });
        this.agenteShopify = new AgenteShopify({ intervaloMinutos: 30 });
        
        await this.agenteCJ.inicializar();
        await this.agenteShopify.inicializar();
        
        console.log('✅ Pipeline de importação inicializado');
        return true;
    }

    // =====================================================
    // FLUXO PRINCIPAL
    // =====================================================

    async executarImportacaoCompleta() {
        console.log('\n🚀 Iniciando pipeline de importação...\n');
        
        const resultado = {
            inicio: new Date().toISOString(),
            etapas: {},
            produtosImportados: [],
            erros: []
        };

        try {
            // Etapa 1: Buscar produtos no CJ
            console.log('📦 Etapa 1: Buscando produtos no CJ...');
            const produtosCJ = await this._buscarProdutosCJ();
            resultado.etapas.busca = { 
                sucesso: true, 
                quantidade: produtosCJ.length 
            };
            console.log(`   ✅ ${produtosCJ.length} produtos encontrados\n`);

            // Etapa 2: Validar produtos
            console.log('🔍 Etapa 2: Validando produtos...');
            const produtosValidados = await this._validarProdutos(produtosCJ);
            resultado.etapas.validacao = { 
                sucesso: true, 
                quantidade: produtosValidados.length 
            };
            console.log(`   ✅ ${produtosValidados.length} produtos validados\n`);

            // Etapa 3: Salvar no banco
            console.log('💾 Etapa 3: Salvando no banco de dados...');
            const salvos = await this._salvarProdutos(produtosValidados);
            resultado.etapas.persistencia = { 
                sucesso: true, 
                quantidade: salvos.length 
            };
            console.log(`   ✅ ${salvos.length} produtos salvos\n`);

            // Etapa 4: Criar na Shopify (se configurado)
            if (process.env.SHOPIFY_ACCESS_TOKEN) {
                console.log('🛒 Etapa 4: Criando produtos na Shopify...');
                const criados = await this._criarProdutosShopify(salvos);
                resultado.etapas.shopify = { 
                    sucesso: true, 
                    quantidade: criados.length 
                };
                resultado.produtosImportados = criados;
                console.log(`   ✅ ${criados.length} produtos criados na Shopify\n`);
            } else {
                console.log('   ⚠️  Shopify não configurada. Produtos salvos apenas no banco.\n');
                resultado.etapas.shopify = { 
                    sucesso: false, 
                    motivo: 'SHOPIFY_ACCESS_TOKEN não configurado' 
                };
            }

            resultado.fim = new Date().toISOString();
            resultado.sucesso = true;
            
            console.log('✅ Pipeline concluído com sucesso!');
            
        } catch (erro) {
            resultado.sucesso = false;
            resultado.erros.push(erro.message);
            console.error('❌ Erro no pipeline:', erro.message);
        }

        return resultado;
    }

    // =====================================================
    // ETAPAS DO PIPELINE
    // =====================================================

    async _buscarProdutosCJ() {
        const categorias = [
            'smart plug',
            'bluetooth earphone', 
            'wireless charger',
            'led strip',
            'phone holder'
        ];

        const todosProdutos = [];

        for (const categoria of categorias.slice(0, 3)) {
            try {
                console.log(`   Buscando: ${categoria}...`);
                
                // Usar modo demonstração se API não disponível
                if (!this.agenteCJ.cjConfig.apiKey) {
                    const produtosDemo = this._produtosDemonstracao(categoria);
                    todosProdutos.push(...produtosDemo);
                    continue;
                }

                const produtos = await this.agenteCJ.pesquisarProdutos(categoria, {
                    sort: 'orders',
                    order: 'desc',
                    limite: 10
                });

                produtos.forEach(p => {
                    p.categoriaPesquisada = categoria;
                    p.fontePesquisa = 'cj-api';
                });

                todosProdutos.push(...produtos);
                
                // Delay para rate limit
                await new Promise(r => setTimeout(r, 1100));
                
            } catch (erro) {
                console.log(`   ⚠️  Falha em ${categoria}: ${erro.message}`);
                // Fallback para demonstração
                const produtosDemo = this._produtosDemonstracao(categoria);
                todosProdutos.push(...produtosDemo);
            }
        }

        // Remover duplicados
        const vistos = new Set();
        return todosProdutos.filter(p => {
            if (vistos.has(p.pid)) return false;
            vistos.add(p.pid);
            return true;
        });
    }

    _produtosDemonstracao(categoria) {
        // Produtos simulados para teste
        const produtos = [
            {
                pid: `DEMO-${categoria.replace(/\s/g, '-')}-001`,
                productNameEn: `Smart ${categoria} Premium`,
                productDesc: `Produto de alta qualidade para ${categoria}`,
                productImage: 'https://example.com/product.jpg',
                productReviewsRate: 4.5 + Math.random() * 0.5,
                productOrders: Math.floor(Math.random() * 5000) + 500,
                categoriaPesquisada: categoria,
                fontePesquisa: 'demo',
                variantes: [{
                    variantSku: `SKU-${Date.now()}-001`,
                    variantPrice: (Math.random() * 15 + 5).toFixed(2),
                    variantInventory: Math.floor(Math.random() * 100) + 50,
                    variantWeight: 0.3
                }]
            }
        ];
        return produtos;
    }

    async _validarProdutos(produtos) {
        const validados = [];

        for (const produto of produtos.slice(0, this.config.limiteProdutosPorExecucao)) {
            try {
                // Buscar variações
                let variantes = produto.variantes || [];
                
                if (!variantes.length && this.agenteCJ.cjConfig.apiKey) {
                    variantes = await this.agenteCJ._buscarVariantes(produto.pid);
                }

                if (!variantes.length) continue;

                const melhorVariante = variantes[0];
                const precoCusto = parseFloat(melhorVariante.variantPrice);
                const precoVenda = this._calcularPrecoVenda(precoCusto);
                const margem = ((precoVenda - precoCusto) / precoVenda) * 100;

                // Critérios de validação
                const criterios = {
                    avaliacaoOk: (produto.productReviewsRate || 0) >= this.config.avaliacaoMinima,
                    pedidosOk: (produto.productOrders || 0) >= this.config.pedidosMinimos,
                    margemOk: margem >= this.config.margemMinima,
                    estoqueOk: (melhorVariante.variantInventory || 0) >= this.config.estoqueMinimo
                };

                if (Object.values(criterios).every(Boolean)) {
                    const score = this._calcularScore(produto, margem, criterios);

                    validados.push({
                        pid: produto.pid,
                        nome: produto.productNameEn,
                        descricao: produto.productDesc || '',
                        sku: melhorVariante.variantSku,
                        categoria: produto.categoriaPesquisada,
                        precoCusto,
                        precoVenda,
                        margem: margem.toFixed(1),
                        score,
                        avaliacao: produto.productReviewsRate || 4.0,
                        pedidos: produto.productOrders || 0,
                        estoque: melhorVariante.variantInventory,
                        imagens: produto.productImage?.split(',') || ['https://example.com/product.jpg'],
                        peso: melhorVariante.variantWeight,
                        fornecedor: 'CJ Dropshipping',
                        fornecedorPid: produto.pid,
                        fonte: produto.fontePesquisa || 'cj-api'
                    });
                }
            } catch (erro) {
                console.log(`   ⚠️  Falha na validação de ${produto.pid}: ${erro.message}`);
            }
        }

        return validados.sort((a, b) => b.score - a.score);
    }

    _calcularPrecoVenda(precoCusto) {
        const precoMinimo = precoCusto * 1.67; // 40% margem
        const precoPsicologico = Math.ceil(precoMinimo / 10) * 10 - 0.10;
        return precoPsicologico;
    }

    _calcularScore(produto, margem, criterios) {
        const avaliacaoPeso = ((produto.productReviewsRate || 4) / 5) * 25;
        const margemPeso = Math.min((margem / 80) * 25, 25);
        const pedidosPeso = Math.min(((produto.productOrders || 0) / 5000) * 25, 25);
        const criteriosPeso = Object.values(criterios).filter(Boolean).length * 6.25;
        
        return Math.round(avaliacaoPeso + margemPeso + pedidosPeso + criteriosPeso);
    }

    async _salvarProdutos(produtos) {
        const salvos = [];

        for (const produto of produtos) {
            try {
                // Verificar se já existe
                const existente = await this.db.getProdutos({ sku: produto.sku });
                if (existente.length > 0) {
                    console.log(`   ⚠️  Produto ${produto.sku} já existe, pulando...`);
                    continue;
                }

                await this.db.salvarProduto(produto);
                salvos.push(produto);
                console.log(`   💾 ${produto.nome} (SKU: ${produto.sku})`);
                
            } catch (erro) {
                console.log(`   ❌ Erro ao salvar ${produto.nome}: ${erro.message}`);
            }
        }

        return salvos;
    }

    async _criarProdutosShopify(produtos) {
        const criados = [];

        for (const produto of produtos) {
            try {
                const resultado = await this.agenteShopify.criarProduto({
                    nome: produto.nome,
                    descricao: produto.descricao,
                    precoVenda: produto.precoVenda,
                    precoCompare: produto.precoVenda * 1.2,
                    categoria: produto.categoria,
                    tags: [produto.categoria, 'cj-dropshipping', 'importado'],
                    sku: produto.sku,
                    imagens: produto.imagens,
                    fornecedor: produto.fornecedor
                });

                if (resultado.sucesso) {
                    criados.push({
                        ...produto,
                        shopifyProductId: resultado.shopifyProductId,
                        shopifyVariantId: resultado.shopifyVariantId
                    });
                    
                    // Atualizar no banco com IDs Shopify
                    await this.db.atualizarShopifyProductId(
                        produto.fornecedorPid, 
                        resultado.shopifyProductId
                    );
                    
                    console.log(`   🛒 ${produto.nome} → Shopify ID: ${resultado.shopifyProductId}`);
                } else {
                    console.log(`   ⚠️  ${produto.nome}: ${resultado.mensagem}`);
                }
                
            } catch (erro) {
                console.log(`   ❌ Erro ao criar ${produto.nome}: ${erro.message}`);
            }
        }

        return criados;
    }

    // =====================================================
    // INTERFACE PÚBLICA
    // =====================================================

    async importarProduto(pid) {
        // Importar produto específico do CJ
        console.log(`🎯 Importando produto específico: ${pid}`);
        
        try {
            const detalhes = await this.agenteCJ._buscarDetalhesProduto(pid);
            const variantes = await this.agenteCJ._buscarVariantes(pid);
            
            if (!variantes.length) {
                throw new Error('Produto sem variações');
            }

            // Criar objeto compatível com validação
            const produto = {
                ...detalhes,
                pid,
                variantes,
                categoriaPesquisada: 'manual',
                fontePesquisa: 'manual'
            };

            const validados = await this._validarProdutos([produto]);
            
            if (validados.length === 0) {
                throw new Error('Produto não atende critérios de validação');
            }

            const salvos = await this._salvarProdutos(validados);
            
            if (process.env.SHOPIFY_ACCESS_TOKEN && salvos.length > 0) {
                const criados = await this._criarProdutosShopify(salvos);
                return criados[0];
            }
            
            return salvos[0];
            
        } catch (erro) {
            console.error(`❌ Erro ao importar ${pid}:`, erro.message);
            throw erro;
        }
    }

    async sincronizarEstoque() {
        // Sincronizar estoque de todos os produtos monitorados
        console.log('🔄 Sincronizando estoque...');
        
        const produtos = await this.db.getProdutos({ 
            status: 'ativo',
            fornecedor: 'CJ Dropshipping' 
        });

        const atualizacoes = [];

        for (const produto of produtos) {
            try {
                const variantes = await this.agenteCJ._buscarVariantes(produto.fornecedor_pid);
                
                if (variantes.length > 0) {
                    const estoqueAtual = variantes[0].variantInventory;
                    
                    if (estoqueAtual !== produto.estoque) {
                        await this.db.salvarProduto({
                            ...produto,
                            estoque: estoqueAtual,
                            atualizado_em: new Date().toISOString()
                        });
                        
                        atualizacoes.push({
                            sku: produto.sku,
                            estoqueAnterior: produto.estoque,
                            estoqueNovo: estoqueAtual
                        });

                        // Atualizar Shopify se configurado
                        if (produto.shopify_variant_id && process.env.SHOPIFY_ACCESS_TOKEN) {
                            await this.agenteShopify.atualizarEstoque(
                                produto.shopify_variant_id, 
                                estoqueAtual
                            );
                        }
                    }
                }
                
                await new Promise(r => setTimeout(r, 1000)); // Rate limit
                
            } catch (erro) {
                console.log(`   ⚠️  Falha ao sincronizar ${produto.sku}: ${erro.message}`);
            }
        }

        console.log(`✅ ${atualizacoes.length} produtos sincronizados`);
        return atualizacoes;
    }

    getConfig() {
        return this.config;
    }

    atualizarConfig(novaConfig) {
        this.config = { ...this.config, ...novaConfig };
        console.log('⚙️  Configuração atualizada:', this.config);
    }
}

export { PipelineImportacao };
