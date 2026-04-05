// =====================================================
// SKILL 3 — MARKETING
// =====================================================

class SkillMarketing {
    constructor() {
        this.nome = 'Marketing';
        this.id = 'marketing';
        this.activa = true;
        this.canais = {
            tiktok: { nome: 'TikTok Ads', activo: true, orcamentoDiario: 10, formato: 'video curto' },
            meta: { nome: 'Meta Ads (Instagram/Facebook)', activo: true, orcamentoDiario: 10, formato: 'imagem + carrossel' },
            google: { nome: 'Google Ads', activo: false, orcamentoDiario: 0, formato: 'search + shopping' }
        };
        this.gatilhos = {
            escassez: ['Ultimas {n} unidades!', 'So hoje com este preco!'],
            urgencia: ['Oferta termina em {tempo}!', 'Promocao relampago!'],
            provaSocial: ['{n} pessoas compraram este produto', 'Avaliacao {score}/5'],
            autoridade: ['Curado pela nossa equipa', 'Score de qualidade: {score}/100']
        };
    }

    async executar(comando, contexto = null) {
        console.log('Skill 3 activada: ' + comando);
        try {
            if (contexto && contexto.produtos) {
                const estrategias = contexto.produtos.map(p => this.gerarEstrategia(p));
                return { status: 'sucesso', skill: this.id, dados: { estrategias, total: estrategias.length, canais_activos: Object.values(this.canais).filter(c => c.activo).map(c => c.nome) }, proximo_passo: 'automacao', timestamp: new Date().toISOString() };
            }
            return { status: 'sucesso', skill: this.id, dados: { canais: this.canais, gatilhos: this.gatilhos }, proximo_passo: null, timestamp: new Date().toISOString() };
        } catch (erro) {
            return { status: 'erro', skill: this.id, dados: null, mensagem: erro.message, proximo_passo: null, timestamp: new Date().toISOString() };
        }
    }

    gerarEstrategia(produto) {
        const margem = parseFloat(produto.margem) || 50;
        const orcamentoDiario = margem > 60 ? 20 : 10;
        return {
            produto: produto.nome,
            score: produto.score,
            orcamentoDiario,
            canaisPrioritarios: margem > 60 ? ['tiktok', 'meta'] : ['tiktok'],
            copy: this.gerarCopy(produto),
            hashtags: this.gerarHashtags(produto.categoria)
        };
    }

    gerarCopy(produto) {
        return {
            tiktok: produto.nome + ' — entrega rapida! Compra agora em gadget-hub.com',
            meta: produto.nome + ' com avaliacao ' + produto.avaliacao + '/5. Frete gratis!',
            google: 'Comprar ' + produto.nome + ' | Melhor preco | Gadget Hub'
        };
    }

    gerarHashtags(categoria) {
        const tags = { 'smart-home': ['#casainteligente', '#smarthome', '#gadgets'], 'audio': ['#fones', '#bluetooth', '#musica'], 'acessorios': ['#acessorios', '#tech', '#gadget'], 'eletronicos': ['#eletronicos', '#tecnologia', '#tech'] };
        return tags[categoria] || ['#gadgethub', '#tech', '#shopping'];
    }
}

export { SkillMarketing };
