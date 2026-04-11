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
        this.skills = {
            pesquisa_produtos: new SkillPesquisaProdutos(),
            criacao_site: new SkillCriacaoSite(),
            marketing: new SkillMarketing(),
            automacao: new SkillAutomacao()
        };
        this.historico = [];
        this.filaTarefas = [];
        this.roteamento = {
            pesquisa_produtos: ['produto', 'pesquisar', 'encontrar', 'catálogo', 'fornecedor', 'aliexpress', 'cj dropshipping', 'zendrop', 'validar produto', 'margem', 'avaliação', 'score', 'nicho'],
            criacao_site: ['site', 'página', 'layout', 'componente', 'design', 'frontend', 'backend', 'checkout', 'carrinho', 'mobile', 'responsivo', 'código', 'html', 'css', 'javascript'],
            marketing: ['anúncio', 'campanha', 'tiktok', 'instagram', 'facebook', 'meta ads', 'google ads', 'público-alvo', 'copy', 'gatilho', 'conversão', 'tráfego', 'leads', 'remarketing'],
            automacao: ['automatizar', 'automação', 'bot', 'chatbot', 'webhook', 'api', 'cron', 'atendimento', 'pedido automático', 'stock', 'integração', 'notificação', 'rastreamento']
        };
        console.log('🧠 Orquestrador iniciado — 4 skills carregadas.');
    }

    async executar(comando) {
        console.log(`\n📥 Comando recebido: "${comando}"`);
        const skillIdentificada = this.identificarSkill(comando);
        if (!skillIdentificada) {
            return this._criarResposta('erro', 'orquestrador', null, 'Não foi possível identificar a skill adequada para este comando.', null);
        }
        console.log(`🎯 Skill identificada: ${skillIdentificada}`);
        const skill = this.skills[skillIdentificada];
        const resultado = await skill.executar(comando);
        this._registarHistorico(comando, skillIdentificada, resultado);
        if (resultado.proximo_passo) {
            this.filaTarefas.push({ skill: resultado.proximo_passo, dados: resultado.dados, origem: skillIdentificada });
        }
        return resultado;
    }

    async executarFluxo(etapas) {
        console.log(`\n🔁 Iniciando fluxo com ${etapas.length} etapas...`);
        const resultados = [];
        for (let i = 0; i < etapas.length; i++) {
            const etapa = etapas[i];
            const skill = this.skills[etapa.skill];
            if (!skill) { resultados.push(this._criarResposta('erro', etapa.skill, null, `Skill "${etapa.skill}" não encontrada.`, null)); break; }
            const contexto = resultados.length > 0 ? resultados[resultados.length - 1].dados : null;
            const resultado = await skill.executar(etapa.comando, contexto);
            resultados.push(resultado);
            this._registarHistorico(etapa.comando, etapa.skill, resultado);
            if (resultado.status === 'erro') break;
        }
        return { status: resultados.every(r => r.status === 'sucesso') ? 'sucesso' : 'parcial', skill: 'orquestrador', total_etapas: etapas.length, etapas_concluidas: resultados.filter(r => r.status === 'sucesso').length, resultados };
    }

    identificarSkill(comando) {
        const comandoLower = comando.toLowerCase();
        let melhorSkill = null;
        let maiorPontuacao = 0;
        for (const [skill, palavras] of Object.entries(this.roteamento)) {
            let pontuacao = 0;
            for (const palavra of palavras) { if (comandoLower.includes(palavra.toLowerCase())) pontuacao += 1; }
            if (pontuacao > maiorPontuacao) { maiorPontuacao = pontuacao; melhorSkill = skill; }
        }
        return melhorSkill;
    }

    getStatus() {
        const status = {};
        for (const [nome, skill] of Object.entries(this.skills)) {
            status[nome] = { nome: skill.nome, activa: true, totalExecucoes: this.historico.filter(h => h.skill === nome).length };
        }
        return { skills: status, totalOperacoes: this.historico.length, tarefasPendentes: this.filaTarefas.length };
    }

    _criarResposta(status, skill, dados, mensagem, proximoPasso) {
        return { status, skill, dados, mensagem, proximo_passo: proximoPasso, timestamp: new Date().toISOString() };
    }

    _registarHistorico(comando, skill, resultado) {
        this.historico.push({ comando, skill, status: resultado.status, timestamp: new Date().toISOString() });
    }
}

export { Orquestrador };
