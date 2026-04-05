// =====================================================
// APP.JS — ARQUIVO PRINCIPAL DO SISTEMA
// =====================================================
// Este arquivo integra o Orquestrador com todas as Skills.
// É o ponto de entrada para testar e usar o sistema completo.
// =====================================================

import { Orquestrador } from './orquestrador.js';

// -------------------------------------------------
// INICIALIZAR O SISTEMA
// -------------------------------------------------
const sistema = new Orquestrador();

// -------------------------------------------------
// EXEMPLOS DE USO
// -------------------------------------------------

// EXEMPLO 1: Comando simples — o orquestrador detecta a skill
async function exemploComandoSimples() {
    console.log('=== EXEMPLO 1: Comando Simples ===');

    // O orquestrador vai identificar que é Skill 1 (Pesquisa de Produtos)
    const resultado = await sistema.executar('Pesquisar produtos de headset gamer com boa avaliação');
    console.log('Resultado:', JSON.stringify(resultado, null, 2));
}

// EXEMPLO 2: Fluxo completo — cadeia de skills
async function exemploFluxoCompleto() {
    console.log('\n=== EXEMPLO 2: Fluxo Completo ===');

    const resultado = await sistema.executarFluxo([
        {
            skill: 'pesquisa_produtos',
            comando: 'Encontrar melhores produtos de periféricos gamer'
        },
        {
            skill: 'criacao_site',
            comando: 'Criar páginas para os produtos encontrados'
        },
        {
            skill: 'marketing',
            comando: 'Gerar estratégia de marketing para os produtos'
        },
        {
            skill: 'automacao',
            comando: 'Configurar automações para os pedidos'
        }
    ]);

    console.log('Fluxo concluído:', JSON.stringify(resultado, null, 2));
}

// EXEMPLO 3: Verificar status do sistema
function exemploStatus() {
    console.log('\n=== EXEMPLO 3: Status do Sistema ===');
    const status = sistema.getStatus();
    console.log('Status:', JSON.stringify(status, null, 2));
}

// EXEMPLO 4: Chatbot automático
async function exemploChatbot() {
    console.log('\n=== EXEMPLO 4: Chatbot ===');

    const perguntas = [
        'Qual o prazo de entrega?',
        'Como faço para rastreamento do meu pedido?',
        'Quero fazer devolução do produto'
    ];

    for (const pergunta of perguntas) {
        const resultado = await sistema.executar(pergunta);
        console.log(`\nPergunta: "${pergunta}"`);
        console.log(`Resposta: ${resultado.dados?.resposta || 'Sem resposta automática'}`);
    }
}

// -------------------------------------------------
// EXECUTAR (descomente o exemplo que quiser testar)
// -------------------------------------------------
// exemploComandoSimples();
// exemploFluxoCompleto();
// exemploStatus();
// exemploChatbot();

// -------------------------------------------------
// EXPORTAR para uso externo
// -------------------------------------------------
export { sistema };
