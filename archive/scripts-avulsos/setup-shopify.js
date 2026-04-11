// =====================================================
// SETUP-SHOPIFY.JS — Helper para configurar Shopify
// =====================================================
// Execute: node setup-shopify.js
// Abre o navegador na página correta para criar o app
// =====================================================

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SHOP_DOMAIN = 'gadget-hub.myshopify.com';

console.log('╔════════════════════════════════════════════════════╗');
console.log('║     🛒 CONFIGURAÇÃO SHOPIFY                        ║');
console.log('║     Loja: gadget-hub                               ║');
console.log('╚════════════════════════════════════════════════════╝\n');

console.log('📋 Passos para obter o token:\n');

console.log('1️⃣  Acesse sua loja Shopify:');
console.log(`   https://admin.shopify.com/store/gadget-hub/apps\n`);

console.log('2️⃣  Clique em "Develop apps" (canto superior direito)\n');

console.log('3️⃣  Clique em "Create an app"');
console.log('   Nome: Gadget Hub Automation\n');

console.log('4️⃣  Configure as permissões:');
console.log('   • read_products');
console.log('   • write_products');
console.log('   • read_orders');
console.log('   • write_orders\n');

console.log('5️⃣  Clique em "Install app" e depois copie o:');
console.log('   🔑 Admin API access token\n');

console.log('⚠️  IMPORTANTE: O token só aparece UMA VEZ!\n');

// Tentar abrir o navegador
try {
    const url = `https://admin.shopify.com/store/gadget-hub/apps`;
    
    console.log('🌐 Abrindo navegador...\n');
    
    // Windows
    exec(`start "" "${url}"`);
    
} catch (erro) {
    console.log('ℹ️  Não foi possível abrir o navegador automaticamente');
    console.log(`   Acesse manualmente: https://admin.shopify.com/store/gadget-hub/apps\n`);
}

console.log('✅ Após obter o token, execute:');
console.log('   node update-env-shopify.js <seu-token>\n');
