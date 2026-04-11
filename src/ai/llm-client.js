// =====================================================
// LLM CLIENT — Cliente unificado para Claude / GPT
// =====================================================
// Abstração que suporta múltiplos providers de IA:
//   - Anthropic (Claude) — primário
//   - OpenAI (GPT) — fallback
//   - Ollama (local) — desenvolvimento
// =====================================================

import { config } from '../core/config.js';
import { criarLogger } from '../core/logger.js';

const log = criarLogger('llm-client');

class LLMClient {
    constructor() {
        this.provider = config.ai.provider;
        this.stats = {
            totalRequests: 0,
            totalTokens: 0,
            erros: 0,
        };
    }

    // =====================================================
    // ENVIAR PROMPT
    // =====================================================

    async enviar(prompt, opcoes = {}) {
        const {
            modelo = null,
            temperatura = 0.7,
            maxTokens = 1024,
            sistema = null,
        } = opcoes;

        this.stats.totalRequests++;

        try {
            switch (this.provider) {
                case 'anthropic':
                    return await this._enviarAnthropic(prompt, { modelo, temperatura, maxTokens, sistema });
                case 'openai':
                    return await this._enviarOpenAI(prompt, { modelo, temperatura, maxTokens, sistema });
                case 'ollama':
                    return await this._enviarOllama(prompt, { modelo, temperatura, maxTokens, sistema });
                default:
                    return this._respostaDemo(prompt);
            }
        } catch (erro) {
            this.stats.erros++;
            log.error(`Erro no provider ${this.provider}`, erro.message);

            // Fallback: tentar outro provider
            if (this.provider === 'anthropic' && config.ai.openaiKey) {
                log.warn('Tentando fallback para OpenAI...');
                return await this._enviarOpenAI(prompt, { modelo, temperatura, maxTokens, sistema });
            }

            return this._respostaDemo(prompt);
        }
    }

    // =====================================================
    // ANTHROPIC (Claude)
    // =====================================================

    async _enviarAnthropic(prompt, { modelo, temperatura, maxTokens, sistema }) {
        if (!config.ai.anthropicKey) {
            log.warn('Anthropic API key não configurada — modo demo');
            return this._respostaDemo(prompt);
        }

        const body = {
            model: modelo || 'claude-sonnet-4-20250514',
            max_tokens: maxTokens,
            temperature: temperatura,
            messages: [{ role: 'user', content: prompt }],
        };

        if (sistema) {
            body.system = sistema;
        }

        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': config.ai.anthropicKey,
                'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Anthropic ${response.status}: ${erro}`);
        }

        const data = await response.json();
        const texto = data.content[0]?.text || '';
        const tokens = (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0);
        this.stats.totalTokens += tokens;

        return {
            texto,
            provider: 'anthropic',
            modelo: data.model,
            tokens,
            timestamp: new Date().toISOString(),
        };
    }

    // =====================================================
    // OPENAI (GPT)
    // =====================================================

    async _enviarOpenAI(prompt, { modelo, temperatura, maxTokens, sistema }) {
        if (!config.ai.openaiKey) {
            log.warn('OpenAI API key não configurada — modo demo');
            return this._respostaDemo(prompt);
        }

        const messages = [];
        if (sistema) messages.push({ role: 'system', content: sistema });
        messages.push({ role: 'user', content: prompt });

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.ai.openaiKey}`,
            },
            body: JSON.stringify({
                model: modelo || 'gpt-4o-mini',
                messages,
                temperature: temperatura,
                max_tokens: maxTokens,
            }),
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`OpenAI ${response.status}: ${erro}`);
        }

        const data = await response.json();
        const texto = data.choices[0]?.message?.content || '';
        const tokens = data.usage?.total_tokens || 0;
        this.stats.totalTokens += tokens;

        return {
            texto,
            provider: 'openai',
            modelo: data.model,
            tokens,
            timestamp: new Date().toISOString(),
        };
    }

    // =====================================================
    // OLLAMA (Local)
    // =====================================================

    async _enviarOllama(prompt, { modelo, temperatura, maxTokens, sistema }) {
        const messages = [];
        if (sistema) messages.push({ role: 'system', content: sistema });
        messages.push({ role: 'user', content: prompt });

        const response = await fetch(`${config.ai.ollamaUrl}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: modelo || 'llama3',
                messages,
                options: { temperature: temperatura, num_predict: maxTokens },
                stream: false,
            }),
        });

        if (!response.ok) {
            throw new Error(`Ollama ${response.status}`);
        }

        const data = await response.json();
        return {
            texto: data.message?.content || '',
            provider: 'ollama',
            modelo: modelo || 'llama3',
            tokens: 0,
            timestamp: new Date().toISOString(),
        };
    }

    // =====================================================
    // MODO DEMO (sem API keys)
    // =====================================================

    _respostaDemo(prompt) {
        log.info('🎭 Modo demo — resposta simulada');
        return {
            texto: `[DEMO] Resposta simulada para: "${prompt.substring(0, 80)}..."`,
            provider: 'demo',
            modelo: 'simulado',
            tokens: 0,
            timestamp: new Date().toISOString(),
        };
    }

    // =====================================================
    // UTILITÁRIOS
    // =====================================================

    getStats() {
        return { ...this.stats, provider: this.provider, configurado: config.ai.isConfigured };
    }

    isConfigured() {
        return config.ai.isConfigured;
    }
}

// Singleton
const llmClient = new LLMClient();

export { LLMClient, llmClient };
export default llmClient;
