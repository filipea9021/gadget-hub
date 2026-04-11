// =====================================================
// FIX-SHOPIFY-CONFIG.js — Corrigir configuração Shopify
// =====================================================

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envPath = path.join(__dirname, '.env');

console.log('🔧 Corrigindo configuração Shopify...\n');

// Ler .env atual
let envContent = fs.readFileSync(envPath, 'utf8');

// Atualizar domínio
envContent = envContent.replace(
    /SHOPIFY_SHOP_DOMAIN=.*/,
    'SHOPIFY_SHOP_DOMAIN=gadget-hub-72955.myshopify.com'
);

// Salvar
fs.writeFileSync(envPath, envContent);

console.log('✅ Domínio atualizado para: gadget-hub-72955.myshopify.com');
console.log('\n📋 Agora precisamos do token correto.');
console.log('\nOs códigos que você tem parecem não ser tokens Shopify.');
console.log('Token Shopify começa com: shpat_');
console.log('\nVamos criar um app novo? Execute:');
console.log('   node setup-shopify.js');
