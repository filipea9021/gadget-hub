// =====================================================
// ORQUESTRADOR (SKILL 0) — O CÉREBRO DO SISTEMA
// =====================================================
// Recebe comandos do utilizador, analisa e delega para
// a skill correcta. Nunca executa tarefas directamente.
// =====================================================

import { SkillPesquisaProdutos } from './skills/skill1-produtos.js';
import { SkillCriacaoSite } from './skills/skill2-site.js';
import { SkillMarketing } from './skills/skill3-marketing.js';
import { SkillAutomacao } from './skills/skill4-automacao.js';

class Orquestrador {
    constructor() {
        // Registo de todas as skills disponíveis
        this.skills = {
            pesquisa_produtos: new SkillPesquisaProdutos(),
            criacao_site: new SkillCriacaoSite(),
            marketing: new SkillMarketing(),
            automacao: new SkillAutomacao()
        };

        // Histórico de todas as operações executadas
        this.historico = [];

        // Fila de tarefas pendentes (para fluxos multi-skill)
        this.filaTarefas = [];

        // Mapa de palavras-chave → skill (para roteamento inteligente)
        this.roteamento = {
            pesquisa_produtos: [
                'produto', 'pesquisar', 'encontrar', 'catálogo', 'fornecedor',
                'aliexpress', 'cj dropshipping', 'zendrop', 'validar produto',
                'margem', 'avaliação', 'score', 'nicho'
            ],
            criacao_site: [
                'site', 'página', 'layout', 'componente', 'design',
                'frontend', 'backend', 'checkout', 'carrinho', 'mobile',
                'responsivo', 'código', 'html', 'css', 'javascript'
            ],
            marketing: [
                'anúncio', 'campanha', 'tiktok', 'instagram', 'facebook',
                'meta ads', 'google ads', 'público-alvo', 'copy', 'gatilho',
                'conversão', 'tráfego', 'leads', 'remarketing'
            ],
            automacao: [
                'automatizar', 'automação', 'bot', 'chatbot', 'webhook',
                'api', 'cron', 'atendimento', 'pedido automático', 'stock',
                'integração', 'notificação', 'rastreamento'
            ]
        };

        console.log('🧠 Orquestrador iniciado — 4 skills carregadas.');
    }

    // -------------------------------------------------
    // MÉTODO PRINCIPAL: Recebe um comando e processa
    // -------------------------------------------------
    async executar(comando) {
        console.log(`\n📥 Comando recebido: "${comando}"`);

        // 1. Identificar qual skill deve responder
        const skillIdentificada = this.identificarSkill(comando);

        if (!skillIdentificada) {
            return this._criarResposta('erro', 'orquestrador', null,
                'Não foi possível identificar a skill adequada para este comando.',
                null
            );
        }

        console.log(`🎯 Skill identificada: ${skillIdentificada}`);

        // 2. Delegar a tarefa para a skill correcta
        const skill = this.skills[skillIdentificada];
        const resultado = await skill.executar(comando);

        // 3. Registar no histórico
        this._registarHistorico(comando, skillIdentificada, resultado);

        // 4. Verificar se há próximo passo (fluxo multi-skill)
        if (resultado.proximo_passo) {
            console.log(`➡️  Próximo passo identificado: ${resultado.proximo_passo}`);
            this.filaTarefas.push({
                skill: resultado.proximo_passo,
                dados: resultado.dados,
                origem: skillIdentificada
            });
        }

        // 5. Retornar resultado ao utilizador
        return resultado;
    }

    // -------------------------------------------------
    // FLUXO COMPLETO: Executa cadeia de skills
    // -------------------------------------------------
    // Exemplo: Pesquisar produtos → Criar página → Marketing
    async executarFluxo(etapas) {
        console.log(`\n🔁 Iniciando fluxo com ${etapas.length} etapas...`);
        const resultados = [];

        for (let i = 0; i < etapas.length; i++) {
            const etapa = etapas[i];
            console.log(`\n--- Etapa ${i + 1}/${etapas.length}: ${etapa.skill} ---`);

            const skill = this.skills[etapa.skill];
            if (!skill) {
                resultados.push(this._criarResposta('erro', etapa.skill, null,
                    `Skill "${etapa.skill}" não encontrada.`, null));
                break;
            }

            // Passa dados da etapa anterior como contexto
            const contexto = resultados.length > 0
                ? resultados[resultados.length - 1].dados
                : null;

            const resultado = await skill.executar(etapa.comando, contexto);
            resultados.push(resultado);

            this._registarHistorico(etapa.comando, etapa.skill, resultado);

            // Se uma etapa falhou, parar o fluxo
            if (resultado.status === 'erro') {
                console.log(`❌ Fluxo interrompido na etapa ${i + 1}`);
                break;
            }
        }

        return {
            status: resultados.every(r => r.status === 'sucesso') ? 'sucesso' : 'parcial',
            skill: 'orquestrador',
            total_etapas: etapas.length,
            etapas_concluidas: resultados.filter(r => r.status === 'sucesso').length,
            resultados: resultados
        };
    }

    // -------------------------------------------------
    // IDENTIFICAR SKILL: Analisa o comando e descobre
    // qual skill deve ser activada
    // -------------------------------------------------
    identificarSkill(comando) {
        const comandoLower = comando.toLowerCase();
        let melhorSkill = null;
        let maiorPontuacao = 0;

        for (const [skill, palavras] of Object.entries(this.roteamento)) {
            let pontuacao = 0;

            for (const palavra of palavras) {
                if (comandoLower.includes(palavra.toLowerCase())) {
                    pontuacao += 1;
                }
            }

            if (pontuacao > maiorPontuacao) {
                maiorPontuacao = pontuacao;
                melhorSkill = skill;
            }
        }

        return melhorSkill;
    }

    // -------------------------------------------------
    // PROCESSAR FILA: Executa tarefas pendentes
    // -------------------------------------------------
    async processarFila() {
        while (this.filaTarefas.length > 0) {
            const tarefa = this.filaTarefas.shift();
            console.log(`📋 Processando tarefa da fila: ${tarefa.skill}`);

            const skill = this.skills[tarefa.skill];
            if (skill) {
                const resultado = await skill.executar(
                    `Continuar a partir de ${tarefa.origem}`,
                    tarefa.dados
                );
                this._registarHistorico(`auto:${tarefa.skill}`, tarefa.skill, resultado);

                if (resultado.proximo_passo) {
                    this.filaTarefas.push({
                        skill: resultado.proximo_passo,
                        dados: resultado.dados,
                        origem: tarefa.skill
                    });
                }
            }
        }
    }

    // -------------------------------------------------
    // STATUS: Ver o estado actual do sistema
    // -------------------------------------------------
    getStatus() {
        const status = {};
        for (const [nome, skill] of Object.entries(this.skills)) {
            status[nome] = {
                nome: skill.nome,
                activa: skill.activa || true,
                totalExecucoes: this.historico.filter(h => h.skill === nome).length
            };
        }

        return {
            skills: status,
            totalOperacoes: this.historico.length,
            tarefasPendentes: this.filaTarefas.length
        };
    }

    // -------------------------------------------------
    // HELPERS PRIVADOS
    // -------------------------------------------------
    _criarResposta(status, skill, dados, mensagem, proximoPasso) {
        return {
            status: status,
            skill: skill,
            dados: dados,
            mensagem: mensagem,
            proximo_passo: proximoPasso,
            timestamp: new Date().toISOString()
        };
    }

    _registarHistorico(comando, skill, resultado) {
        this.historico.push({
            comando: comando,
            skill: skill,
            status: resultado.status,
            timestamp: new Date().toISOString()
        });
    }
}

export { Orquestrador };
