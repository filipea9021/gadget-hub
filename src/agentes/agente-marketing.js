// =====================================================
// AGENTE MARKETING — Automação de campanhas
// =====================================================
// Capacidades:
// - Gerar copy para anúncios automaticamente
// - Criar campanhas baseadas em performance
// - A/B testing automático
// - Segmentação de público
// - Otimização de ROAS
// =====================================================

import { AgenteBase } from '../core/agente-base.js';

class AgenteMarketing extends AgenteBase {
    constructor(config) {
        super({
            id: 'marketing',
            nome: 'Agente de Marketing',
            descricao: 'Gerencia campanhas publicitárias e otimização de conversão',
            intervaloMinutos: 180, // Análise a cada 3 horas
            ...config
        });

        this.canais = {
            tiktok: { ativo: true, orcamentoDiario: 15, roasMinimo: 2.0 },
            meta: { ativo: true, orcamentoDiario: 15, roasMinimo: 2.5 },
            google: { ativo: false, orcamentoDiario: 0, roasMinimo: 3.0 }
        };

        this.campanhasAtivas = new Map();
        this.templatesCopy = {
            awareness: [
                "🔥 {produto} — Tendência 2024! Descobre porque {n} pessoas já compraram.",
                "✨ Transforma a tua casa com {produto}. Envio grátis para PT! 🇵🇹",
                "🎁 O gadget perfeito para {publico}. Aproveita antes que acabe!"
            ],
            conversion: [
                "⚡ ÚLTIMAS UNIDADES! {produto} com {desconto}% OFF + Frete Grátis",
                "⏰ Oferta termina HOJE — {produto} a apenas {preco}€",
                "🛒 {produto} — Clique e compra em 30 segundos. Pagamento MBWay ✅"
            ],
            remarketing: [
                "Ainda estás a pensar? 👀 {produto} espera por ti + 10% OFF",
                "Esqueceste algo? 🛒 {produto} reservado por mais 24h",
                "Viste isto? 👇 {produto} — Preço especial para ti"
            ]
        };
    }

    async _tarefa() {
        const acoes = [];
        const resultados = {
            campanhasCriadas: 0,
            campanhasOtimizadas: 0,
            campanhasPausadas: 0,
            copyGerada: 0,
            insights: []
        };

        try {
            // 1. Analisar performance das campanhas ativas
            const performance = await this._analisarCampanhas();
            
            // 2. Otimizar campanhas baseado em ROAS
            const otimizacoes = await this._otimizarCampanhas(performance);
            resultados.campanhasOtimizadas = otimizacoes.ajustadas;
            resultados.campanhasPausadas = otimizacoes.pausadas;

            if (otimizacoes.ajustadas > 0) acoes.push('campanhas_otimizadas');
            if (otimizacoes.pausadas > 0) acoes.push('campanhas_pausadas');

            // 3. Identificar produtos para novas campanhas
            const oportunidades = await this._identificarOportunidades();
            
            // 4. Criar campanhas para produtos de alto potencial
            for (const oportunidade of oportunidades.slice(0, 2)) {
                const campanha = await this._criarCampanha(oportunidade);
                if (campanha.sucesso) {
                    resultados.campanhasCriadas++;
                }
            }

            if (resultados.campanhasCriadas > 0) acoes.push('campanhas_criadas');

            // 5. Gerar relatório de insights
            resultados.insights = await this._gerarInsights(performance);

            return {
                sucesso: true,
                acoes,
                dados: resultados,
                mensagem: `${resultados.campanhasCriadas} novas, ${resultados.campanhasOtimizadas} otimizadas, ${resultados.campanhasPausadas} pausadas`
            };

        } catch (erro) {
            return {
                sucesso: false,
                acoes,
                dados: resultados,
                mensagem: `Erro no marketing: ${erro.message}`
            };
        }
    }

    async _analisarCampanhas() {
        const analise = {
            campanhas: [],
            roasMedio: 0,
            cpaMedio: 0,
            conversoes: 0
        };

        for (const [id, campanha] of this.campanhasAtivas) {
            // Simulação de métricas
            const metricas = {
                id,
                gasto: Math.random() * 100,
                receita: Math.random() * 250,
                conversoes: Math.floor(Math.random() * 10),
                cliques: Math.floor(Math.random() * 500),
                impressoes: Math.floor(Math.random() * 10000)
            };

            metricas.roas = metricas.receita / (metricas.gasto || 1);
            metricas.cpa = metricas.gasto / (metricas.conversoes || 1);
            metricas.ctr = (metricas.cliques / (metricas.impressoes || 1)) * 100;

            analise.campanhas.push(metricas);
        }

        if (analise.campanhas.length > 0) {
            analise.roasMedio = analise.campanhas.reduce((a, c) => a + c.roas, 0) / analise.campanhas.length;
            analise.cpaMedio = analise.campanhas.reduce((a, c) => a + c.cpa, 0) / analise.campanhas.length;
            analise.conversoes = analise.campanhas.reduce((a, c) => a + c.conversoes, 0);
        }

        return analise;
    }

    async _otimizarCampanhas(performance) {
        const resultados = { ajustadas: 0, pausadas: 0 };

        for (const campanha of performance.campanhas) {
            const config = this.canais[campanha.canal] || { roasMinimo: 2.0 };

            // Pausar campanha com ROAS baixo
            if (campanha.roas < config.roasMinimo && campanha.gasto > 20) {
                campanha.status = 'pausada';
                resultados.pausadas++;
                this.notificar('campanha_pausada', { campanhaId: campanha.id, roas: campanha.roas });
            }
            // Aumentar orçamento se ROAS alto
            else if (campanha.roas > config.roasMinimo * 1.5) {
                campanha.orcamentoSugerido = campanha.orcamentoAtual * 1.2;
                resultados.ajustadas++;
            }
        }

        return resultados;
    }

    async _identificarOportunidades() {
        // Receber produtos com alto score do agente de produtos
        // Retornar lista de produtos prontos para campanha
        return [];
    }

    async _criarCampanha(oportunidade) {
        const copy = this._gerarCopy(oportunidade.produto, oportunidade.publico);
        const campanha = {
            id: `camp_${Date.now()}`,
            produto: oportunidade.produto.id,
            nome: oportunidade.produto.nome,
            canais: this._selecionarCanais(oportunidade),
            copy,
            orcamentoTotal: this._calcularOrcamento(oportunidade),
            duracaoDias: 7,
            objetivo: 'conversao',
            status: 'ativa',
            criadaEm: new Date().toISOString()
        };

        this.campanhasAtivas.set(campanha.id, campanha);

        // Notificar criação
        this.notificar('campanha_criada', {
            campanhaId: campanha.id,
            produto: oportunidade.produto.nome,
            canais: campanha.canais
        });

        return { sucesso: true, campanha };
    }

    _gerarCopy(produto, publico) {
        const variaveis = {
            produto: produto.nome,
            preco: produto.precoVenda.toFixed(2),
            desconto: 10,
            publico: publico || 'tech lovers',
            n: produto.pedidos || 1000
        };

        const copy = {
            awareness: this._aplicarTemplate(
                this.templatesCopy.awareness[Math.floor(Math.random() * this.templatesCopy.awareness.length)],
                variaveis
            ),
            conversion: this._aplicarTemplate(
                this.templatesCopy.conversion[Math.floor(Math.random() * this.templatesCopy.conversion.length)],
                variaveis
            ),
            remarketing: this.templatesCopy.remarketing.map(t => this._aplicarTemplate(t, variaveis))
        };

        return copy;
    }

    _aplicarTemplate(template, variaveis) {
        return template.replace(/\{(\w+)\}/g, (match, key) => variaveis[key] || match);
    }

    _selecionarCanais(oportunidade) {
        const canais = [];
        if (this.canais.tiktok.ativo && oportunidade.produto.score > 80) {
            canais.push('tiktok');
        }
        if (this.canais.meta.ativo) {
            canais.push('meta');
        }
        return canais;
    }

    _calcularOrcamento(oportunidade) {
        const base = oportunidade.produto.margem > 60 ? 50 : 30;
        return base * 7; // 7 dias
    }

    async _gerarInsights(performance) {
        const insights = [];

        if (performance.roasMedio > 3) {
            insights.push({
                tipo: 'positivo',
                mensagem: `ROAS médio excelente: ${performance.roasMedio.toFixed(2)}x. Aumentar investimento recomendado.`
            });
        }

        if (performance.cpaMedio > 30) {
            insights.push({
                tipo: 'alerta',
                mensagem: `CPA elevado: ${performance.cpaMedio.toFixed(2)}€. Revisar segmentação.`
            });
        }

        return insights;
    }

    // Interface pública
    getCampanhasAtivas() {
        return Array.from(this.campanhasAtivas.values());
    }

    pausarCampanha(campanhaId) {
        const campanha = this.campanhasAtivas.get(campanhaId);
        if (campanha) {
            campanha.status = 'pausada';
            this._log('info', `Campanha ${campanhaId} pausada`);
        }
    }

    atualizarConfigCanais(novaConfig) {
        this.canais = { ...this.canais, ...novaConfig };
    }
}

export { AgenteMarketing };
