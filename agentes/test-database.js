// =====================================================
// TEST-DATABASE.JS — Script de validação do sistema
// =====================================================
// Execute: node test-database.js
// Verifica se SQLite e estrutura estão funcionando
// =====================================================

import { getDatabase } from './core/database.js';

async function testarSistema() {
    console.log('🧪 Testando Sistema de Agentes\n');
    
    try {
        // 1. Testar conexão com database
        console.log('1️⃣  Conectando ao SQLite...');
        const db = await getDatabase();
        console.log('   ✅ Database conectado');
        
        // 2. Testar resumo do sistema
        console.log('\n2️⃣  Verificando tabelas...');
        const resumo = await db.getResumoSistema();
        console.log('   📊 Resumo:', JSON.stringify(resumo, null, 2));
        
        // 3. Testar inserção de produto
        console.log('\n3️⃣  Testando inserção de produto...');
        const produtoTeste = {
            id: 'TEST-001',
            nome: 'Produto de Teste',
            sku: 'TEST-SKU-001',
            categoria: 'teste',
            precoCusto: 10.00,
            precoVenda: 29.90,
            margem: 66.6,
            score: 85,
            avaliacao: 4.5,
            fornecedor: 'Teste'
        };
        await db.salvarProduto(produtoTeste);
        console.log('   ✅ Produto salvo');
        
        // 4. Testar recuperação
        const produtos = await db.getProdutos({ status: 'ativo' });
        console.log(`   📦 ${produtos.length} produtos no banco`);
        
        // 5. Testar fila de operações
        console.log('\n4️⃣  Testando fila de operações...');
        const opId = await db.adicionarOperacao('criar_produto', produtoTeste);
        console.log(`   ✅ Operação #${opId} adicionada à fila`);
        
        const pendentes = await db.getOperacoesPendentes();
        console.log(`   📋 ${pendentes.length} operações pendentes`);
        
        // 6. Testar logs
        console.log('\n5️⃣  Testando logs...');
        await db.adicionarLog('teste', 'info', 'Teste de log estruturado', { teste: true });
        const logs = await db.getLogs('teste', 5);
        console.log(`   📝 ${logs.length} logs recentes`);
        
        console.log('\n✨ Todos os testes passaram!');
        console.log('\n📋 Próximos passos:');
        console.log('   1. Configure .env com suas credenciais');
        console.log('   2. Execute: node main.js');
        console.log('   3. Use status() para ver agentes');
        
    } catch (erro) {
        console.error('\n❌ Erro nos testes:', erro.message);
        console.error(erro.stack);
        process.exit(1);
    } finally {
        const db = await getDatabase();
        await db.fechar();
    }
}

testarSistema();
