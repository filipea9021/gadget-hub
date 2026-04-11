#!/usr/bin/env node
// =====================================================
// TESTE — Geração de imagem via HuggingFace
// =====================================================
// Uso: node scripts/test-imagegen.js
// Requer: HF_TOKEN no .env
// =====================================================

import { gerarImagem, gerarImagemProduto, gerarVariacoes, MODELOS } from '../src/ai/image-generator.js';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const OUTPUT_DIR = resolve(ROOT, 'product-images', 'test-hf');

console.log('═══════════════════════════════════════════');
console.log('  🎨 Teste — HuggingFace Image Generation  ');
console.log('═══════════════════════════════════════════\n');

console.log('Modelos disponíveis:', Object.keys(MODELOS).join(', '));
console.log(`Output: ${OUTPUT_DIR}\n`);

// --- Teste 1: Imagem simples ---
console.log('▶ Teste 1: Imagem simples com prompt direto');
try {
    const resultado1 = await gerarImagem({
        prompt: 'Professional product photography of wireless bluetooth earbuds on a minimalist white surface, soft studio lighting, matte black finish, e-commerce style, clean background',
        outputPath: resolve(OUTPUT_DIR, 'teste-earbuds.png'),
    });
    console.log(`  ✅ Sucesso! ${(resultado1.tempo / 1000).toFixed(1)}s — ${resultado1.path}\n`);
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}\n`);
}

// --- Teste 2: Imagem de produto (prompt automático) ---
console.log('▶ Teste 2: Imagem de produto (prompt gerado automaticamente)');
try {
    const resultado2 = await gerarImagemProduto({
        produto: 'smartwatch with silver metal band and round AMOLED display',
        estilo: 'hero',
        fundo: 'escuro',
        outputPath: resolve(OUTPUT_DIR, 'teste-smartwatch-hero.png'),
    });
    console.log(`  ✅ Sucesso! ${(resultado2.tempo / 1000).toFixed(1)}s — ${resultado2.path}\n`);
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}\n`);
}

// --- Teste 3: Variações ---
console.log('▶ Teste 3: Gerar 3 variações de um produto');
try {
    const resultados3 = await gerarVariacoes({
        produto: 'portable bluetooth speaker, cylindrical shape, fabric texture, waterproof',
        estilos: ['minimal', 'hero', 'lifestyle'],
        outputDir: resolve(OUTPUT_DIR, 'speaker-variacoes'),
    });
    const ok = resultados3.filter(r => r.sucesso).length;
    console.log(`  ✅ ${ok}/3 variações geradas com sucesso\n`);
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}\n`);
}

console.log('═══════════════════════════════════════════');
console.log('  Teste completo! Verifica as imagens em:');
console.log(`  ${OUTPUT_DIR}`);
console.log('═══════════════════════════════════════════');
