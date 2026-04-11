// =====================================================
// AGENTE MARKETING CLIENT — Cliente do Marketing Studio
// =====================================================
// Ponte entre o Gadget Hub e o Marketing Studio.
// Substitui chamadas diretas ao AgenteBlender por
// pedidos ao Marketing Studio via:
//   1. Message Bus (local, se ambos correm no mesmo workspace)
//   2. HTTP API (remoto, se Marketing Studio corre na cloud)
//
// Mantém retrocompatibilidade: emite os mesmos eventos
// que o AgenteBlender original (renders_prontos).
// =====================================================

// Usa o AgenteBase do shared diretamente — este agente é novo
// e não depende da database legacy do Gadget Hub.
// O db é injectado via config.
import { AgenteBase } from '../../../shared/core/agente-base.js';

class AgenteMarketingClient extends AgenteBase {
    constructor(config = {}) {
        super({
            id: 'marketing-client',
            nome: 'Marketing Studio Client',
            descricao: 'Cliente do Marketing Studio — envia pedidos de vídeo e recebe resultados',
            intervaloMinutos: config.intervaloMinutos || 10,
            ...config
        });

        // Conexão ao Marketing Studio
        this.studioUrl = config.studioUrl || process.env.MARKETING_STUDIO_URL || 'http://localhost:3002';
        this.messageBus = config.messageBus || null;

        // Fila local de pedidos pendentes (para quando Studio não responde)
        this.pedidosPendentes = [];
        this.pedidosEnviados = new Map(); // id → { timestamp, dados }

        // Stats
        this.stats = {
            totalPedidosEnviados: 0,
            totalRespostasRecebidas: 0,
            totalFalhados: 0,
            ultimoPedido: null,
            ultimaResposta: null,
        };
    }

    // =====================================================
    // INJETAR MESSAGE BUS (feito no main.js)
    // =====================================================
    setMessageBus(bus) {
        this.messageBus = bus;
    }

    // =====================================================
    // TAREFA PRINCIPAL — Verificar respostas + reenviar falhas
    // =====================================================
    async _tarefa() {
        const acoes = [];

        try {
            // 1. Verificar estado do Marketing Studio
            const studioHealth = await this._verificarStudio();
            acoes.push(studioHealth.ok ? 'studio_online' : 'studio_offline');

            // 2. Reenviar pedidos pendentes
            if (this.pedidosPendentes.length > 0 && studioHealth.ok) {
                const reenviados = await this._reenviarPendentes();
                if (reenviados > 0) {
                    acoes.push(`${reenviados}_reenviados`);
                }
            }

            // 3. Verificar status dos pedidos enviados
            const respostas = await this._verificarPedidosEnviados();
            if (respostas.length > 0) {
                acoes.push(`${respostas.length}_respostas`);

                // Emitir eventos compatíveis com o pipeline do Blender
                for (const resposta of respostas) {
                    this._emitirResultado(resposta);
                }
            }

            return {
                sucesso: true, acoes,
                dados: {
                    studioOnline: studioHealth.ok,
                    pedidosPendentes: this.pedidosPendentes.length,
                    pedidosEnviados: this.pedidosEnviados.size,
                    stats: this.stats,
                },
                mensagem: `Client cycle: ${acoes.length} ações`
            };

        } catch (erro) {
            this._log('erro', `Erro no ciclo: ${erro.message}`);
            return { sucesso: false, acoes, mensagem: erro.message };
        }
    }

    // =====================================================
    // ENVIAR PEDIDO DE VÍDEO AO MARKETING STUDIO
    // =====================================================
    // API pública — chamado pelo pipeline ou REPL
    async solicitarVideo(produto, opcoes = {}) {
        const pedidoId = `req_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

        const pedido = {
            id: pedidoId,
            from: 'gadget-hub',
            to: 'marketing-studio',
            task: 'gerar_video',
            payload: {
                produtoId: produto.id || produto.sku,
                produtoNome: produto.nome,
                categoria: produto.categoria,
                sku: produto.sku,
                shopifyProductId: produto.shopify_product_id,
                estilo: opcoes.estilo || 'produto_360',
                renderTypes: opcoes.renderTypes || ['hero', 'turntable'],
                prioridade: opcoes.prioridade || 'normal',
            },
        };

        this._log('info', `📤 Pedido de vídeo: ${produto.nome} [${pedido.payload.estilo}]`);

        const resultado = await this._enviarPedido(pedido);

        if (resultado.enviado) {
            this.pedidosEnviados.set(pedidoId, {
                timestamp: Date.now(),
                dados: pedido.payload,
                studioId: resultado.studioId,
            });
            this.stats.totalPedidosEnviados++;
            this.stats.ultimoPedido = new Date().toISOString();
        }

        return { pedidoId, ...resultado };
    }

    // Atalho compatível com o AgenteBlender
    async solicitarRenderCompleto(produto) {
        return this.solicitarVideo(produto, {
            renderTypes: ['hero', 'multiAngle', 'turntable', 'exploded'],
        });
    }

    // Solicitar vídeo cinematográfico
    async solicitarCinematico(produto, opcoes = {}) {
        return this.solicitarVideo(produto, {
            estilo: 'cinematico',
            renderTypes: [
                opcoes.tipo || 'cinematicOrbit',
            ],
            prioridade: opcoes.prioridade || 'normal',
            ...opcoes,
        });
    }

    // =====================================================
    // ENVIAR PEDIDO (Message Bus ou HTTP)
    // =====================================================
    async _enviarPedido(pedido) {
        // 1. Tentar via Message Bus (preferível — local, persistente)
        if (this.messageBus) {
            try {
                const resultado = await this.messageBus.enviar(pedido);

                if (resultado.status === 'completed') {
                    return {
                        enviado: true,
                        via: 'message-bus',
                        studioId: resultado.result?.id,
                    };
                }

                if (resultado.status === 'queued') {
                    this._log('aviso', `Pedido ${pedido.id} na fila do Message Bus (Studio offline?)`);
                    return { enviado: true, via: 'message-bus-queued' };
                }
            } catch (err) {
                this._log('aviso', `Message Bus falhou: ${err.message}`);
            }
        }

        // 2. Tentar via HTTP API
        try {
            const response = await this.fetchComRetry(`${this.studioUrl}/api/pedidos`, {
                method: 'POST',
                body: JSON.stringify({
                    from: 'gadget-hub',
                    produtoId: pedido.payload.produtoId,
                    produtoNome: pedido.payload.produtoNome,
                    categoria: pedido.payload.categoria,
                    sku: pedido.payload.sku,
                    estilo: pedido.payload.estilo,
                    renderTypes: pedido.payload.renderTypes,
                    prioridade: pedido.payload.prioridade,
                }),
            }, 2);

            return {
                enviado: true,
                via: 'http',
                studioId: response.id,
            };

        } catch (err) {
            this._log('aviso', `HTTP ao Studio falhou: ${err.message}`);
        }

        // 3. Nenhum método funcionou — guardar na fila local
        this.pedidosPendentes.push(pedido);
        this._log('aviso', `Pedido ${pedido.id} guardado na fila local (${this.pedidosPendentes.length} pendentes)`);

        return { enviado: false, via: 'queued-local' };
    }

    // =====================================================
    // VERIFICAR STUDIO
    // =====================================================
    async _verificarStudio() {
        try {
            const health = await this.fetchComRetry(`${this.studioUrl}/api/health`, {}, 1);
            if (health?.status === 'ok') {
                return { ok: true, data: health };
            }
        } catch {
            // Studio offline
        }
        return { ok: false };
    }

    // =====================================================
    // VERIFICAR PEDIDOS ENVIADOS
    // =====================================================
    async _verificarPedidosEnviados() {
        const respostas = [];

        for (const [pedidoId, info] of this.pedidosEnviados) {
            const studioId = info.studioId;
            if (!studioId) continue;

            try {
                const status = await this.fetchComRetry(
                    `${this.studioUrl}/api/pedidos/${studioId}`, {}, 1
                );

                if (status?.pedido?.status === 'completed') {
                    respostas.push({
                        pedidoId,
                        studioId,
                        dados: info.dados,
                        resultado: status,
                    });
                    this.pedidosEnviados.delete(pedidoId);
                    this.stats.totalRespostasRecebidas++;
                    this.stats.ultimaResposta = new Date().toISOString();

                } else if (status?.pedido?.status === 'failed') {
                    this._log('erro', `Pedido ${pedidoId} falhou no Studio: ${status.pedido.erro}`);
                    this.pedidosEnviados.delete(pedidoId);
                    this.stats.totalFalhados++;
                }
                // Se 'processing' ou 'queued', deixar na lista

            } catch {
                // Studio pode estar temporariamente offline
                const age = Date.now() - info.timestamp;
                if (age > 30 * 60 * 1000) {
                    // Mais de 30 min sem resposta — mover para pendentes
                    this._log('aviso', `Pedido ${pedidoId} expirou — reenviando`);
                    this.pedidosPendentes.push({
                        id: pedidoId,
                        from: 'gadget-hub',
                        to: 'marketing-studio',
                        task: 'gerar_video',
                        payload: info.dados,
                    });
                    this.pedidosEnviados.delete(pedidoId);
                }
            }
        }

        return respostas;
    }

    // =====================================================
    // REENVIAR PENDENTES
    // =====================================================
    async _reenviarPendentes() {
        const pendentes = [...this.pedidosPendentes];
        this.pedidosPendentes = [];
        let reenviados = 0;

        for (const pedido of pendentes) {
            const resultado = await this._enviarPedido(pedido);
            if (resultado.enviado) {
                reenviados++;
                this.pedidosEnviados.set(pedido.id, {
                    timestamp: Date.now(),
                    dados: pedido.payload,
                    studioId: resultado.studioId,
                });
            }
        }

        return reenviados;
    }

    // =====================================================
    // EMITIR RESULTADO (compatível com pipeline Blender)
    // =====================================================
    _emitirResultado(resposta) {
        // Emitir no formato que o pipeline do main.js espera
        this.notificar('renders_prontos', {
            produtoId: resposta.dados.produtoId,
            shopifyProductId: resposta.dados.shopifyProductId,
            renders: resposta.resultado?.renders?.map(r => ({
                tipo: r.tipo,
                url: r.arquivo_saida || r.arquivo,
            })) || [],
            animacoes: resposta.resultado?.video ? [{
                tipo: 'video',
                url: resposta.resultado.video.arquivo,
            }] : [],
            via: 'marketing-studio',
        });

        this._log('info', `✅ Resultado recebido: ${resposta.dados.produtoNome}`);
    }

    // =====================================================
    // STATUS E STATS
    // =====================================================
    getStats() {
        return {
            ...this.stats,
            pedidosPendentes: this.pedidosPendentes.length,
            pedidosEmEspera: this.pedidosEnviados.size,
            studioUrl: this.studioUrl,
        };
    }

    async getStudioHealth() {
        return this._verificarStudio();
    }

    async getStudioStats() {
        try {
            return await this.fetchComRetry(`${this.studioUrl}/api/stats`, {}, 1);
        } catch {
            return null;
        }
    }
}

export { AgenteMarketingClient };
export default AgenteMarketingClient;
