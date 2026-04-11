// =====================================================
// AGENTE AUTOMAÇÃO — FAQs, Webhooks, Emails, Chatbot
// =====================================================
// Absorve funcionalidades de:
//   - skill4-automacao (FAQs, webhooks, email sequences)
//   - skill3-marketing (hashtags por categoria)
// Roda periodicamente para processar filas de webhooks
// e responder automaticamente a perguntas frequentes.
// =====================================================

import { AgenteBase } from '../core/agente-base.js';

class AgenteAutomacao extends AgenteBase {
    constructor(config = {}) {
        super({
            id: 'automacao',
            nome: 'Agente Automação',
            descricao: 'Gestão de FAQs, webhooks de pedidos, emails automáticos e chatbot',
            intervaloMinutos: config.intervaloMinutos || 15,
        });

        // =====================================================
        // FAQs — Respostas automáticas para chatbot
        // =====================================================
        this.faqs = [
            { pergunta: 'prazo de entrega', resposta: 'O prazo de entrega é de 7 a 15 dias úteis para Portugal.' },
            { pergunta: 'rastreamento', resposta: 'Enviamos o código de rastreamento por email após o envio.' },
            { pergunta: 'devolucao', resposta: 'Aceitamos devoluções em até 30 dias após a entrega.' },
            { pergunta: 'pagamento', resposta: 'Aceitamos MBWay, Multibanco, cartão de crédito e PayPal.' },
            { pergunta: 'mbway', resposta: 'Pode pagar com MBWay de forma rápida e segura.' },
            { pergunta: 'garantia', resposta: 'Todos os produtos têm garantia de 1 ano.' },
            { pergunta: 'frete', resposta: 'Frete grátis para Portugal em compras acima de 30€.' },
            { pergunta: 'contacto', resposta: 'Entre em contacto pelo email suporte@gadget-hub.com.' },
        ];

        // =====================================================
        // SEQUÊNCIAS DE EMAIL
        // =====================================================
        this.emailSequencias = {
            'boas-vindas': { assunto: 'Bem-vindo à Gadget Hub!', delay: 0 },
            'abandono-carrinho': { assunto: 'Esqueceu algo no carrinho?', delay: 3600000 },
            'confirmacao': { assunto: 'Pedido confirmado!', delay: 0 },
            'enviado': { assunto: 'O seu pedido foi enviado!', delay: 0 },
            'entregue': { assunto: 'Pedido entregue — como foi?', delay: 86400000 },
            'pos-compra': { assunto: 'Gostou? Avalie o produto!', delay: 604800000 },
            'recompra': { assunto: 'Novidades que vão gostar!', delay: 2592000000 },
        };

        // =====================================================
        // HASHTAGS POR CATEGORIA (absorvido do skill3)
        // =====================================================
        this.hashtagsPorCategoria = {
            'smart-home': ['#casainteligente', '#smarthome', '#gadgets', '#domotica'],
            'smart_plug': ['#smartplug', '#casainteligente', '#automacao', '#wifi'],
            'audio': ['#fones', '#bluetooth', '#musica', '#audio'],
            'fone': ['#fones', '#bluetooth', '#musica', '#audiofilo'],
            'smartwatch': ['#smartwatch', '#relogio', '#fitness', '#wearable'],
            'acessorios': ['#acessorios', '#tech', '#gadget', '#presentes'],
            'eletronicos': ['#eletronicos', '#tecnologia', '#tech', '#inovacao'],
            'iluminacao': ['#ledstrip', '#iluminacao', '#rgb', '#decoracao'],
            'carregador': ['#carregador', '#wireless', '#fastcharge', '#usbc'],
            'camera': ['#camera', '#seguranca', '#smarthome', '#vigilancia'],
        };

        // Fila de webhooks pendentes
        this.filaWebhooks = [];

        // Stats
        this.stats = {
            faqsRespondidas: 0,
            webhooksProcessados: 0,
            emailsEnviados: 0,
        };
    }

    // =====================================================
    // TAREFA PERIÓDICA
    // =====================================================

    async _tarefa() {
        this._log('info', 'Processando automações...');

        // Processar webhooks pendentes
        const webhooksProcessados = await this._processarFilaWebhooks();

        // Verificar sequências de email pendentes
        const emailsPendentes = await this._verificarEmailsPendentes();

        return {
            webhooksProcessados,
            emailsPendentes,
            faqsDisponiveis: this.faqs.length,
            stats: { ...this.stats },
        };
    }

    // =====================================================
    // CHATBOT / FAQ
    // =====================================================

    responderPergunta(texto) {
        const textoLower = texto.toLowerCase();
        const match = this.faqs.find(f => textoLower.includes(f.pergunta));

        if (match) {
            this.stats.faqsRespondidas++;
            return {
                encontrada: true,
                resposta: match.resposta,
                perguntaOriginal: texto,
                timestamp: new Date().toISOString(),
            };
        }

        return {
            encontrada: false,
            resposta: 'Peço desculpa, não consigo ajudar com essa questão. Entre em contacto com o suporte.',
            perguntaOriginal: texto,
            timestamp: new Date().toISOString(),
        };
    }

    adicionarFAQ(pergunta, resposta) {
        this.faqs.push({ pergunta: pergunta.toLowerCase(), resposta });
        this._log('info', `Nova FAQ adicionada: "${pergunta}"`);
    }

    // =====================================================
    // WEBHOOKS
    // =====================================================

    processarWebhook(evento, dados) {
        const handlers = {
            'order.created': () => this._enviarEmail('confirmacao', dados),
            'order.shipped': () => this._enviarEmail('enviado', dados),
            'order.delivered': () => this._enviarEmail('entregue', dados),
            'cart.abandoned': () => this._enviarEmail('abandono-carrinho', dados),
            'customer.created': () => this._enviarEmail('boas-vindas', dados),
        };

        const handler = handlers[evento];
        if (handler) {
            handler();
            this.stats.webhooksProcessados++;
            this._log('info', `Webhook processado: ${evento}`);
            return { processado: true, evento, timestamp: new Date().toISOString() };
        }

        this._log('warn', `Webhook não reconhecido: ${evento}`);
        return { processado: false, evento, motivo: 'Evento não reconhecido' };
    }

    adicionarWebhookFila(evento, dados) {
        this.filaWebhooks.push({ evento, dados, recebidoEm: new Date().toISOString() });
    }

    async _processarFilaWebhooks() {
        const pendentes = [...this.filaWebhooks];
        this.filaWebhooks = [];

        let processados = 0;
        for (const webhook of pendentes) {
            const resultado = this.processarWebhook(webhook.evento, webhook.dados);
            if (resultado.processado) processados++;
        }

        return processados;
    }

    // =====================================================
    // EMAILS
    // =====================================================

    _enviarEmail(tipo, dados) {
        const seq = this.emailSequencias[tipo];
        if (!seq) {
            this._log('warn', `Sequência de email não encontrada: ${tipo}`);
            return;
        }

        // Em modo real, integraria com serviço de email (SendGrid, SES, etc.)
        this._log('info', `📧 Email "${seq.assunto}" → ${dados.email || 'cliente'}`);
        this.stats.emailsEnviados++;
        return { enviado: true, tipo, assunto: seq.assunto, timestamp: new Date().toISOString() };
    }

    async _verificarEmailsPendentes() {
        // Placeholder — verificaria DB por emails agendados com delay
        return 0;
    }

    // =====================================================
    // HASHTAGS (absorvido do skill3-marketing)
    // =====================================================

    getHashtags(categoria) {
        const base = ['#gadgethub', '#tech', '#portugal', '#shopping'];
        const especificas = this.hashtagsPorCategoria[categoria] || [];
        return [...new Set([...especificas, ...base])];
    }

    // =====================================================
    // GATILHOS DE MARKETING (absorvido do skill3)
    // =====================================================

    gerarGatilho(tipo, params = {}) {
        const gatilhos = {
            escassez: [
                `Últimas ${params.n || 3} unidades!`,
                'Só hoje com este preço!',
                'Stock limitado — garanta já!',
            ],
            urgencia: [
                `Oferta termina em ${params.tempo || '24h'}!`,
                'Promoção relâmpago!',
                'Últimas horas de desconto!',
            ],
            provaSocial: [
                `${params.n || 50} pessoas compraram este produto`,
                `Avaliação ${params.score || '4.8'}/5`,
                'Best-seller em Portugal!',
            ],
            autoridade: [
                'Curado pela nossa equipa',
                `Score de qualidade: ${params.score || 95}/100`,
                'Recomendado por especialistas',
            ],
        };

        const lista = gatilhos[tipo];
        if (!lista) return null;
        return lista[Math.floor(Math.random() * lista.length)];
    }

    // =====================================================
    // STATS
    // =====================================================

    getStats() {
        return {
            ...this.stats,
            faqsDisponiveis: this.faqs.length,
            webhooksPendentes: this.filaWebhooks.length,
            sequenciasEmail: Object.keys(this.emailSequencias).length,
            categoriasHashtags: Object.keys(this.hashtagsPorCategoria).length,
        };
    }
}

export { AgenteAutomacao };
