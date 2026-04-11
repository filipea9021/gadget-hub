// =====================================================
// NOTIFICADOR — Sistema de notificações
// =====================================================
// Canais:
// - Webhook (Slack, Discord, etc)
// - Email (SMTP)
// - Console (desenvolvimento)
// =====================================================

import fetch from 'node-fetch';

class Notificador {
    constructor(config = {}) {
        this.config = {
            webhookUrl: process.env.WEBHOOK_URL,
            email: process.env.NOTIFICATION_EMAIL,
            modo: process.env.MODO || 'semi',
            ...config
        };
        
        this.historico = [];
    }

    // =====================================================
    // NOTIFICAÇÕES GERAIS
    // =====================================================

    async notificar(tipo, dados) {
        const timestamp = new Date().toISOString();
        const notificacao = { tipo, dados, timestamp };
        
        // Salvar no histórico
        this.historico.push(notificacao);
        if (this.historico.length > 100) {
            this.historico.shift();
        }

        // Enviar por todos os canais configurados
        const promessas = [];
        
        if (this.config.webhookUrl) {
            promessas.push(this._enviarWebhook(notificacao));
        }
        
        if (this.config.email) {
            promessas.push(this._enviarEmail(notificacao));
        }
        
        // Sempre logar no console
        this._logConsole(notificacao);
        
        await Promise.allSettled(promessas);
        
        return notificacao;
    }

    // =====================================================
    // NOTIFICAÇÕES ESPECÍFICAS
    // =====================================================

    async produtoImportado(produto) {
        return this.notificar('produto_importado', {
            titulo: '✅ Produto Importado',
            mensagem: `${produto.nome} foi importado com sucesso`,
            detalhes: {
                sku: produto.sku,
                preco: produto.precoVenda,
                margem: produto.margem,
                score: produto.score,
                categoria: produto.categoria
            }
        });
    }

    async produtoCriadoShopify(produto) {
        return this.notificar('produto_criado_shopify', {
            titulo: '🛒 Produto na Shopify',
            mensagem: `${produto.nome} criado na Shopify`,
            detalhes: {
                sku: produto.sku,
                shopifyProductId: produto.shopifyProductId,
                url: `https://${process.env.SHOPIFY_SHOP_DOMAIN}/products/${produto.handle || produto.sku}`
            }
        });
    }

    async estoqueBaixo(produto, estoqueAtual) {
        return this.notificar('estoque_baixo', {
            titulo: '⚠️ Estoque Baixo',
            mensagem: `${produto.nome} está com estoque baixo`,
            prioridade: 'alta',
            detalhes: {
                sku: produto.sku,
                estoqueAtual,
                estoqueMinimo: 5,
                fornecedor: produto.fornecedor
            }
        });
    }

    async precoAlterado(produto, precoAntigo, precoNovo) {
        const variacao = ((precoNovo - precoAntigo) / precoAntigo * 100).toFixed(1);
        return this.notificar('preco_alterado', {
            titulo: '💰 Preço Alterado',
            mensagem: `${produto.nome} teve o preço ajustado`,
            detalhes: {
                sku: produto.sku,
                precoAntigo,
                precoNovo,
                variacao: `${variacao}%`
            }
        });
    }

    async erro(erro, contexto = {}) {
        return this.notificar('erro', {
            titulo: '❌ Erro no Sistema',
            mensagem: erro.message,
            prioridade: 'critica',
            detalhes: {
                stack: erro.stack,
                contexto,
                timestamp: new Date().toISOString()
            }
        });
    }

    async execucaoAgente(agenteId, resultado) {
        const sucesso = resultado.sucesso;
        return this.notificar('execucao_agente', {
            titulo: sucesso ? '🤖 Agente Executado' : '❌ Falha no Agente',
            mensagem: `Agente ${agenteId} ${sucesso ? 'concluído' : 'falhou'}`,
            detalhes: {
                agenteId,
                sucesso,
                acoes: resultado.acoes,
                duracao: resultado.duracao,
                mensagem: resultado.mensagem
            }
        });
    }

    async resumoDiario(metricas) {
        return this.notificar('resumo_diario', {
            titulo: '📊 Resumo Diário',
            mensagem: `Resumo de ${new Date().toLocaleDateString('pt-BR')}`,
            detalhes: {
                produtosImportados: metricas.produtosImportados,
                produtosVendidos: metricas.produtosVendidos,
                faturamento: metricas.faturamento,
                erros: metricas.erros,
                alertas: metricas.alertas
            }
        });
    }

    // =====================================================
    // CANAIS DE ENVIO
    // =====================================================

    async _enviarWebhook(notificacao) {
        try {
            const payload = this._formatarParaWebhook(notificacao);
            
            const resposta = await fetch(this.config.webhookUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!resposta.ok) {
                throw new Error(`Webhook falhou: ${resposta.status}`);
            }
            
            return true;
        } catch (erro) {
            console.error('Erro ao enviar webhook:', erro.message);
            return false;
        }
    }

    _formatarParaWebhook(notificacao) {
        // Formato compatível com Slack/Discord
        const corMap = {
            'produto_importado': '#10b981',
            'produto_criado_shopify': '#3b82f6',
            'estoque_baixo': '#f59e0b',
            'preco_alterado': '#8b5cf6',
            'erro': '#ef4444',
            'execucao_agente': '#6b7280',
            'resumo_diario': '#3b82f6'
        };

        return {
            text: notificacao.dados.titulo,
            embeds: [{
                title: notificacao.dados.titulo,
                description: notificacao.dados.mensagem,
                color: parseInt(corMap[notificacao.tipo] || '#3b82f6', 16),
                fields: Object.entries(notificacao.dados.detalhes || {}).map(([key, value]) => ({
                    name: key,
                    value: String(value),
                    inline: true
                })),
                timestamp: notificacao.timestamp
            }]
        };
    }

    async _enviarEmail(notificacao) {
        // Implementação básica - em produção usaria nodemailer
        console.log(`📧 [EMAIL PARA ${this.config.email}] ${notificacao.dados.titulo}`);
        return true;
    }

    _logConsole(notificacao) {
        const emojiMap = {
            'produto_importado': '✅',
            'produto_criado_shopify': '🛒',
            'estoque_baixo': '⚠️',
            'preco_alterado': '💰',
            'erro': '❌',
            'execucao_agente': '🤖',
            'resumo_diario': '📊'
        };

        const emoji = emojiMap[notificacao.tipo] || '📢';
        const hora = new Date(notificacao.timestamp).toLocaleTimeString('pt-BR');
        
        console.log(`${emoji} [${hora}] ${notificacao.dados.titulo}`);
        console.log(`   ${notificacao.dados.mensagem}`);
        
        if (notificacao.dados.detalhes) {
            Object.entries(notificacao.dados.detalhes).forEach(([key, value]) => {
                console.log(`   • ${key}: ${value}`);
            });
        }
    }

    // =====================================================
    // INTERFACE PÚBLICA
    // =====================================================

    getHistorico(limite = 10) {
        return this.historico.slice(-limite);
    }

    limparHistorico() {
        this.historico = [];
    }

    configurar(novaConfig) {
        this.config = { ...this.config, ...novaConfig };
    }
}

export { Notificador };
