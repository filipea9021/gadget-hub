// =====================================================
// MAIN.JS — Ponto de entrada do sistema de agentes
// =====================================================
// Inicializa e coordena todos os agentes autônomos
// =====================================================

import { ManagerAgentes } from './core/manager-agentes.js';
import { AgenteShopify } from './shopify/agente-shopify.js';
import { AgenteCJ } from './cj-dropshipping/agente-cj.js';
import { AgentePrecos } from './pricing/agente-precos.js';
import { AgenteMarketing } from './marketing/agente-marketing.js';
import { AgenteEstoque } from './estoque/agente-estoque.js';
import { AgenteBlender } from './blender/agente-blender.js';

// =====================================================
// CONFIGURAÇÃO DO SISTEMA
// =====================================================

const CONFIG = {
    // Modo de operação
    modo: process.env.MODO || 'semi', // 'manual', 'semi', 'autonomo'
    
    // Intervalos (em minutos)
    intervalos: {
        shopify: 30,
        cj: 60,
        precos: 120,
        marketing: 180,
        estoque: 30,
        blender: 45
    },
    
    // Notificações
    notificacoes: {
        webhook: process.env.WEBHOOK_URL,
        email: process.env.NOTIFICATION_EMAIL
    },
    
    // Limites
    limites: {
        margemMinima: 40,
        estoqueMinimo: 5,
        roasMinimo: 2.0
    }
};

// =====================================================
// INICIALIZAÇÃO
// =====================================================

async function inicializarSistema() {
    console.log('╔════════════════════════════════════════════════════╗');
    console.log('║     🤖 GADGET HUB — Sistema de Agentes Autônomos   ║');
    console.log('║         Shopify + CJ Dropshipping                  ║');
    console.log('╚════════════════════════════════════════════════════╝\n');

    const manager = new ManagerAgentes();

    // Criar agentes
    const agenteShopify = new AgenteShopify({ intervaloMinutos: CONFIG.intervalos.shopify });
    const agenteCJ = new AgenteCJ({ intervaloMinutos: CONFIG.intervalos.cj });
    const agentePrecos = new AgentePrecos({ intervaloMinutos: CONFIG.intervalos.precos });
    const agenteMarketing = new AgenteMarketing({ intervaloMinutos: CONFIG.intervalos.marketing });
    const agenteEstoque = new AgenteEstoque({ intervaloMinutos: CONFIG.intervalos.estoque });
    const agenteBlender = new AgenteBlender({ intervaloMinutos: CONFIG.intervalos.blender });

    // Registrar no manager
    manager.registrar(agenteShopify);
    manager.registrar(agenteCJ);
    manager.registrar(agentePrecos);
    manager.registrar(agenteMarketing);
    manager.registrar(agenteEstoque);
    manager.registrar(agenteBlender);

    // Configurar comunicação entre agentes
    configurarComunicacao(manager, agenteShopify, agenteCJ, agentePrecos, agenteMarketing, agenteEstoque, agenteBlender);

    // Inicializar todos
    await manager.inicializarTodos();

    // Retornar sistema pronto
    return { manager, agentes: { agenteShopify, agenteCJ, agentePrecos, agenteMarketing, agenteEstoque, agenteBlender } };
}

function configurarComunicacao(manager, shopify, cj, precos, marketing, estoque, blender) {

    // =====================================================
    // PIPELINE: CJ → Shopify → Blender → Marketing
    // =====================================================

    // Agente CJ → Agente Shopify (novos produtos validados)
    cj.onNotificacao((notificacao) => {
        if (notificacao.evento === 'novos_produtos_validados') {
            console.log(`📦 ${notificacao.dados.produtos.length} produtos validados recebidos do CJ`);

            // Adicionar produtos à fila do Shopify
            for (const produto of notificacao.dados.produtos.slice(0, 5)) {
                shopify.adicionarProdutoFila({
                    nome: produto.nome,
                    descricao: produto.descricao,
                    precoVenda: produto.precoVenda,
                    precoCompare: produto.precoVenda * 1.2,
                    categoria: produto.categoria,
                    tags: [produto.categoria, 'cj-dropshipping'],
                    sku: produto.sku,
                    imagens: produto.imagens,
                    fornecedor: 'CJ Dropshipping'
                });
            }

            // ★ CJ → Blender: Solicitar renders para produtos novos
            for (const produto of notificacao.dados.produtos.slice(0, 5)) {
                console.log(`🎨 Solicitando renders 3D para: ${produto.nome}`);
                blender.solicitarRenderCompleto({
                    id: produto.id || produto.sku,
                    nome: produto.nome,
                    sku: produto.sku,
                    categoria: produto.categoria,
                    shopify_product_id: null // será atualizado quando Shopify criar
                });
            }
        }
    });

    // Agente Shopify → Agente Estoque (produtos criados)
    shopify.onNotificacao((notificacao) => {
        if (notificacao.evento === 'produto_na_fila') {
            // Registrar para monitoramento
            console.log(`📝 Produto "${notificacao.dados.nome}" será monitorado`);
        }

        // ★ Shopify → Blender: Quando produto é criado no Shopify, atualizar o shopifyProductId nos jobs
        if (notificacao.evento === 'produto_criado') {
            console.log(`🎨 Produto "${notificacao.dados.nome}" criado no Shopify — vinculando renders`);
            // Os renders já foram solicitados pelo CJ, agora vinculamos ao ID do Shopify
        }
    });

    // ★ Blender → Shopify: Quando renders ficam prontos, atualizar imagens do produto
    blender.onNotificacao((notificacao) => {
        if (notificacao.evento === 'renders_prontos') {
            const { produtoId, shopifyProductId, renders, animacoes } = notificacao.dados;
            console.log(`🖼️ Renders prontos: ${renders.length} imagens + ${animacoes.length} vídeos para produto ${produtoId}`);

            // Em modo autônomo, atualizar imagens no Shopify automaticamente
            if (CONFIG.modo === 'autonomo' && shopifyProductId) {
                console.log(`📤 Enviando renders para Shopify — produto ${shopifyProductId}`);
                // shopify.atualizarImagens(shopifyProductId, renders);
            }

            // ★ Blender → Marketing: Renders prontos disponíveis para campanhas
            console.log(`📢 Renders disponíveis para campanhas de marketing`);
            marketing.emit('notificacao_recebida', {
                origem: 'blender',
                evento: 'renders_disponiveis',
                dados: {
                    produtoId,
                    renders: renders.map(r => r.url),
                    animacoes: animacoes.map(a => a.url)
                },
                timestamp: new Date().toISOString()
            });
        }
    });

    // Agente Preços → Agente Shopify (ajuste de preço)
    precos.onNotificacao((notificacao) => {
        if (notificacao.evento === 'ajustar_preco') {
            console.log(`💰 Preço ajustado: ${notificacao.dados.motivo}`);
            // Em modo autônomo, aplicaria automaticamente
            if (CONFIG.modo === 'autonomo') {
                shopify.atualizarPreco(notificacao.dados.produtoId, notificacao.dados.novoPreco);
            }
        }
    });

    // Agente Estoque → Agente Marketing (estoque baixo)
    estoque.onNotificacao((notificacao) => {
        if (notificacao.evento === 'estoque_alerta') {
            console.log(`⚠️ Alerta de estoque: ${notificacao.dados.mensagem}`);

            if (notificacao.dados.nivel === 'critico') {
                // Pausar campanhas para este produto
                marketing.pausarCampanhaPorProduto(notificacao.dados.produtoId);
            }
        }
    });

    // Agente Marketing → Manager (relatórios)
    marketing.onNotificacao((notificacao) => {
        if (notificacao.evento === 'campanha_criada') {
            console.log(`📢 Nova campanha: ${notificacao.dados.produto}`);
        }
    });
}

// =====================================================
// COMANDOS MANUAIS
// =====================================================

async function comandoExecutarAgente(manager, agenteId) {
    console.log(`\n▶️ Executando agente: ${agenteId}`);
    const resultado = await manager.executarAgente(agenteId);
    console.log('Resultado:', JSON.stringify(resultado, null, 2));
    return resultado;
}

async function comandoStatus(manager) {
    const status = manager.getStatusCompleto();
    console.log('\n📊 Status do Sistema:');
    console.table(status.agentes.map(a => ({
        Agente: a.nome,
        Status: a.status,
        'Última Execução': a.ultimaExecucao ? new Date(a.ultimaExecucao).toLocaleTimeString() : 'Nunca',
        'Próxima Execução': a.proximaExecucao ? new Date(a.proximaExecucao).toLocaleTimeString() : 'Aguardando'
    })));
    return status;
}

async function comandoAdicionarProduto(manager, dadosProduto) {
    console.log(`\n➕ Adicionando produto: ${dadosProduto.nome}`);
    // Implementar lógica
}

// =====================================================
// EXECUÇÃO
// =====================================================

async function main() {
    try {
        const { manager, agentes } = await inicializarSistema();

        // Menu de comandos baseado no modo
        if (CONFIG.modo === 'autonomo') {
            console.log('\n🤖 Modo AUTÔNOMO — Iniciando execução contínua...\n');
            manager.iniciarTodos();
            
            // Relatório periódico
            setInterval(async () => {
                const arquivo = await manager.exportarRelatorio();
                console.log(`📄 Relatório exportado: ${arquivo}`);
            }, 3600000); // A cada hora

        } else if (CONFIG.modo === 'semi') {
            console.log('\n👤 Modo SEMI-AUTÔNOMO — Aguardando comandos...\n');
            console.log('Comandos disponíveis:');
            console.log('  - status()              : Ver status dos agentes');
            console.log('  - executar(id)          : Executar agente específico');
            console.log('  - iniciar()             : Iniciar execução contínua');
            console.log('  - parar()               : Parar todos os agentes');
            console.log('  - render(produto,tipos) : Solicitar render 3D');
            console.log('  - renderStatus()        : Ver fila de renders');
            console.log('  - templates()           : Ver templates disponíveis\n');

            // Expor funções globalmente para uso manual
            global.status = () => comandoStatus(manager);
            global.executar = (id) => comandoExecutarAgente(manager, id);
            global.iniciar = () => manager.iniciarTodos();
            global.parar = () => manager.pararTodos();
            global.adicionarProduto = (dados) => comandoAdicionarProduto(manager, dados);

            // Comandos do Blender
            global.render = (produto, tipos) => agentes.agenteBlender.solicitarRender(produto, tipos);
            global.renderCompleto = (produto) => agentes.agenteBlender.solicitarRenderCompleto(produto);
            global.renderStatus = () => {
                const stats = agentes.agenteBlender.getStats();
                console.log('\n🎨 Status do Blender:');
                console.table({
                    'Modo Demo': stats.modoDemo ? 'Sim' : 'Não',
                    'Renders Gerados': stats.totalRendersGerados,
                    'Animações Geradas': stats.totalAnimacoesGeradas,
                    'Jobs Concluídos': stats.totalJobsConcluidos,
                    'Jobs Falhados': stats.totalJobsFalhados,
                    'Fila Atual': stats.filaAtual,
                    'Jobs Ativos': stats.jobsAtivos,
                    'Engine': stats.renderConfig.engine
                });
                return stats;
            };
            global.templates = () => {
                const t = agentes.agenteBlender.getTemplatesDisponiveis();
                console.log('\n🎨 Templates de Cena Disponíveis:');
                for (const [key, desc] of Object.entries(t)) {
                    console.log(`  ${key.padEnd(22)} → ${desc}`);
                }
                return t;
            };

            // Comandos Cinematográficos
            global.cinematic = (produto, opcoes) => agentes.agenteBlender.gerarVideoCinematico(produto, opcoes);
            global.cinematicContent = (obj, opcoes) => agentes.agenteBlender.gerarConteudoCinematico(obj, opcoes);
            global.cinematicBatch = (configs) => agentes.agenteBlender.gerarBatchCinematico(configs);
            global.paletas = () => {
                const p = agentes.agenteBlender.getPaletasDisponiveis();
                console.log('\n🎨 Paletas Cinematográficas:');
                for (const [key, desc] of Object.entries(p)) {
                    console.log(`  ${key.padEnd(18)} → ${desc}`);
                }
                return p;
            };

            console.log('\n--- Comandos Cinematográficos ---');
            console.log('  - cinematic(produto, opcoes)    : Vídeo cinematográfico de produto');
            console.log('  - cinematicContent(obj, opcoes) : Conteúdo abstrato (sphere/cube/torus)');
            console.log('  - cinematicBatch(configs)       : Gerar vários vídeos em batch');
            console.log('  - paletas()                     : Ver paletas de cor disponíveis\n');

        } else {
            console.log('\n👤 Modo MANUAL — Executar comandos individualmente\n');
            // Executar uma vez e sair
            await comandoStatus(manager);
        }

    } catch (erro) {
        console.error('❌ Erro fatal:', erro);
        process.exit(1);
    }
}

// Executar automaticamente
main();

export { inicializarSistema, CONFIG };
