// =====================================================
// SKILL 3 — MARKETING 📢
// =====================================================
// Responsável EXCLUSIVAMENTE pela estratégia de aquisição
// e retenção de clientes. NÃO cria site. NÃO busca produtos.
// Canais: TikTok Ads, Meta Ads, Google Ads.
// =====================================================

class SkillMarketing {
    constructor() {
        this.nome = 'Marketing';
        this.id = 'marketing';
        this.activa = true;

        // Canais de marketing configurados
        this.canais = {
            tiktok: {
                nome: 'TikTok Ads',
                activo: true,
                orcamentoDiario: 20,    // R$ por dia
                formato: 'vídeo curto'
            },
            meta: {
                nome: 'Meta Ads (Instagram/Facebook)',
                activo: true,
                orcamentoDiario: 30,
                formato: 'imagem + carrossel'
            },
            google: {
                nome: 'Google Ads',
                activo: false,           // Activar depois
                orcamentoDiario: 0,
                formato: 'search + shopping'
            }
        };

        // Gatilhos mentais disponíveis
        this.gatilhos = {
            escassez: {
                nome: 'Escassez',
                exemplos: [
                    'Últimas {n} unidades!',
                    'Só hoje com este preço!',
                    'Stock limitado — {n} restantes'
                ]
            },
            urgencia: {
                nome: 'Urgência',
                exemplos: [
                    'Oferta termina em {tempo}!',
                    'Promoção relâmpago — corre!',
                    'Desconto válido só até meia-noite'
                ]
            },
            provaSocial: {
                nome: 'Prova Social',
                exemplos: [
                    '{n} pessoas compraram este produto',
                    'Avaliação {score}/5 por {n} clientes',
                    'O mais vendido da semana'
                ]
            },
            autoridade: {
                nome: 'Autoridade',
                exemplos: [
                    'Curado pela nossa equipa de especialistas',
                    'Score de qualidade: {score}/100',
                    'Produto verificado pela TechZone'
                ]
            }
        };
    }

    // -------------------------------------------------
    // EXECUTAR: Ponto de entrada da skill
    // -------------------------------------------------
    async executar(comando, contexto = null) {
        console.log(`📢 Skill 3 activada: ${comando}`);

        try {
            // Se recebeu dados do site/produtos, gerar estratégia de marketing
            if (contexto && contexto.paginas_geradas) {
                const estrategia = this.gerarEstrategia(contexto.paginas_geradas);
                return {
                    status: 'sucesso',
                    skill: this.id,
                    dados: estrategia,
                    proximo_passo: 'automacao',
                    timestamp: new Date().toISOString()
                };
            }

            // Caso contrário, retornar configuração actual
            return {
                status: 'sucesso',
                skill: this.id,
                dados: {
                    canais: this.canais,
                    gatilhos: Object.keys(this.gatilhos),
                    orcamento_total_diario: this.calcularOrcamentoTotal()
                },
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        } catch (erro) {
            return {
                status: 'erro',
                skill: this.id,
                dados: null,
                mensagem: `Erro no marketing: ${erro.message}`,
                proximo_passo: null,
                timestamp: new Date().toISOString()
            };
        }
    }

    // -------------------------------------------------
    // ESTRATÉGIA: Gerar plano de marketing para produtos
    // -------------------------------------------------
    gerarEstrategia(paginas) {
        const campanhas = paginas.map(pagina => ({
            produto: pagina.nome,
            canais: ['tiktok', 'meta'],
            copy: this.gerarCopy(pagina),
            publicoAlvo: this.definirPublico(pagina),
            gatilhos: this.selecionarGatilhos(pagina),
            orcamento: {
                diario: 25,
                semanal: 175,
                mensal: 750
            }
        }));

        return {
            total_campanhas: campanhas.length,
            campanhas: campanhas,
            orcamento_total_mensal: campanhas.reduce((sum, c) => sum + c.orcamento.mensal, 0)
        };
    }

    // -------------------------------------------------
    // COPY: Gerar texto para anúncios
    // -------------------------------------------------
    gerarCopy(pagina) {
        return {
            titulo: `${pagina.nome} — Qualidade Garantida`,
            descricao: `Score ${pagina.dados.score}/100 | Entrega em até ${pagina.dados.tempoEntrega} dias | TechZone`,
            cta: 'Comprar Agora',
            hashtags: ['#TechZone', '#GamerSetup', '#TechDeals', '#Gaming']
        };
    }

    // -------------------------------------------------
    // PÚBLICO: Definir público-alvo para cada produto
    // -------------------------------------------------
    definirPublico(pagina) {
        const publicos = {
            perifericos: {
                idade: '18-35',
                interesses: ['gaming', 'tecnologia', 'PC gaming', 'setup gamer'],
                genero: 'todos'
            },
            consoles: {
                idade: '16-40',
                interesses: ['videogames', 'PlayStation', 'Xbox', 'Nintendo'],
                genero: 'todos'
            },
            acessorios: {
                idade: '18-45',
                interesses: ['tecnologia', 'gadgets', 'produtividade', 'streaming'],
                genero: 'todos'
            },
            games: {
                idade: '16-35',
                interesses: ['jogos digitais', 'gaming', 'e-sports', 'streaming'],
                genero: 'todos'
            }
        };

        return publicos[pagina.dados.categoria] || publicos.perifericos;
    }

    // -------------------------------------------------
    // GATILHOS: Selecionar gatilhos para o produto
    // -------------------------------------------------
    selecionarGatilhos(pagina) {
        const gatilhosSelecionados = [];

        // Sempre usar prova social se tiver score
        if (pagina.dados.score) {
            gatilhosSelecionados.push({
                tipo: 'provaSocial',
                texto: `Score de qualidade: ${pagina.dados.score}/100`
            });
        }

        // Urgência para preços altos
        if (pagina.dados.preco > 150) {
            gatilhosSelecionados.push({
                tipo: 'urgencia',
                texto: 'Promoção por tempo limitado!'
            });
        }

        // Escassez como padrão
        gatilhosSelecionados.push({
            tipo: 'escassez',
            texto: 'Stock limitado — garanta o seu!'
        });

        return gatilhosSelecionados;
    }

    // -------------------------------------------------
    // HELPER: Calcular orçamento total diário
    // -------------------------------------------------
    calcularOrcamentoTotal() {
        return Object.values(this.canais)
            .filter(c => c.activo)
            .reduce((sum, canal) => sum + canal.orcamentoDiario, 0);
    }
}

export { SkillMarketing };
