// =====================================================
// SKILL 4 — AUTOMAÇÃO ⚙️
// =====================================================
// Responsável EXCLUSIVAMENTE por automatizar processos
// operacionais. NÃO cria site do zero. NÃO faz pesquisa.
// Ferramentas: API Claude, webhooks, cron jobs, chatbot.
// =====================================================

class SkillAutomacao {
    constructor() {
        this.nome = 'Automação';
        this.id = 'automacao';
        this.activa = true;

        // Processos automatizáveis
        this.processos = {
            atendimento: {
                nome: 'Atendimento ao Cliente',
                tipo: 'chatbot',
                status: 'pendente',
                descricao: 'Respostas automáticas para perguntas frequentes'
            },
            pedidos: {
                nome: 'Fluxo de Pedidos',
                tipo: 'webhook',
                status: 'pendente',
                descricao: 'Repassar pedidos automaticamente ao fornecedor'
            },
            rastreamento: {
                nome: 'Rastreamento Automático',
                tipo: 'cron',
                status: 'pendente',
                descricao: 'Enviar código de rastreamento ao cliente por e-mail'
            },
            stock: {
                nome: 'Actualização de Stock',
                tipo: 'api',
                status: 'pendente',
                descricao: 'Sincronizar stock com o fornecedor automaticamente'
            },
            notificacoes: {
                nome: 'Notificações',
                tipo: 'webhook',
                status: 'pendente',
                descricao: 'Alertas de pedido, envio, entrega e problemas'
            }
        };

        // Respostas automáticas do chatbot
        this.respostasAutomaticas = {
            'prazo de entrega': 'O prazo de entrega varia entre 7 a 15 dias úteis. Você receberá o código de rastreamento por e-mail assim que o produto for enviado.',
            'rastreamento': 'Pode acompanhar o seu pedido com o código de rastreamento enviado por e-mail. Se não recebeu, verifique a pasta de spam ou entre em contacto connosco.',
            'devolução': 'Aceitamos devoluções em até 30 dias após a entrega. O produto deve estar em condições originais. Entre em contacto para iniciar o processo.',
            'pagamento': 'Aceitamos cartão de crédito, PIX e boleto. Todos os pagamentos são processados com segurança via Stripe.',
            'produto com defeito': 'Lamentamos o inconveniente. Envie fotos do defeito para nosso e-mail e faremos a troca ou reembolso em até 48 horas.',
            'cancelamento': 'Pode cancelar o pedido em até 24 horas após a compra. Depois desse prazo, o pedido já estará em processamento.'
        };
    }

    // -------------------------------------------------
    // EXECUTAR: Ponto de entrada da skill
    // -------------------------------------------------
    async executar(comando, contexto = null) {
        console.log(`⚙️ Skill 4 activada: ${comando}`);

        try {
            // Se veio do fluxo de marketing, configurar automações
            if (contexto && contexto.campanhas) {
                const automacoes = this.configurarAutomacoes(contexto.campanhas);
                return {
                    status: 'sucesso',
                    skill: this.id,
                    dados: automacoes,
                    proximo_passo: null,   // Última skill do fluxo
                    timestamp: new Date().toISOString()
                };
            }

            // Verificar se é uma pergunta de atendimento
            const respostaBot = this.processarPergunta(comando);
            if (respostaBot) {
                return {
                    status: 'sucesso',
                    skill: this.id,
                    dados: {
                        tipo: 'atendimento_automatico',
                        pergunta: comando,
                        resposta: respostaBot
                    },
                    proximo_passo: null,
                    timestamp: new Date().toISOString()
                };
            }

            // Caso contrário, retornar status dos processos
            return {
                status: 'sucesso',
                skill: this.id,
                dados: {
                    processos: this.processos,
                    total_automatizados: this.contarAutomatizados(),
                    total_pendentes: this.contarPendentes()
                },
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        } catch (erro) {
            return {
                status: 'erro',
                skill: this.id,
                dados: null,
                mensagem: `Erro na automação: ${erro.message}`,
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        }
    }

    // -------------------------------------------------
    // CONFIGURAR: Montar automações para campanhas
    // -------------------------------------------------
    configurarAutomacoes(campanhas) {
        const automacoes = [];

        // 1. Webhook de pedidos para cada produto em campanha
        campanhas.forEach(campanha => {
            automacoes.push({
                tipo: 'webhook',
                evento: 'novo_pedido',
                produto: campanha.produto,
                accao: 'repassar_fornecedor',
                descricao: `Quando houver pedido de "${campanha.produto}", repassar ao fornecedor automaticamente`
            });
        });

        // 2. Cron job de rastreamento (a cada 6 horas)
        automacoes.push({
            tipo: 'cron',
            intervalo: '0 */6 * * *',
            accao: 'verificar_rastreamento',
            descricao: 'Verificar códigos de rastreamento e enviar ao cliente'
        });

        // 3. Notificação de stock baixo
        automacoes.push({
            tipo: 'webhook',
            evento: 'stock_baixo',
            limite: 10,
            accao: 'alerta_lojista',
            descricao: 'Alertar quando stock de um produto ficar abaixo de 10 unidades'
        });

        // 4. Chatbot de atendimento
        automacoes.push({
            tipo: 'chatbot',
            respostas: Object.keys(this.respostasAutomaticas).length,
            accao: 'atendimento_automatico',
            descricao: `Chatbot com ${Object.keys(this.respostasAutomaticas).length} respostas automáticas configuradas`
        });

        return {
            total_automacoes: automacoes.length,
            automacoes: automacoes
        };
    }

    // -------------------------------------------------
    // CHATBOT: Processar pergunta do cliente
    // -------------------------------------------------
    processarPergunta(pergunta) {
        const perguntaLower = pergunta.toLowerCase();

        for (const [chave, resposta] of Object.entries(this.respostasAutomaticas)) {
            if (perguntaLower.includes(chave)) {
                return resposta;
            }
        }

        return null;  // Não encontrou resposta automática
    }

    // -------------------------------------------------
    // HELPERS
    // -------------------------------------------------
    contarAutomatizados() {
        return Object.values(this.processos)
            .filter(p => p.status === 'activo').length;
    }

    contarPendentes() {
        return Object.values(this.processos)
            .filter(p => p.status === 'pendente').length;
    }
}

export { SkillAutomacao };
