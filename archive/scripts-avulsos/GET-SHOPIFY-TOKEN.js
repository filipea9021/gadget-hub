// =====================================================
// GET-SHOPIFY-TOKEN.js — Guia interativo para obter token
// =====================================================

import { exec } from 'child_process';

console.log('╔════════════════════════════════════════════════════╗');
console.log('║     🔑 COMO OBTER SHOPIFY ACCESS TOKEN             ║');
console.log('╚════════════════════════════════════════════════════╝\n');

console.log('📋 PASSO A PASSO:\n');

console.log('1️⃣  Acesse sua loja Shopify:');
console.log('   👉 https://admin.shopify.com/store/gadget-hub/apps\n');

console.log('2️⃣  No canto SUPERIOR DIREITO, clique em:');
console.log('   "Develop apps"\n');

console.log('3️⃣  Clique no botão LARANJA:');
console.log('   "Create an app"\n');

console.log('4️⃣  Preencha:');
console.log('   Nome do app: Gadget Hub Automation');
console.log('   Clique: "Create"\n');

console.log('5️⃣  Clique em:"Configure Admin API scopes"\n');

console.log('6️⃣  Marque as permissões:');
console.log('   ☑️ read_products');
console.log('   ☑️ write_products');
console.log('   ☑️ read_orders');
console.log('   ☑️ write_orders');
console.log('   Clique: "Save"\n');

console.log('7️⃣  Clique na aba "API credentials"\n');

console.log('8️⃣  Clique no botão VERDE:');
console.log('   "Install app"\n');

console.log('9️⃣  Confirme clicando "Install" na popup\n');

console.log('🔟  IMPORTANTE - Token só aparece UMA VEZ:');
console.log('   Clique em "Reveal token once"');
console.log('   Copie o token (começa com shpat_...)\n');

console.log('═════════════════════════════════════════════════════\n');

console.log('✅ DEPOIS DE COPIAR O TOKEN:');
console.log('   Cole aqui no chat que eu configuro!\n');

console.log('⚠️  SE PERDER O TOKEN:');
console.log('   1. Vá em "API credentials"');
console.log('   2. Clique "Uninstall app"');
console.log('   3. Reinstale o app');
console.log('   4. Novo token será gerado\n');

// Abrir navegador
try {
    console.log('🌐 Abrindo Shopify Admin...\n');
    exec('start "" "https://admin.shopify.com/store/gadget-hub/apps"');
} catch (e) {
    console.log('ℹ️  Acesse manualmente:');
    console.log('   https://admin.shopify.com/store/gadget-hub/apps\n');
}

console.log('💡 DICA: O token tem formato:');
console.log('   shpat_abc123def456ghi789... (muito longo)\n');

console.log('⏳ Aguardando seu token...');
