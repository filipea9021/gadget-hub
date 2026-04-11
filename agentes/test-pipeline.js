// =====================================================
// TEST-PIPELINE.JS — Testar pipeline de importação
// =====================================================
// Execute: node test-pipeline.js
// =====================================================

import { PipelineImportacao } from './pipeline-importacao.js';

async function testarPipeline() {
    console.log('╔════════════════════════════════════════════════════╗');
    console.log('║     🔄 TESTE PIPELINE IMPORTAÇÃO                   ║');
    console.log('║     CJ → Shopify                                   ║');
    console.log('╚════════════════════════════════════════════════════╝\n');

    const pipeline = new PipelineImportacao();

    try {
        // Inicializar
        console.log('1️⃣  Inicializando pipeline...');
        await pipeline.inicializar();
        console.log('   ✅ Pipeline pronto\n');

        // Mostrar configuração
        console.log('⚙️  Configuração atual:');
        console.log(`   • Margem mínima: ${pipeline.getConfig().margemMinima}%`);
        console.log(`   • Avaliação mínima: ${pipeline.getConfig().avaliacaoMinima}`);
        console.log(`   • Pedidos mínimos: ${pipeline.getConfig().pedidosMinimos}`);
        console.log(`   • Limite por execução: ${pipeline.getConfig().limiteProdutosPorExecucao}\n`);

        // Executar importação completa
        console.log('🚀 Executando importação...\n');
        const resultado = await pipeline.executarImportacaoCompleta();

        // Resumo
        console.log('\n═════════════════════════════════════════════════════');
        console.log('📊 RESUMO DA IMPORTAÇÃO');
        console.log('═════════════════════════════════════════════════════');
        console.log(`Início: ${resultado.inicio}`);
        console.log(`Fim: ${resultado.fim}`);
        console.log(`Sucesso: ${resultado.sucesso ? '✅ SIM' : '❌ NÃO'}`);
        console.log('\nEtapas:');
        Object.entries(resultado.etapas).forEach(([etapa, info]) => {
            const status = info.sucesso ? '✅' : '⚠️';
            const detalhe = info.quantidade !== undefined ? `(${info.quantidade})` : '';
            console.log(`   ${status} ${etapa}: ${detalhe}`);
        });

        if (resultado.produtosImportados.length > 0) {
            console.log('\n📦 Produtos importados:');
            resultado.produtosImportados.forEach((p, i) => {
                console.log(`   ${i + 1}. ${p.nome}`);
                console.log(`      SKU: ${p.sku}`);
                console.log(`      Preço: $${p.precoCusto} → $${p.precoVenda} (margem: ${p.margem}%)`);
                if (p.shopifyProductId) {
                    console.log(`      Shopify ID: ${p.shopifyProductId}`);
                }
            });
        }

        if (resultado.erros.length > 0) {
            console.log('\n❌ Erros:');
            resultado.erros.forEach(erro => console.log(`   • ${erro}`));
        }

        console.log('\n✅ Teste concluído!');

    } catch (erro) {
        console.error('\n❌ Erro no teste:', erro.message);
        console.error(erro.stack);
    }
}

// Executar
testarPipeline();
