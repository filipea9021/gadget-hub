// =====================================================
// IMAGE GENERATOR — Geração de imagens via HuggingFace
// =====================================================
// Usa a Inference API do HuggingFace para gerar imagens
// de produto para e-commerce via FLUX.1 e outros modelos.
// =====================================================

import fetch from 'node-fetch';
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { resolve, dirname } from 'path';
import config from '../core/config.js';
import { logger } from '../core/logger.js';

// Modelos disponíveis (do mais rápido ao mais lento)
const MODELOS = {
    'flux-schnell': 'black-forest-labs/FLUX.1-schnell',       // Rápido, 4 steps
    'flux-dev':     'black-forest-labs/FLUX.1-dev',            // Qualidade alta, mais lento
    'sdxl':         'stabilityai/stable-diffusion-xl-base-1.0', // Clássico, bom fallback
};

/**
 * Gera uma imagem via HuggingFace Inference API
 *
 * @param {Object} opcoes
 * @param {string} opcoes.prompt - Descrição da imagem a gerar
 * @param {string} [opcoes.modelo] - Chave do modelo (flux-schnell, flux-dev, sdxl) ou ID completo
 * @param {string} [opcoes.outputPath] - Caminho para gravar o ficheiro (opcional)
 * @param {Object} [opcoes.parametros] - Parâmetros extra do modelo (width, height, etc.)
 * @returns {Promise<{buffer: Buffer, path?: string, modelo: string, tempo: number}>}
 */
async function gerarImagem(opcoes) {
    const {
        prompt,
        modelo = 'flux-schnell',
        outputPath = null,
        parametros = {},
    } = opcoes;

    // Validar token
    const token = config.huggingface?.token;
    if (!token) {
        throw new Error('HF_TOKEN não configurado. Adiciona ao .env: HF_TOKEN=hf_xxx');
    }

    // Resolver modelo
    const modeloId = MODELOS[modelo] || modelo;
    logger.info(`[ImageGen] Gerando imagem com ${modeloId}...`);
    logger.info(`[ImageGen] Prompt: ${prompt.substring(0, 80)}...`);

    const inicio = Date.now();

    // Chamar API
    const url = `${config.huggingface.apiUrl}/${modeloId}`;
    const body = {
        inputs: prompt,
        parameters: {
            width: parametros.width || 1024,
            height: parametros.height || 768,
            num_inference_steps: parametros.steps || (modelo === 'flux-schnell' ? 4 : 25),
            ...parametros,
        },
    };

    const resposta = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    // Verificar erros
    if (!resposta.ok) {
        const erro = await resposta.text();

        // Modelo a carregar — retry automático
        if (resposta.status === 503) {
            const data = JSON.parse(erro);
            const tempoEstimado = data.estimated_time || 30;
            logger.warn(`[ImageGen] Modelo a carregar, retry em ${Math.ceil(tempoEstimado)}s...`);
            await sleep(tempoEstimado * 1000);
            return gerarImagem(opcoes); // Retry
        }

        throw new Error(`HuggingFace API erro ${resposta.status}: ${erro}`);
    }

    const buffer = Buffer.from(await resposta.arrayBuffer());
    const tempo = Date.now() - inicio;

    logger.info(`[ImageGen] Imagem gerada em ${(tempo / 1000).toFixed(1)}s (${(buffer.length / 1024).toFixed(0)}KB)`);

    // Gravar ficheiro se pedido
    let path = outputPath;
    if (path) {
        const dir = dirname(path);
        if (!existsSync(dir)) {
            await mkdir(dir, { recursive: true });
        }
        await writeFile(path, buffer);
        logger.info(`[ImageGen] Gravada em: ${path}`);
    }

    return { buffer, path, modelo: modeloId, tempo };
}

/**
 * Gera imagem de produto para e-commerce
 * Adiciona automaticamente termos de fotografia profissional ao prompt
 *
 * @param {Object} opcoes
 * @param {string} opcoes.produto - Nome/descrição do produto
 * @param {string} [opcoes.estilo] - Estilo: 'minimal', 'lifestyle', 'hero', 'detail'
 * @param {string} [opcoes.fundo] - Cor/tipo de fundo: 'branco', 'gradiente', 'contexto'
 * @param {string} [opcoes.outputPath] - Caminho para gravar
 * @returns {Promise<{buffer: Buffer, path?: string, modelo: string, tempo: number}>}
 */
async function gerarImagemProduto(opcoes) {
    const {
        produto,
        estilo = 'minimal',
        fundo = 'branco',
        outputPath = null,
    } = opcoes;

    const estilos = {
        minimal: 'minimalist product photography, clean composition, centered product, soft shadows',
        lifestyle: 'lifestyle product photography, natural setting, warm ambient lighting, in-use context',
        hero: 'hero shot product photography, dramatic lighting, low angle, premium feel, cinematic',
        detail: 'macro product photography, extreme close-up, texture detail, sharp focus, studio lighting',
    };

    const fundos = {
        branco: 'pure white background, seamless backdrop',
        gradiente: 'soft gradient background, light to dark, elegant',
        contexto: 'contextual environment, natural setting, complementary props',
        escuro: 'dark moody background, dramatic contrast, spotlight',
    };

    const prompt = [
        `Professional e-commerce product photography of ${produto}`,
        estilos[estilo] || estilos.minimal,
        fundos[fundo] || fundos.branco,
        'high resolution, commercial quality, shot with Canon EOS R5 85mm f/1.4',
        'shallow depth of field, color-accurate, no text, no watermark',
    ].join(', ');

    return gerarImagem({
        prompt,
        modelo: 'flux-schnell',
        outputPath,
        parametros: { width: 1024, height: 1024 },
    });
}

/**
 * Gera múltiplas variações de um produto
 *
 * @param {Object} opcoes
 * @param {string} opcoes.produto - Nome/descrição do produto
 * @param {string[]} [opcoes.estilos] - Array de estilos a gerar
 * @param {string} opcoes.outputDir - Directório de output
 * @returns {Promise<Array>}
 */
async function gerarVariacoes(opcoes) {
    const {
        produto,
        estilos = ['minimal', 'hero', 'lifestyle'],
        outputDir,
    } = opcoes;

    if (!existsSync(outputDir)) {
        await mkdir(outputDir, { recursive: true });
    }

    const nomeBase = produto.toLowerCase().replace(/[^a-z0-9]+/g, '-').substring(0, 30);
    const resultados = [];

    for (const estilo of estilos) {
        try {
            const resultado = await gerarImagemProduto({
                produto,
                estilo,
                outputPath: resolve(outputDir, `${nomeBase}-${estilo}.png`),
            });
            resultados.push({ estilo, ...resultado, sucesso: true });
        } catch (erro) {
            logger.error(`[ImageGen] Erro no estilo ${estilo}: ${erro.message}`);
            resultados.push({ estilo, sucesso: false, erro: erro.message });
        }
    }

    const sucesso = resultados.filter(r => r.sucesso).length;
    logger.info(`[ImageGen] Variações geradas: ${sucesso}/${estilos.length}`);

    return resultados;
}

// Utility
function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

export {
    gerarImagem,
    gerarImagemProduto,
    gerarVariacoes,
    MODELOS,
};

export default { gerarImagem, gerarImagemProduto, gerarVariacoes, MODELOS };
