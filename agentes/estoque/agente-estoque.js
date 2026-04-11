// =====================================================
// AGENTE ESTOQUE — Monitoramento e alertas
// =====================================================
// Capacidades:
// - Monitorar níveis de estoque em tempo real
// - Alertar produtos com estoque baixo
// - Prever necessidade de reposição
// - Sincronizar com fornecedores
// =====================================================

import { AgenteBase } from '../core/agente-base.js';

class AgenteEstoque extends AgenteBase {
    constructor(config) {
        super({
            id: 'estoque',
            nome: 'Agente de Estoque',
            descricao: 'Monitora níveis de estoque e alerta sobre reposição',
            intervaloMinutos: 30, // Verifica a cada 30 minutos
            ...config
        });

        this.limites = {
            estoqueMinimo: 5,
            estoqueCritico: 2,
            estoqueIdeal: 50
        };

        this.produtosMonitorados = new Map();
        this.alertas = [];
    }

    async _tarefa() {
        const acoes = [];
        const resultados = {
            produtosVerificados: 0,
            alertasGerados: 0,
            sincronizacoes: 0,
            previsoes: []
        };

        try {
            // 1. Verificar estoque atual de todos os produtos
            const estoque = await this._verificarEstoque();
            resultados.produtosVerificados = estoque.length;

            // 2. Identificar produtos com estoque baixo
            const alertas = this._identificarAlertas(estoque);
            resultados.alertasGerados = alertas.length;

            if (alertas.length > 0) {
                acoes.push('alertas_gerados');
                
                for (const alerta of alertas) {
                    this.notificar('estoque_alerta', alerta);
                }
            }

            // 3. Sincronizar estoque com CJ Dropshipping
            const sincronizacao = await this._sincronizarComFornecedor(estoque);
            resultados.sincronizacoes = sincronizacao.atualizados;

            if (sincronizacao.atualizados > 0) {
                acoes.push('estoque_sincronizado');
            }

            // 4. Gerar previsões de reposição
            resultados.previsoes = await this._gerarPrevisoes(estoque);

            return {
                sucesso: true,
                acoes,
                dados: resultados,
                mensagem: `${resultados.produtosVerificados} produtos verificados, ${resultados.alertasGerados} alertas`
            };

        } catch (erro) {
            return {
                sucesso: false,
                acoes,
                dados: resultados,
                mensagem: `Erro no monitoramento: ${erro.message}`
            };
        }
    }

    async _verificarEstoque() {
        // Buscar estoque atual da Shopify
        const produtos = [];
        
        for (const [productId, info] of this.produtosMonitorados) {
            // Simulação - em produção, buscar da API
            produtos.push({
                id: productId,
                nome: info.nome,
                estoqueAtual: Math.floor(Math.random() * 20), // Simulado
                vendasUltimos7Dias: Math.floor(Math.random() * 10),
                status: 'ativo'
            });
        }

        return produtos;
    }

    _identificarAlertas(estoque) {
        const alertas = [];

        for (const produto of estoque) {
            if (produto.estoqueAtual <= this.limites.estoqueCritico) {
                alertas.push({
                    nivel: 'critico',
                    produtoId: produto.id,
                    nome: produto.nome,
                    estoqueAtual: produto.estoqueAtual,
                    mensagem: `Estoque CRÍTICO: ${produto.nome} tem apenas ${produto.estoqueAtual} unidades`,
                    acaoRecomendada: 'pausar_anuncios'
                });
            } else if (produto.estoqueAtual <= this.limites.estoqueMinimo) {
                alertas.push({
                    nivel: 'alerta',
                    produtoId: produto.id,
                    nome: produto.nome,
                    estoqueAtual: produto.estoqueAtual,
                    mensagem: `Estoque BAIXO: ${produto.nome} tem ${produto.estoqueAtual} unidades`,
                    acaoRecomendada: 'repor_urgente'
                });
            }
        }

        return alertas;
    }

    async _sincronizarComFornecedor(estoque) {
        const atualizados = { count: 0, produtos: [] };

        // Verificar estoque real no CJ Dropshipping
        // Atualizar Shopify se houver discrepâncias

        return atualizados;
    }

    async _gerarPrevisoes(estoque) {
        const previsoes = [];

        for (const produto of estoque) {
            const velocidadeVenda = produto.vendasUltimos7Dias / 7; // vendas/dia
            const diasAteEsgotar = produto.estoqueAtual / (velocidadeVenda || 0.1);

            if (diasAteEsgotar < 14) {
                previsoes.push({
                    produtoId: produto.id,
                    nome: produto.nome,
                    estoqueAtual: produto.estoqueAtual,
                    velocidadeVenda: velocidadeVenda.toFixed(2),
                    diasAteEsgotar: Math.floor(diasAteEsgotar),
                    recomendacao: diasAteEsgotar < 7 ? 'repor_imediatamente' : 'repor_em_breve',
                    quantidadeSugerida: Math.max(this.limites.estoqueIdeal - produto.estoqueAtual, 50)
                });
            }
        }

        return previsoes.sort((a, b) => a.diasAteEsgotar - b.diasAteEsgotar);
    }

    // Interface pública
    monitorarProduto(productId, nome, fornecedorId = null) {
        this.produtosMonitorados.set(productId, {
            id: productId,
            nome,
            fornecedorId,
            historico: []
        });
        
        this._log('info', `Produto ${nome} adicionado ao monitoramento de estoque`);
    }

    removerMonitoramento(productId) {
        this.produtosMonitorados.delete(productId);
    }

    atualizarLimites(novosLimites) {
        this.limites = { ...this.limites, ...novosLimites };
    }

    getAlertasAtivos() {
        return this.alertas.filter(a => a.status === 'ativo');
    }
}

export { AgenteEstoque };
