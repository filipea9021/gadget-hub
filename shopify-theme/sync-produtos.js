#!/usr/bin/env node
/**
 * ============================================================
 * Gadget Hub — Sincronizador de Produtos → Shopify
 * ============================================================
 * Lê o catálogo local e cria/atualiza produtos na Shopify
 * com todos os metafields (score, margem, fornecedor, etc.)
 *
 * Uso:
 *   node sync-produtos.js              → Apenas mostra o que faria
 *   node sync-produtos.js --executar   → Executa a sincronização real
 *   node sync-produtos.js --id=4       → Sync de produto específico
 * ============================================================
 */

import 'dotenv/config';

// ===== CATÁLOGO DE PRODUTOS =====
const CATALOGO = [
    { id:1,  sku:'GH-001', name:'Smart Plug WiFi 16A',        description:'Controla dispositivos pelo smartphone, compatível com Alexa, Google Home e Apple HomeKit. Programação por horários e temporizadores. Monitorização do consumo de energia em tempo real. Fácil instalação sem ferramentas.',                              price:29.90, supplierPrice:8.00,  category:'smart-home',  emoji:'🔌', rating:4.6, orders:8200, deliveryDays:8,  supplier:'CJ Dropshipping', cjId:'CJ-SP-001' },
    { id:2,  sku:'GH-002', name:'Lâmpada RGB Smart E27',       description:'16 milhões de cores via app ou controlo por voz. 12W equivalente a 100W incandescente. Compatível com Alexa, Google Home e Apple HomeKit. Cria cenas e automatizações por horário.',                                                                       price:24.90, supplierPrice:6.50,  category:'smart-home',  emoji:'💡', rating:4.5, orders:3500, deliveryDays:9,  supplier:'CJ Dropshipping', cjId:'CJ-LB-001' },
    { id:3,  sku:'GH-003', name:'Câmera WiFi 1080p',           description:'Vigilância 360° com motor pan/tilt. Visão noturna a 10 metros. Deteção de movimento com alertas por app. Armazenamento local (cartão SD) ou cloud. Áudio bidirecional.',                                                                                     price:49.90, supplierPrice:14.00, category:'smart-home',  emoji:'📷', rating:4.4, orders:3300, deliveryDays:10, supplier:'CJ Dropshipping', cjId:'CJ-CM-001' },
    { id:4,  sku:'GH-004', name:'Fone TWS Bluetooth 5.3',      description:'Cancelamento ativo de ruído (ANC) de 40dB. Até 30h de bateria com case. Resistência à água IPX5. Modo de transparência para ouvir o ambiente. Driver de 10mm para graves potentes.',                                                                          price:69.90, supplierPrice:18.00, category:'audio',       emoji:'🎧', rating:4.7, orders:9100, deliveryDays:7,  supplier:'CJ Dropshipping', cjId:'CJ-AU-001' },
    { id:5,  sku:'GH-005', name:'Coluna Bluetooth Portátil',   description:'Som omnidirecional 360° com 20W de potência. Resistência à água IPX7, ideal para exterior. Autonomia de 12 horas. Emparelhamento duplo (2 dispositivos simultâneos). Microfone integrado para chamadas.',                                                    price:59.90, supplierPrice:16.00, category:'audio',       emoji:'🔊', rating:4.5, orders:5700, deliveryDays:9,  supplier:'CJ Dropshipping', cjId:'CJ-AU-002' },
    { id:6,  sku:'GH-006', name:'Hub USB-C 7 em 1',            description:'HDMI 4K@60Hz, 2x USB 3.0, leitor SD/TF, carregamento PD 100W passthrough. Corpo em alumínio para dissipação de calor. Plug and play, sem drivers. Compatível com Mac, Windows, iPad Pro.',                                                                   price:39.90, supplierPrice:11.00, category:'acessorios',  emoji:'🔗', rating:4.5, orders:2900, deliveryDays:8,  supplier:'CJ Dropshipping', cjId:'CJ-AC-001' },
    { id:7,  sku:'GH-007', name:'Carregador Wireless 15W',     description:'Carregamento rápido Qi 15W para Android e 15W MagSafe para iPhone. LED indicador de estado de carga. Base antiderrapante em silicone. Compatível com todos os dispositivos Qi. Cabo USB-C incluído.',                                                        price:34.90, supplierPrice:9.00,  category:'acessorios',  emoji:'⚡', rating:4.6, orders:7300, deliveryDays:7,  supplier:'CJ Dropshipping', cjId:'CJ-AC-002' },
    { id:8,  sku:'GH-008', name:'Power Bank 20000mAh',         description:'Carga rápida 22.5W para smartphone. 3 portas de saída (USB-A x2, USB-C). Display LCD com percentagem de carga. Espessura ultra-slim de 1.5cm. Carga simultânea de 3 dispositivos.',                                                                          price:49.90, supplierPrice:14.00, category:'acessorios',  emoji:'🔋', rating:4.4, orders:3100, deliveryDays:10, supplier:'CJ Dropshipping', cjId:'CJ-AC-003' },
    { id:9,  sku:'GH-009', name:'Aspirador Robô Smart',        description:'Mapeamento LiDAR para percursos inteligentes. App WiFi com mapas interativos e zonas proibidas. Compatível com Alexa e Google Home. Autonomia de 120 minutos. Sucção de 2700Pa.',                                                                              price:189.90,supplierPrice:55.00, category:'smart-home',  emoji:'🤖', rating:4.3, orders:1800, deliveryDays:12, supplier:'CJ Dropshipping', cjId:'CJ-SM-001' },
    { id:10, sku:'GH-010', name:'Rato Sem Fio Silencioso',     description:'Cliques silenciosos a 99% sem ruído. Recetor 2.4GHz nano com alcance de 10m. 1600 DPI ajustável em 3 níveis. Bateria AAA com até 12 meses de autonomia. Ergonómico para uso prolongado.',                                                                    price:29.90, supplierPrice:7.50,  category:'acessorios',  emoji:'🖱️', rating:4.4, orders:4200, deliveryDays:9,  supplier:'CJ Dropshipping', cjId:'CJ-AC-004' },
    { id:11, sku:'GH-011', name:'Teclado Bluetooth Ultra-slim',description:'Multidispositivo: troca entre 3 gadgets com um toque. Compatível com Windows, Mac, iOS e Android. Recarga USB-C com autonomia de 3 meses. Design flat elegante com 1cm de espessura.',                                                                        price:44.90, supplierPrice:12.00, category:'acessorios',  emoji:'⌨️', rating:4.3, orders:3100, deliveryDays:11, supplier:'CJ Dropshipping', cjId:'CJ-AC-005' },
    { id:12, sku:'GH-012', name:'Monitor Portátil 15.6" FHD',  description:'Resolução Full HD 1920x1080, 60Hz. Ligação via USB-C (único cabo para imagem e energia). Ângulo de visão de 178°. Peso de apenas 800g com capa de proteção. Ideal para home office e trabalho remoto.',                                                       price:149.90,supplierPrice:48.00, category:'eletronicos', emoji:'🖥️', rating:4.6, orders:2200, deliveryDays:12, supplier:'CJ Dropshipping', cjId:'CJ-EL-001' },
];

// ===== MAPAS DE CATEGORIAS → SHOPIFY =====
const CATEGORY_MAP = {
    'smart-home': 'Casa Inteligente',
    'audio':      'Áudio',
    'acessorios': 'Acessórios Tech',
    'eletronicos':'Eletrônicos',
    'gaming':     'Gaming',
};

// ===== CÁLCULO DE SCORE =====
function calcularScore(p) {
    const margem = ((p.price - p.supplierPrice) / p.price) * 100;
    const sA = (p.rating / 5) * 30;
    const sM = Math.min((margem / 80) * 30, 30);
    const sE = p.deliveryDays === 0 ? 20 : Math.max(((15 - p.deliveryDays) / 15) * 20, 0);
    const sP = Math.min((p.orders / 5000) * 20, 20);
    return Math.round(sA + sM + sE + sP);
}

// Enriquecer catálogo
CATALOGO.forEach(p => {
    p.score  = calcularScore(p);
    p.margin = Math.round(((p.price - p.supplierPrice) / p.price) * 100);
    p.compareAtPrice = Math.round(p.price * 1.3 * 100) / 100; // Preço "riscado" +30%
});

// ===== SHOPIFY API HELPER =====
const SHOP   = process.env.SHOPIFY_SHOP_DOMAIN;
const TOKEN  = process.env.SHOPIFY_ACCESS_TOKEN;
const VER    = process.env.SHOPIFY_API_VERSION || '2024-01';

async function shopifyGraphQL(query, variables = {}) {
    if (!SHOP || !TOKEN) {
        throw new Error('Configure SHOPIFY_SHOP_DOMAIN e SHOPIFY_ACCESS_TOKEN no .env');
    }

    const url = `https://${SHOP}/admin/api/${VER}/graphql.json`;
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'X-Shopify-Access-Token': TOKEN,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, variables }),
    });

    const json = await res.json();
    if (json.errors) throw new Error(json.errors.map(e => e.message).join('\n'));
    return json.data;
}

// ===== CRIAR PRODUTO NA SHOPIFY =====
async function criarProduto(p) {
    const mutation = `
        mutation productCreate($input: ProductInput!) {
            productCreate(input: $input) {
                product { id title handle }
                userErrors { field message }
            }
        }
    `;

    const data = await shopifyGraphQL(mutation, {
        input: {
            title: p.name,
            descriptionHtml: `<p>${p.description}</p>`,
            vendor: 'Gadget Hub',
            productType: CATEGORY_MAP[p.category] || 'Eletrônicos',
            tags: [p.category, 'cj-dropshipping', `score-${p.score}`, `delivery-${p.deliveryDays}d`],
            status: 'ACTIVE',
            variants: [{
                price: p.price.toFixed(2),
                compareAtPrice: p.compareAtPrice.toFixed(2),
                sku: p.sku,
                inventoryManagement: 'SHOPIFY',
                inventoryPolicy: 'DENY',
                requiresShipping: true,
                taxable: true,
            }],
        }
    });

    const erros = data.productCreate?.userErrors;
    if (erros?.length > 0) throw new Error(erros.map(e => e.message).join(', '));

    const produto = data.productCreate?.product;

    // Definir metafields
    await definirMetafields(produto.id, p);

    return produto;
}

// ===== DEFINIR METAFIELDS =====
async function definirMetafields(productId, p) {
    const mutation = `
        mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
            metafieldsSet(metafields: $metafields) {
                metafields { key value }
                userErrors { field message }
            }
        }
    `;

    const metafields = [
        { ownerId: productId, namespace: 'gadgethub', key: 'score',          type: 'number_integer',          value: String(p.score) },
        { ownerId: productId, namespace: 'gadgethub', key: 'rating',         type: 'number_decimal',          value: String(p.rating) },
        { ownerId: productId, namespace: 'gadgethub', key: 'orders',         type: 'number_integer',          value: String(p.orders) },
        { ownerId: productId, namespace: 'gadgethub', key: 'delivery_days',  type: 'number_integer',          value: String(p.deliveryDays) },
        { ownerId: productId, namespace: 'gadgethub', key: 'supplier',       type: 'single_line_text_field',  value: p.supplier },
        { ownerId: productId, namespace: 'gadgethub', key: 'supplier_price', type: 'number_decimal',          value: String(p.supplierPrice) },
        { ownerId: productId, namespace: 'gadgethub', key: 'margin',         type: 'number_decimal',          value: String(p.margin) },
        { ownerId: productId, namespace: 'gadgethub', key: 'cj_product_id',  type: 'single_line_text_field',  value: p.cjId },
    ];

    return shopifyGraphQL(mutation, { metafields });
}

// ===== MODO PREVIEW (sem executar) =====
function mostrarPreview() {
    console.log('\n╔══════════════════════════════════════════════════╗');
    console.log('║     GADGET HUB — Preview de Sincronização        ║');
    console.log('╚══════════════════════════════════════════════════╝\n');
    console.log(`📦 ${CATALOGO.length} produtos prontos para sync:\n`);

    CATALOGO.forEach(p => {
        const margem = `${p.margin}%`;
        const score  = `${p.score}/100`;
        console.log(`  ${p.emoji}  [${p.sku}] ${p.name}`);
        console.log(`       R$ ${p.price.toFixed(2).padEnd(8)} | Margem: ${margem.padEnd(6)} | Score: ${score} | ${p.deliveryDays}d`);
    });

    console.log('\n💡 Para executar a sincronização real:');
    console.log('   1. Configure o .env com SHOPIFY_SHOP_DOMAIN e SHOPIFY_ACCESS_TOKEN');
    console.log('   2. Execute: node sync-produtos.js --executar\n');
}

// ===== MAIN =====
async function main() {
    const args = process.argv.slice(2);
    const executar = args.includes('--executar');
    const idFiltro = args.find(a => a.startsWith('--id='))?.split('=')[1];

    if (!executar) {
        mostrarPreview();
        return;
    }

    let catalogo = CATALOGO;
    if (idFiltro) catalogo = CATALOGO.filter(p => p.id === parseInt(idFiltro));

    console.log(`\n🚀 Iniciando sync de ${catalogo.length} produto(s)...\n`);

    let ok = 0, falha = 0;
    for (const p of catalogo) {
        try {
            const resultado = await criarProduto(p);
            console.log(`  ✅ ${p.emoji} ${p.name} → ${resultado.handle}`);
            ok++;
        } catch (err) {
            console.error(`  ❌ ${p.name}: ${err.message}`);
            falha++;
        }
        // Rate limit: 2 req/s
        await new Promise(r => setTimeout(r, 500));
    }

    console.log(`\n📊 Resultado: ${ok} criados, ${falha} erros\n`);
}

main().catch(console.error);
