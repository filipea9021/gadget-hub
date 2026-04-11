// =====================================================
// MAIN.JS — Ponto de entrada unificado do Gadget Hub
// =====================================================
// Inicializa config, database, todos os agentes e o
// pipeline de comunicação entre eles.
// =====================================================

import repl from 'repl';
import { config, printConfig } from './src/core/config.js';
import { logger, criarLogger } from './src/core/logger.js';
import { ManagerAgentes } from './src/core/manager.js';
import { AgenteShopify } from './src/agentes/agente-shopify.js';
import { AgenteCJ } from './src/agentes/agente-cj.js';
import { AgentePrecos } from './src/agentes/agente-precos.js';
import { AgenteMarketing } from './src/agentes/agente-marketing.js';
import { AgenteEstoque } from './src/agentes/agente-estoque.js';
// AgenteBlender removido — agora vive no Marketing Studio (Fase 3)
// import { AgenteBlender } from './src/agentes/blender/agente-blender.js';
import { AgenteAutomacao } from './src/agentes/agente-automacao.js';
import { AgenteMarketingClient } from './src/agentes/agente-marketing-client.js';
import { MessageBus } from '../shared/core/message-bus.js';
import { AIRouter } from './src/ai/router.js';
import { llmClient } from './src/ai/llm-client.js';
import { injetarSistema, iniciarServidor } from './src/api/server.js';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// =====================================================
// INICIALIZAÇÃO
// =====================================================

async function inicializarSistema() {
    // Boot log
    printConfig();

    const log = criarLogger('main');
    const manager = new ManagerAgentes();

    // Criar agentes com intervalos do config centralizado
    const agentes = {
        shopify:   new AgenteShopify({ intervaloMinutos: config.intervals.shopify }),
        cj:        new AgenteCJ({ intervaloMinutos: config.intervals.cj }),
        precos:    new AgentePrecos({ intervaloMinutos: config.intervals.precos }),
        marketing: new AgenteMarketing({ intervaloMinutos: config.intervals.marketing }),
        estoque:   new AgenteEstoque({ intervaloMinutos: config.intervals.estoque }),
        // blender removido — renders agora via Marketing Studio (studioClient)
        automacao: new AgenteAutomacao({ intervaloMinutos: config.intervals.automacao }),
        studioClient: new AgenteMarketingClient({ intervaloMinutos: 10 }),
    };

    // Message Bus — comunicação com Marketing Studio
    const bus = new MessageBus({
        queueDir: resolve(__dirname, '..', 'marketing-studio', 'queue'),
    });

    // Injetar Message Bus no client
    agentes.studioClient.setMessageBus(bus);

    // Registrar todos no manager
    for (const agente of Object.values(agentes)) {
        manager.registrar(agente);
    }

    // Configurar pipeline de comunicação
    configurarPipeline(agentes);

    // Inicializar todos
    await manager.inicializarTodos();

    log.ok('Sistema inicializado com sucesso');
    return { manager, agentes, bus };
}

// =====================================================
// PIPELINE DE COMUNICAÇÃO ENTRE AGENTES
// =====================================================

function configurarPipeline({ shopify, cj, precos, marketing, estoque, automacao, studioClient }) {

    // CJ → Shopify + Marketing Studio (novos produtos validados)
    cj.onNotificacao((notificacao) => {
        if (notificacao.evento === 'novos_produtos_validados') {
            logger.info(`📦 ${notificacao.dados.produtos.length} produtos validados do CJ`);

            for (const produto of notificacao.dados.produtos.slice(0, 5)) {
                // Adicionar à fila do Shopify
                shopify.adicionarProdutoFila({
                    nome: produto.nome,
                    descricao: produto.descricao,
                    precoVenda: produto.precoVenda,
                    precoCompare: produto.precoVenda * 1.2,
                    categoria: produto.categoria,
                    tags: [produto.categoria, 'cj-dropshipping'],
                    sku: produto.sku,
                    imagens: produto.imagens,
                    fornecedor: 'CJ Dropshipping',
                });

                // Enviar ao Marketing Studio para renders 3D + vídeo
                studioClient.solicitarVideo({
                    id: produto.id || produto.sku,
                    nome: produto.nome,
                    sku: produto.sku,
                    categoria: produto.categoria,
                    shopify_product_id: null,
                }, {
                    renderTypes: ['hero', 'turntable'],
                }).catch(err => {
                    logger.warn(`Marketing Studio: ${err.message}`);
                });
            }
        }
    });

    // Shopify → log de fila
    shopify.onNotificacao((notificacao) => {
        if (notificacao.evento === 'produto_na_fila') {
            logger.info(`📝 Produto "${notificacao.dados.nome}" na fila Shopify`);
        }
        if (notificacao.evento === 'produto_criado') {
            logger.info(`🎨 Produto "${notificacao.dados.nome}" criado — vinculando renders`);
        }
    });

    // [Blender removido — renders agora via studioClient acima]

    // Preços → Shopify (ajuste de preço)
    precos.onNotificacao((notificacao) => {
        if (notificacao.evento === 'ajustar_preco') {
            logger.info(`💰 Preço ajustado: ${notificacao.dados.motivo}`);
            if (config.mode === 'autonomo') {
                shopify.atualizarPreco(notificacao.dados.produtoId, notificacao.dados.novoPreco);
            }
        }
    });

    // Estoque → Marketing (estoque baixo pausa campanhas)
    estoque.onNotificacao((notificacao) => {
        if (notificacao.evento === 'estoque_alerta') {
            logger.warn(`Alerta estoque: ${notificacao.dados.mensagem}`);
            if (notificacao.dados.nivel === 'critico') {
                marketing.pausarCampanhaPorProduto(notificacao.dados.produtoId);
            }
        }
    });

    // Marketing Studio Client → Shopify + Marketing (renders do Studio prontos)
    studioClient.onNotificacao((notificacao) => {
        if (notificacao.evento === 'renders_prontos') {
            const { produtoId, shopifyProductId, renders, animacoes } = notificacao.dados;
            logger.info(`🎬 Studio: renders prontos — ${renders.length} imgs + ${animacoes.length} vídeos (via ${notificacao.dados.via})`);

            if (config.mode === 'autonomo' && shopifyProductId) {
                logger.info(`📤 Enviando renders do Studio para Shopify — ${shopifyProductId}`);
            }

            marketing.emit('notificacao_recebida', {
                origem: 'marketing-studio',
                evento: 'renders_disponiveis',
                dados: {
                    produtoId,
                    renders: renders.map(r => r.url),
                    animacoes: animacoes.map(a => a.url),
                },
                timestamp: new Date().toISOString(),
            });
        }
    });

    // Marketing → log
    marketing.onNotificacao((notificacao) => {
        if (notificacao.evento === 'campanha_criada') {
            logger.info(`📢 Nova campanha: ${notificacao.dados.produto}`);
        }
    });

    // Shopify → Automação (webhooks de pedidos)
    shopify.onNotificacao((notificacao) => {
        if (notificacao.evento === 'pedido_criado') {
            automacao.processarWebhook('order.created', notificacao.dados);
        }
        if (notificacao.evento === 'pedido_enviado') {
            automacao.processarWebhook('order.shipped', notificacao.dados);
        }
    });
}

// =====================================================
// COMANDOS MANUAIS (REPL)
// =====================================================

function registrarComandos(manager, agentes, aiRouter) {
    global.status = () => {
        const s = manager.getStatusCompleto();
        console.log('\n📊 Status do Sistema:');
        console.table(s.agentes.map(a => ({
            Agente: a.nome,
            Status: a.status,
            'Última Execução': a.ultimaExecucao ? new Date(a.ultimaExecucao).toLocaleTimeString() : 'Nunca',
            'Próxima Execução': a.proximaExecucao ? new Date(a.proximaExecucao).toLocaleTimeString() : 'Aguardando',
        })));
        return s;
    };

    global.executar = (id) => {
        console.log(`\n▶️ Executando agente: ${id}`);
        return manager.executarAgente(id);
    };

    global.iniciar = () => manager.iniciarTodos();
    global.parar = () => manager.pararTodos();

    // Renders (via Marketing Studio)
    global.render = (produto, tipos) => agentes.studioClient.solicitarVideo(produto, { renderTypes: tipos || ['hero'] });
    global.renderCompleto = (produto) => agentes.studioClient.solicitarRenderCompleto(produto);
    global.renderStatus = () => global.studioStatus();

    // Cinematográficos (via Marketing Studio)
    global.cinematic = (produto, opcoes) => agentes.studioClient.solicitarCinematico(produto, opcoes);
    global.cinematicBatch = async (produtos) => {
        const resultados = [];
        for (const p of (produtos || [])) {
            resultados.push(await agentes.studioClient.solicitarCinematico(p));
        }
        console.log(`\n🎬 ${resultados.length} pedidos cinematográficos enviados ao Studio`);
        return resultados;
    };

    // Automação
    global.faq = (texto) => {
        const r = agentes.automacao.responderPergunta(texto);
        console.log(`\n💬 ${r.encontrada ? '✅' : '❌'} ${r.resposta}`);
        return r;
    };
    global.hashtags = (categoria) => {
        const tags = agentes.automacao.getHashtags(categoria);
        console.log(`\n#️⃣ Hashtags para "${categoria}": ${tags.join(' ')}`);
        return tags;
    };
    global.webhook = (evento, dados) => agentes.automacao.processarWebhook(evento, dados);
    global.autoStats = () => {
        const s = agentes.automacao.getStats();
        console.log('\n🤖 Stats Automação:');
        console.table(s);
        return s;
    };

    // Marketing Studio
    global.studioStatus = async () => {
        const health = await agentes.studioClient.getStudioHealth();
        const stats = agentes.studioClient.getStats();
        console.log('\n🎬 Marketing Studio:');
        console.log(`  Online:    ${health.ok ? '✅ Sim' : '❌ Não'}`);
        console.log(`  URL:       ${stats.studioUrl}`);
        console.log(`  Enviados:  ${stats.totalPedidosEnviados}`);
        console.log(`  Respostas: ${stats.totalRespostasRecebidas}`);
        console.log(`  Falhados:  ${stats.totalFalhados}`);
        console.log(`  Pendentes: ${stats.pedidosPendentes}`);
        console.log(`  Em espera: ${stats.pedidosEmEspera}`);
        return { health, stats };
    };
    global.studioVideo = (produto, opcoes) => agentes.studioClient.solicitarVideo(produto, opcoes);
    global.studioCinematic = (produto, opcoes) => agentes.studioClient.solicitarCinematico(produto, opcoes);
    global.studioStats = async () => {
        const remote = await agentes.studioClient.getStudioStats();
        if (remote) {
            console.log('\n🎬 Marketing Studio Stats (remoto):');
            console.table(remote);
        } else {
            console.log('\n⚠️  Marketing Studio offline — sem stats remotos');
        }
        return remote;
    };

    // AI Router
    global.ai = (texto) => aiRouter.processar(texto);
    global.aiStats = () => {
        const s = llmClient.getStats();
        console.log('\n🧠 Stats AI:');
        console.table(s);
        return s;
    };
}

// =====================================================
// EXECUÇÃO
// =====================================================

async function main() {
    try {
        const { manager, agentes, bus } = await inicializarSistema();

        // Criar AI Router
        const aiRouter = new AIRouter(manager, agentes);

        // Injetar sistema no servidor API e iniciar
        injetarSistema(manager, agentes, aiRouter);
        iniciarServidor();

        if (config.mode === 'autonomo') {
            logger.info('🤖 Modo AUTÔNOMO — execução contínua');
            manager.iniciarTodos();

            setInterval(async () => {
                const arquivo = await manager.exportarRelatorio();
                logger.info(`📄 Relatório exportado: ${arquivo}`);
            }, 3600000);

        } else if (config.mode === 'semi') {
            logger.info('👤 Modo SEMI-AUTÔNOMO — aguardando comandos\n');
            registrarComandos(manager, agentes, aiRouter);

            console.log('Comandos disponíveis:');
            console.log('  status()              — Ver status dos agentes');
            console.log('  executar(id)          — Executar agente específico');
            console.log('  iniciar()             — Iniciar execução contínua');
            console.log('  parar()               — Parar todos os agentes');
            console.log('  ─── Renders (via Marketing Studio) ───');
            console.log('  render(produto,tipos) — Solicitar render ao Studio');
            console.log('  renderCompleto(prod)  — Render completo (hero+multi+turntable+exploded)');
            console.log('  renderStatus()        — Ver status do Studio');
            console.log('  cinematic(prod,opts)  — Vídeo cinematográfico via Studio');
            console.log('  cinematicBatch(prods) — Batch de vídeos cinematográficos');
            console.log('  studioStatus()        — Status completo do Marketing Studio');
            console.log('  studioVideo(prod,opt) — Enviar pedido de vídeo');
            console.log('  studioStats()         — Stats remotos do Studio');
            console.log('  ─── Automação ───');
            console.log('  faq(texto)            — Testar chatbot FAQ');
            console.log('  hashtags(categoria)   — Ver hashtags por categoria');
            console.log('  webhook(evento,dados) — Simular webhook');
            console.log('  autoStats()           — Stats da automação');
            console.log('  ai(texto)             — Comando em linguagem natural');
            console.log('  aiStats()             — Stats do módulo AI\n');

            // Iniciar REPL interativo
            const r = repl.start({ prompt: 'gadget-hub> ', useGlobal: true });
            r.on('exit', () => { process.exit(0); });

        } else {
            logger.info('👤 Modo MANUAL — execução única');
            global.status && global.status();
        }
    } catch (erro) {
        logger.error('Erro fatal', erro);
        process.exit(1);
    }
}

main();

export { inicializarSistema, config };
