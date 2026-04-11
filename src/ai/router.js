// =====================================================
// AI ROUTER — Interpreta comandos em linguagem natural
// =====================================================
// Recebe texto do operador, classifica a intenção via LLM
// e executa a ação correspondente no sistema de agentes.
// =====================================================

import { llmClient } from './llm-client.js';
import { promptClassificarComando } from './prompts.js';
import { criarLogger } from '../core/logger.js';

const log = criarLogger('ai-router');

class AIRouter {
    constructor(manager, agentes) {
        this.manager = manager;
        this.agentes = agentes;
        this.historico = [];
    }

    // =====================================================
    // PROCESSAR COMANDO
    // =====================================================

    async processar(texto) {
        log.info(`Comando recebido: "${texto}"`);

        // 1. Tentar match local rápido (sem LLM)
        const matchLocal = this._matchLocal(texto);
        if (matchLocal) {
            log.info(`Match local: ${matchLocal.intencao}`);
            return await this._executar(matchLocal);
        }

        // 2. Classificar via LLM
        const { sistema, prompt } = promptClassificarComando(texto);
        const resposta = await llmClient.enviar(prompt, { sistema, temperatura: 0.1, maxTokens: 256 });

        try {
            const classificacao = JSON.parse(resposta.texto);
            log.info(`Classificação LLM: ${classificacao.intencao} (${classificacao.confianca}%)`);

            this.historico.push({
                texto,
                classificacao,
                timestamp: new Date().toISOString(),
            });

            if (classificacao.confianca < 50) {
                return {
                    sucesso: false,
                    mensagem: `Não tenho a certeza do que queres dizer. Podes reformular? (confiança: ${classificacao.confianca}%)`,
                };
            }

            return await this._executar(classificacao);
        } catch (erro) {
            log.error('Erro ao parsear resposta do LLM', erro.message);
            return {
                sucesso: false,
                mensagem: 'Não consegui interpretar o comando. Tenta ser mais específico.',
                respostaRaw: resposta.texto,
            };
        }
    }

    // =====================================================
    // MATCH LOCAL (sem LLM — palavras-chave)
    // =====================================================

    _matchLocal(texto) {
        const t = texto.toLowerCase().trim();

        // Status
        if (/^(status|estado|como est[aá])/.test(t)) {
            return { intencao: 'status', agente: null, parametros: {} };
        }

        // Executar agente específico
        const agenteMatch = t.match(/^(executar|rodar|correr)\s+(shopify|cj|precos|marketing|estoque|blender|automacao)/);
        if (agenteMatch) {
            return { intencao: 'executar_agente', agente: agenteMatch[2], parametros: {} };
        }

        // Render
        if (/^(render|gerar render|3d)/.test(t)) {
            return { intencao: 'gerar_render', agente: 'blender', parametros: {} };
        }

        // Relatório
        if (/^(relat[oó]rio|report|exportar)/.test(t)) {
            return { intencao: 'relatorio', agente: null, parametros: {} };
        }

        // FAQ
        if (/^(faq|pergunta|chatbot)/.test(t)) {
            return { intencao: 'consultar_faq', agente: 'automacao', parametros: { texto: t } };
        }

        return null; // sem match — vai para LLM
    }

    // =====================================================
    // EXECUTAR AÇÃO
    // =====================================================

    async _executar(classificacao) {
        const { intencao, agente, parametros } = classificacao;

        switch (intencao) {
            case 'status':
                return {
                    sucesso: true,
                    dados: this.manager.getStatusCompleto(),
                    mensagem: 'Status do sistema obtido.',
                };

            case 'executar_agente':
                if (!agente || !this.agentes[agente]) {
                    return { sucesso: false, mensagem: `Agente "${agente}" não encontrado.` };
                }
                const resultado = await this.manager.executarAgente(agente);
                return {
                    sucesso: true,
                    dados: resultado,
                    mensagem: `Agente ${agente} executado.`,
                };

            case 'relatorio':
                const arquivo = await this.manager.exportarRelatorio();
                return {
                    sucesso: true,
                    dados: { arquivo },
                    mensagem: `Relatório exportado: ${arquivo}`,
                };

            case 'consultar_faq':
                if (this.agentes.automacao) {
                    const faq = this.agentes.automacao.responderPergunta(parametros.texto || '');
                    return { sucesso: true, dados: faq, mensagem: faq.resposta };
                }
                return { sucesso: false, mensagem: 'Agente de automação não disponível.' };

            case 'gerar_render':
                return {
                    sucesso: true,
                    mensagem: 'Para gerar render, use: render({id, nome, sku, categoria}, tipos)',
                    dados: { dica: 'Use renderStatus() para ver a fila' },
                };

            case 'adicionar_produto':
            case 'ajustar_preco':
            case 'criar_campanha':
                return {
                    sucesso: true,
                    mensagem: `Ação "${intencao}" reconhecida. Funcionalidade em desenvolvimento.`,
                    dados: { classificacao },
                };

            default:
                return {
                    sucesso: false,
                    mensagem: `Intenção "${intencao}" não suportada ainda.`,
                };
        }
    }

    // =====================================================
    // STATS
    // =====================================================

    getHistorico() {
        return this.historico.slice(-20);
    }
}

export { AIRouter };
export default AIRouter;
