// =====================================================
// CONFIG — Configuração centralizada do sistema
// =====================================================
// Carrega variáveis de ambiente e valida no boot.
// Detecta automaticamente: demo / semi / autonomo
// =====================================================

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..', '..');
const WORKSPACE_ROOT = resolve(ROOT, '..');  // Raiz do ecossistema

// Carregar .env manualmente (sem dependência de dotenv)
function loadEnvFile() {
    const paths = [
        resolve(WORKSPACE_ROOT, '.env'),      // Prioridade: .env do ecossistema
        resolve(ROOT, 'config', '.env'),
        resolve(ROOT, '.env'),
        resolve(ROOT, 'agentes', '.env'),
    ];

    for (const envPath of paths) {
        if (existsSync(envPath)) {
            const content = readFileSync(envPath, 'utf8');
            for (const line of content.split('\n')) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#')) continue;
                const [key, ...rest] = trimmed.split('=');
                const value = rest.join('=').trim();
                if (key && !process.env[key.trim()]) {
                    process.env[key.trim()] = value;
                }
            }
            return envPath;
        }
    }
    return null;
}

// Carregar .env
const envFile = loadEnvFile();

// =====================================================
// CONFIGURAÇÃO PRINCIPAL
// =====================================================

const config = {
    // --- Modo de operação ---
    mode: process.env.MODO || 'semi',

    // --- Shopify ---
    shopify: {
        domain: process.env.SHOPIFY_SHOP_DOMAIN || '',
        accessToken: process.env.SHOPIFY_ACCESS_TOKEN || '',
        apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01',
        get isConfigured() {
            return !!(this.domain && this.accessToken);
        }
    },

    // --- CJ Dropshipping ---
    cj: {
        apiKey: process.env.CJ_API_KEY || '',
        email: process.env.CJ_EMAIL || '',
        apiSecret: process.env.CJ_API_SECRET || '',
        baseUrl: 'https://developers.cjdropshipping.com/api2.0/v1',
        get isConfigured() {
            return !!this.apiKey;
        }
    },

    // --- Blender ---
    blender: {
        serverUrl: process.env.BLENDER_SERVER_URL || 'http://localhost:8585',
        apiKey: process.env.BLENDER_API_KEY || '',
        port: parseInt(process.env.BLENDER_PORT || '8585'),
        maxConcurrentJobs: parseInt(process.env.MAX_CONCURRENT_JOBS || '2'),
    },

    // --- IA ---
    ai: {
        provider: process.env.AI_PROVIDER || 'anthropic',
        anthropicKey: process.env.ANTHROPIC_API_KEY || '',
        openaiKey: process.env.OPENAI_API_KEY || '',
        ollamaUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        get isConfigured() {
            return !!(this.anthropicKey || this.openaiKey);
        }
    },

    // --- Notificações ---
    notifications: {
        webhookUrl: process.env.WEBHOOK_URL || '',
        email: process.env.NOTIFICATION_EMAIL || '',
    },

    // --- Marketing ---
    marketing: {
        metaToken: process.env.META_ACCESS_TOKEN || '',
        tiktokToken: process.env.TIKTOK_ACCESS_TOKEN || '',
    },

    // --- HuggingFace ---
    huggingface: {
        token: process.env.HF_TOKEN || '',
        defaultModel: process.env.HF_IMAGE_MODEL || 'black-forest-labs/FLUX.1-schnell',
        apiUrl: 'https://api-inference.huggingface.co/models',
        get isConfigured() {
            return !!this.token;
        }
    },

    // --- Servidor ---
    server: {
        port: parseInt(process.env.GADGET_HUB_PORT || process.env.DASHBOARD_PORT || '3001'),
    },

    // --- Logging ---
    logLevel: process.env.LOG_LEVEL || 'info',

    // --- Intervalos de execução (minutos) ---
    intervals: {
        shopify: 30,
        cj: 60,
        precos: 120,
        marketing: 180,
        estoque: 30,
        blender: 45,
        automacao: 15,
    },

    // --- Limites ---
    limits: {
        margemMinima: 40,
        estoqueMinimo: 5,
        roasMinimo: 2.0,
    },

    // --- Paths ---
    paths: {
        root: ROOT,
        data: resolve(ROOT, 'data'),
        database: resolve(ROOT, 'data', 'gadgethub.db'),
        relatorios: resolve(ROOT, 'data', 'relatorios'),
        blenderOutput: resolve(ROOT, 'src', 'agentes', 'blender', 'output'),
    },

    // --- Status ---
    get isDemo() {
        return !this.shopify.isConfigured && !this.cj.isConfigured;
    },

    get envFile() {
        return envFile;
    }
};

// =====================================================
// BOOT LOG
// =====================================================

function printConfig() {
    console.log('╔════════════════════════════════════════════════════╗');
    console.log('║     🤖 GADGET HUB — Sistema Unificado              ║');
    console.log('║     Shopify + CJ + Blender + IA                    ║');
    console.log('╚════════════════════════════════════════════════════╝\n');

    console.log(`  Modo:       ${config.mode.toUpperCase()}`);
    console.log(`  .env:       ${envFile || 'não encontrado (usando defaults)'}`);
    console.log(`  Shopify:    ${config.shopify.isConfigured ? '✅ configurado' : '⚠️  modo demo'}`);
    console.log(`  CJ:         ${config.cj.isConfigured ? '✅ configurado' : '⚠️  modo demo'}`);
    console.log(`  Blender:    ${config.blender.serverUrl}`);
    console.log(`  IA:         ${config.ai.isConfigured ? `✅ ${config.ai.provider}` : '⚠️  sem API key'}`);
    console.log(`  HuggingFace:${config.huggingface.isConfigured ? ' ✅ configurado' : ' ⚠️  sem token'}`);
    console.log(`  Database:   ${config.paths.database}`);
    console.log('');
}

export { config, printConfig };
export default config;
