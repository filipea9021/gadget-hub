// =====================================================
// AGENTE PREÇOS — Monitoramento e ajuste automático
// =====================================================
// Capacidades:
// - Monitorar preços da concorrência
// - Ajustar preços dinamicamente
// - Manter margem mínima de 40%
// - Detectar oportunidades de promoção
// =====================================================

import { AgenteBase } from '../core/agente-base.js';

class AgentePrecos extends AgenteBase {
    constructor(config) {
        super({
            id: 'precos',
            nome: 'Agente de Preços',
            descricao: 'Monitora e ajusta preços mantendo competitividade e margem',
            intervaloMinutos: 120, // Verifica a cada 2 horas
            ...config
        });

        this.regras = {
            margemMinima: 40,
            margemAlvo: 50,
            margemMaxima: 70,
            ajusteMaximo: 10, // % máximo de alteração por ciclo
            precosPsicologicos: true
        };

        this.competidores = [
            { nome: 'Amazon', url: 'https://amazon.es', ativo: true },
            { nome: 'FNAC', url: 'https://fnac.pt', ativo: true },
            { nome: 'AliExpress', url: 'https://aliexpress.com', ativo: false }
        ];

        this.historicoPrecos = new Map();
    }

    async _tarefa() {
        const acoes = [];
        const resultados = {
            produtosAnalisados: 0,
            precosAjustados: 0,
            oportunidades: [],
            alertas: []
        };

        try {
            // 1. Buscar produtos ativos da loja
            const produtos = await this._buscarProdutosAtivos();
            resultados.produtosAnalisados = produtos.length;

            // 2. Analisar cada produto
            for (const produto of produtos) {
                const analise = await this._analisarProduto(produto);
                
                if (analise.recomendacao !== 'manter') {
                    const ajuste = await this._executarAjuste(produto, analise);
                    if (ajuste.sucesso) {
                        resultados.precosAjustados++;
                    }
                }

                if (analise.oportunidade) {
                    resultados.oportunidades.push({
                        produto: produto.id,
                        tipo: analise.oportunidade,
                        precoSugerido: analise.precoSugerido
                    });
                }
            }

            if (resultados.precosAjustados > 0) {
                acoes.push('precos_ajustados');
                this.notificar('precos_atualizados', { total: resultados.precosAjustados });
            }

            if (resultados.oportunidades.length > 0) {
                acoes.push('oportunidades_identificadas');
            }

            return {
                sucesso: true,
                acoes,
                dados: resultados,
                mensagem: `${resultados.precosAjustados} preços ajustados, ${resultados.oportunidades.length} oportunidades`
            };

        } catch (erro) {
            return {
                sucesso: false,
                acoes,
                dados: resultados,
                mensagem: `Erro na análise de preços: ${erro.message}`
            };
        }
    }

    async _analisarProduto(produto) {
        const precoAtual = parseFloat(produto.preco);
        const precoCusto = produto.precoCusto || (precoAtual * 0.5); // Estimativa
        
        // Calcular margem atual
        const margemAtual = ((precoAtual - precoCusto) / precoAtual) * 100;
        
        // Buscar preço médio de mercado (simulado)
        const precoMercado = await this._buscarPrecoConcorrencia(produto);
        
        // Determinar recomendação
        let recomendacao = 'manter';
        let precoSugerido = precoAtual;
        let oportunidade = null;

        // Margem muito baixa - precisa aumentar
        if (margemAtual < this.regras.margemMinima) {
            precoSugerido = this._calcularPrecoMinimo(precoCusto);
            recomendacao = 'aumentar';
        }
        // Margem alta e preço acima do mercado - pode reduzir
        else if (margemAtual > this.regras.margemMaxima && precoAtual > precoMercado * 1.1) {
            precoSugerido = this._calcularPrecoCompetitivo(precoCusto, precoMercado);
            recomendacao = 'reduzir';
            oportunidade = 'preco_competitivo';
        }
        // Oportunidade de promoção
        else if (margemAtual > 55 && precoMercado > precoAtual * 1.2) {
            oportunidade = 'promocao_agressiva';
        }

        // Verificar se ajuste está dentro do limite permitido
        const variacao = Math.abs((precoSugerido - precoAtual) / precoAtual) * 100;
        if (variacao > this.regras.ajusteMaximo) {
            // Limitar ajuste
            const fator = precoSugerido > precoAtual ? 1 + (this.regras.ajusteMaximo / 100) : 1 - (this.regras.ajusteMaximo / 100);
            precoSugerido = precoAtual * fator;
        }

        // Aplicar preço psicológico
        if (this.regras.precosPsicologicos) {
            precoSugerido = this._aplicarPrecoPsicologico(precoSugerido);
        }

        return {
            recomendacao,
            precoAtual,
            precoSugerido: Math.round(precoSugerido * 100) / 100,
            margemAtual: Math.round(margemAtual * 10) / 10,
            margemNova: Math.round(((precoSugerido - precoCusto) / precoSugerido) * 100 * 10) / 10,
            precoMercado,
            oportunidade
        };
    }

    async _buscarPrecoConcorrencia(produto) {
        // Simulação - em produção, usaria scraping ou APIs
        // Retorna preço médio estimado baseado no produto
        const precoBase = parseFloat(produto.preco);
        const variacao = (Math.random() - 0.5) * 0.3; // ±15%
        return precoBase * (1 + variacao);
    }

    _calcularPrecoMinimo(precoCusto) {
        // Garante margem mínima de 40%
        return precoCusto / (1 - this.regras.margemMinima / 100);
    }

    _calcularPrecoCompetitivo(precoCusto, precoMercado) {
        // Preço entre margem alvo e preço de mercado
        const precoMargem = precoCusto / (1 - this.regras.margemAlvo / 100);
        return Math.min(precoMargem, precoMercado * 0.95); // 5% abaixo do mercado
    }

    _aplicarPrecoPsicologico(preco) {
        // Converter para preço psicológico (X9.90, X9.99, etc)
        const base = Math.floor(preco);
        const decimal = preco - base;
        
        if (base < 10) return base + 0.99;
        if (base < 50) return base + 0.90;
        if (base < 100) return base - 0.10;
        return base - 1 + 0.90;
    }

    async _executarAjuste(produto, analise) {
        // Notificar agente Shopify para atualizar preço
        this.notificar('ajustar_preco', {
            produtoId: produto.id,
            novoPreco: analise.precoSugerido,
            motivo: analise.recomendacao,
            margemAnterior: analise.margemAtual,
            margemNova: analise.margemNova
        });

        // Registrar histórico
        if (!this.historicoPrecos.has(produto.id)) {
            this.historicoPrecos.set(produto.id, []);
        }
        this.historicoPrecos.get(produto.id).push({
            timestamp: new Date().toISOString(),
            precoAnterior: analise.precoAtual,
            precoNovo: analise.precoSugerido,
            motivo: analise.recomendacao
        });

        return { sucesso: true };
    }

    async _buscarProdutosAtivos() {
        // Em produção, buscar da API Shopify
        // Por enquanto, retorna dados simulados
        return [];
    }

    getHistoricoPrecos(produtoId) {
        return this.historicoPrecos.get(produtoId) || [];
    }

    atualizarRegras(novasRegras) {
        this.regras = { ...this.regras, ...novasRegras };
        this._log('info', 'Regras de preço atualizadas');
    }
}

export { AgentePrecos };
