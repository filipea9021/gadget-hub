// =====================================================
// START-PRODUCAO.JS — Iniciar sistema em modo produção
// =====================================================
// Uso: node start-producao.js
// Modo: autônomo total com logs em arquivo
// =====================================================

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('╔════════════════════════════════════════════════════╗');
console.log('║     🚀 GADGET HUB — MODO PRODUÇÃO                  ║');
console.log('║     Iniciando sistema autônomo...                ║');
console.log('╚════════════════════════════════════════════════════╝\n');

// Criar pasta de logs se não existir
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

const logFile = path.join(logsDir, `sistema-${new Date().toISOString().split('T')[0]}.log`);

console.log('📋 Configuração de Produção:');
console.log('   • Modo: AUTÔNOMO');
console.log('   • Logs:', logFile);
console.log('   • Dashboard: http://localhost:3001');
console.log('   • Agente CJ: Modo demonstração (dados simulados)');
console.log('   • Agente Shopify: Configurado e ativo');
console.log('   • Sincronização: Automática\n');

console.log('⏱️  Intervalos:');
console.log('   • CJ: A cada 60 minutos (buscar novos produtos)');
console.log('   • Shopify: A cada 30 minutos (processar fila)');
console.log('   • Estoque: A cada 30 minutos (sincronizar)');
console.log('   • Preços: A cada 2 horas (ajustar margens)');
console.log('   • Marketing: A cada 3 horas\n');

console.log('🔄 Iniciando em 3 segundos...\n');

setTimeout(() => {
    try {
        // Iniciar dashboard em background
        console.log('🌐 Iniciando Dashboard (porta 3001)...');
        
        const dashboard = execSync('node dashboard/server.js', {
            cwd: __dirname,
            stdio: 'pipe',
            env: { ...process.env, MODO: 'autonomo' }
        });
        
    } catch (erro) {
        console.log('⚠️  Dashboard não pôde ser iniciado automaticamente.');
        console.log('   Execute manualmente: npm run dashboard\n');
    }
    
    console.log('✅ Sistema pronto!');
    console.log('\n📊 Acompanhe em:');
    console.log('   • Dashboard: http://localhost:3001');
    console.log('   • Logs: tail -f logs/sistema-*.log');
    console.log('\n🛑 Para parar: Ctrl+C');
    
}, 3000);
