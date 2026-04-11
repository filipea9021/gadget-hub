// =====================================================
// DEMO.JS — Demonstração do sistema sem API keys
// =====================================================
// Executa agentes CJ e Shopify com dados de demonstração
// =====================================================

import { AgenteCJ } from './cj-dropshipping/agente-cj.js';
import { AgenteShopify } from './shopify/agente-shopify.js';
import { getDatabase } from './core/database.js';

async function demo() {
    console.log('╔════════════════════════════════════════════════════╗');
    console.log('║     🤖 GADGET HUB — Demonstração                   ║');
    console.log('║     Modo: SEM API KEYS (dados simulados)           ║');
    console.log('╚════════════════════════════════════════════════════╝\n');

    // Inicializar database
    const db = await getDatabase();
    console.log('💾 Database inicializado\n');

    // Criar agentes
    const agenteCJ = new AgenteCJ({ intervaloMinutos: 60 });
    const agenteShopify = new AgenteShopify({ intervaloMinutos: 30 });

    // Inicializar
    await agenteCJ.inicializar();
    await agenteShopify.inicializar();

    console.log('═════════════════════════════════════════════════════');
    console.log('📦 PASSO 1: Agente CJ — Pesquisando produtos...');
    console.log('═════════════════════════════════════════════════════\n');

    // Executar CJ uma vez
    const resultadoCJ = await agenteCJ.executar();
    
    if (resultadoCJ.sucesso && resultadoCJ.dados.produtosValidados > 0) {
        const produtos = resultadoCJ.dados._produtosValidados || [];
        
        console.log(`\n✅ ${produtos.length} produtos validados:\n`);
        produtos.forEach((p, i) => {
            console.log(`  ${i + 1}. ${p.nome}`);
            console.log(`     💰 Custo: $${p.precoCusto} → Venda: $${p.precoVenda} (margem: ${p.margem}%)`);
            console.log(`     ⭐ Score: ${p.score} | SKU: ${p.sku}`);
            console.log();
        });

        console.log('═════════════════════════════════════════════════════');
        console.log('🛒 PASSO 2: Agente Shopify — Criando produtos...');
        console.log('═════════════════════════════════════════════════════\n');

        // Adicionar produtos à fila do Shopify
        for (const produto of produtos.slice(0, 2)) {
            await agenteShopify.adicionarProdutoFila({
                nome: produto.nome,
                descricao: produto.descricao,
                precoVenda: produto.precoVenda,
                precoCompare: produto.precoVenda * 1.2,
                categoria: produto.categoria,
                tags: [produto.categoria, 'cj-dropshipping', 'demo'],
                sku: produto.sku,
                imagens: produto.imagens,
                fornecedor: 'CJ Dropshipping'
            });
        }

        // Executar tarefa do Shopify (processa fila)
        console.log('   Processando fila de produtos...\n');
        const resultadoShopify = await agenteShopify.executar();
        
        console.log(`\n✅ Shopify executado:`);
        console.log(`   Sync produtos: ${resultadoShopify.dados.produtosSync}`);
        console.log(`   Ações: ${resultadoShopify.acoes.join(', ') || 'nenhuma'}`);
        console.log(`   Modo: ${resultadoShopify.sucesso ? 'OK' : 'ERRO'}`);
        
        // Mostrar operações pendentes
        const ops = await db.getOperacoesPendentes();
        console.log(`   Operações pendentes: ${ops.length}\n`);

        // Mostrar produtos no banco
        const produtosDB = await db.getProdutos({ status: 'ativo' });
        console.log('📦 Produtos no banco:');
        produtosDB.forEach(p => {
            console.log(`   - ${p.nome} (SKU: ${p.sku})`);
        });

    } else {
        console.log('⚠️ Nenhum produto validado (modo demonstração)');
    }

    console.log('\n═════════════════════════════════════════════════════');
    console.log('📊 Resumo do Sistema:');
    console.log('═════════════════════════════════════════════════════');
    
    const resumo = await db.getResumoSistema();
    console.log(`   Agentes: ${resumo.agentes}`);
    console.log(`   Produtos: ${resumo.produtos.ativos} ativos / ${resumo.produtos.total} total`);
    console.log(`   Operações pendentes: ${resumo.operacoesPendentes}`);
    console.log(`   Logs hoje: ${resumo.logsHoje}`);

    console.log('\n✨ Demonstração completa!');
    console.log('\n📋 Para usar com dados reais:');
    console.log('   1. Configure .env com SHOPIFY_ACCESS_TOKEN');
    console.log('   2. Configure .env com CJ_API_KEY');
    console.log('   3. Execute: node main.js');

    await db.fechar();
}

demo().catch(erro => {
    console.error('❌ Erro:', erro);
    process.exit(1);
});
