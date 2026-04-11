// =====================================================
// TEST-SHOPIFY.JS — Testar conexão com Shopify API
// =====================================================
// Execute: node test-shopify.js
// =====================================================

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ler .env manualmente
function loadEnv() {
    try {
        const envPath = path.join(__dirname, '.env');
        const envContent = fs.readFileSync(envPath, 'utf8');
        const lines = envContent.split('\n');
        
        for (const line of lines) {
            if (line.includes('=') && !line.startsWith('#')) {
                const [key, ...valueParts] = line.split('=');
                const value = valueParts.join('=').trim();
                if (key && value) {
                    process.env[key.trim()] = value;
                }
            }
        }
    } catch (erro) {
        console.log('⚠️  Não foi possível ler .env:', erro.message);
    }
}

loadEnv();

const SHOPIFY_CONFIG = {
    shopDomain: process.env.SHOPIFY_SHOP_DOMAIN || 'gadget-hub-72955.myshopify.com',
    accessToken: process.env.SHOPIFY_ACCESS_TOKEN,
    apiVersion: '2024-01'
};

console.log('╔════════════════════════════════════════════════════╗');
console.log('║     🛒 TESTE SHOPIFY API                           ║');
console.log('╚════════════════════════════════════════════════════╝\n');

console.log('Configuração:');
console.log(`  Loja: ${SHOPIFY_CONFIG.shopDomain}`);
console.log(`  Token: ${SHOPIFY_CONFIG.accessToken ? '✓ Configurado' : '✗ NÃO CONFIGURADO'}`);
if (SHOPIFY_CONFIG.accessToken) {
    console.log(`  Comprimento: ${SHOPIFY_CONFIG.accessToken.length} caracteres`);
    console.log(`  Início: ${SHOPIFY_CONFIG.accessToken.substring(0, 20)}...`);
}
console.log();

async function testarGraphQL() {
    try {
        console.log('1️⃣  Testando GraphQL API...');
        
        const url = `https://${SHOPIFY_CONFIG.shopDomain}/admin/api/${SHOPIFY_CONFIG.apiVersion}/graphql.json`;
        
        const query = `
            query {
                shop {
                    name
                    email
                    primaryDomain {
                        url
                    }
                }
            }
        `;
        
        const resposta = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': SHOPIFY_CONFIG.accessToken
            },
            body: JSON.stringify({ query })
        });
        
        const dados = await resposta.json();
        
        if (dados.errors) {
            console.log(`   ❌ Erro GraphQL: ${dados.errors[0].message}`);
            return false;
        }
        
        if (dados.data && dados.data.shop) {
            console.log('   ✅ Conexão bem-sucedida!');
            console.log(`   🏪 Loja: ${dados.data.shop.name}`);
            console.log(`   📧 Email: ${dados.data.shop.email}`);
            console.log(`   🌐 URL: ${dados.data.shop.primaryDomain.url}`);
            return true;
        }
        
        console.log('   ⚠️  Resposta inesperada:', dados);
        return false;
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
        return false;
    }
}

async function testarProdutos() {
    try {
        console.log('\n2️⃣  Testando listagem de produtos...');
        
        const url = `https://${SHOPIFY_CONFIG.shopDomain}/admin/api/${SHOPIFY_CONFIG.apiVersion}/graphql.json`;
        
        const query = `
            query {
                products(first: 5) {
                    edges {
                        node {
                            id
                            title
                            handle
                            status
                            variants(first: 1) {
                                edges {
                                    node {
                                        id
                                        sku
                                        price
                                    }
                                }
                            }
                        }
                    }
                }
            }
        `;
        
        const resposta = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': SHOPIFY_CONFIG.accessToken
            },
            body: JSON.stringify({ query })
        });
        
        const dados = await resposta.json();
        
        if (dados.errors) {
            console.log(`   ❌ Erro: ${dados.errors[0].message}`);
            return;
        }
        
        const produtos = dados.data?.products?.edges || [];
        
        console.log(`   ✅ ${produtos.length} produtos encontrados`);
        
        if (produtos.length > 0) {
            console.log('\n   📦 Produtos:');
            produtos.forEach((p, i) => {
                const node = p.node;
                const variant = node.variants.edges[0]?.node;
                console.log(`      ${i + 1}. ${node.title}`);
                console.log(`         Status: ${node.status}`);
                console.log(`         SKU: ${variant?.sku || 'N/A'}`);
                console.log(`         Preço: $${variant?.price || 'N/A'}`);
            });
        }
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
    }
}

async function main() {
    if (!SHOPIFY_CONFIG.accessToken) {
        console.log('❌ SHOPIFY_ACCESS_TOKEN não configurado!\n');
        console.log('📋 Para configurar:');
        console.log('   1. Execute: node setup-shopify.js');
        console.log('   2. Siga as instruções para criar o app');
        console.log('   3. Obtenha o token e execute:');
        console.log('      node update-env-shopify.js <seu-token>');
        process.exit(1);
    }
    
    const conectado = await testarGraphQL();
    
    if (conectado) {
        await testarProdutos();
        
        console.log('\n✅ Todos os testes concluídos!');
        console.log('\n🚀 Próximo passo: Execute o sistema:');
        console.log('   node main.js        (modo CLI)');
        console.log('   npm run dashboard   (modo web)');
    } else {
        console.log('\n❌ Falha na conexão. Verifique seu token.');
        console.log('\n🔧 Soluções:');
        console.log('   • Certifique-se de que o token está correto');
        console.log('   • Verifique se o app está instalado na loja');
        console.log('   • Confirme as permissões (read_products, write_products)');
    }
}

main().catch(erro => {
    console.error('Erro fatal:', erro);
    process.exit(1);
});
