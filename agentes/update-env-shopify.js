// =====================================================
// UPDATE-ENV-SHOPIFY.JS — Atualizar .env com token Shopify
// =====================================================
// Uso: node update-env-shopify.js <token>
// =====================================================

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const token = process.argv[2];

if (!token) {
    console.log('❌ Token não fornecido!');
    console.log('Uso: node update-env-shopify.js <seu-token>');
    console.log('\nExemplo:');
    console.log('  node update-env-shopify.js shpat_abc123xyz...');
    process.exit(1);
}

console.log('🔑 Token recebido:', token.substring(0, 15) + '...\n');

const envPath = path.join(__dirname, '.env');

try {
    // Ler .env atual
    let envContent = '';
    if (fs.existsSync(envPath)) {
        envContent = fs.readFileSync(envPath, 'utf8');
    }
    
    // Verificar se SHOPIFY_ACCESS_TOKEN já existe
    if (envContent.includes('SHOPIFY_ACCESS_TOKEN=')) {
        // Atualizar token existente
        envContent = envContent.replace(
            /SHOPIFY_ACCESS_TOKEN=.*/,
            `SHOPIFY_ACCESS_TOKEN=${token}`
        );
    } else {
        // Adicionar novo token
        envContent += `\n# Shopify (configurado em ${new Date().toISOString()})\n`;
        envContent += `SHOPIFY_ACCESS_TOKEN=${token}\n`;
    }
    
    // Escrever de volta
    fs.writeFileSync(envPath, envContent);
    
    console.log('✅ Token Shopify configurado com sucesso!\n');
    console.log('📋 Próximos passos:');
    console.log('   1. Testar conexão: node test-shopify.js');
    console.log('   2. Executar sistema: node main.js');
    console.log('   3. Ou dashboard: npm run dashboard\n');
    
} catch (erro) {
    console.error('❌ Erro ao atualizar .env:', erro.message);
    process.exit(1);
}
