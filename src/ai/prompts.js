// =====================================================
// PROMPTS — Templates de prompt para o LLM
// =====================================================
// Cada função retorna um prompt formatado para um caso
// de uso específico do sistema Gadget Hub.
// =====================================================

const SYSTEM_PROMPT = `Tu és o assistente AI do Gadget Hub, uma loja de dropshipping de gadgets e eletrónica em Portugal.
Responde sempre em português europeu. Sê direto, prático e focado em e-commerce.
A loja usa Shopify, CJ Dropshipping, e gera renders 3D com Blender.`;

// =====================================================
// PRODUTOS
// =====================================================

function promptAnalisarProduto(produto) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Analisa este produto para a loja Gadget Hub:

Nome: ${produto.nome}
Categoria: ${produto.categoria}
Preço CJ: ${produto.precoCJ || 'N/A'}€
Preço Venda: ${produto.precoVenda || 'N/A'}€
Avaliação: ${produto.avaliacao || 'N/A'}/5

Responde em JSON com:
{
  "recomendacao": "aprovar" | "rejeitar" | "revisar",
  "score": 0-100,
  "motivo": "...",
  "tituloSEO": "título optimizado para SEO",
  "descricaoSEO": "meta description optimizada",
  "tags": ["tag1", "tag2", ...],
  "precoProposto": número
}`
    };
}

function promptGerarDescricao(produto) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Gera uma descrição de produto para a Shopify em português europeu:

Produto: ${produto.nome}
Categoria: ${produto.categoria}
Características: ${produto.caracteristicas || 'gadget electrónico'}

A descrição deve ter:
- Título apelativo (H1)
- 2-3 parágrafos com benefícios (não features)
- Lista de especificações
- Call-to-action final
- Tom: moderno, tech-savvy, direto

Formato: HTML simples (h1, p, ul, li, strong)`
    };
}

// =====================================================
// MARKETING
// =====================================================

function promptGerarCopy(produto, plataforma) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Gera copy de anúncio para ${plataforma}:

Produto: ${produto.nome}
Preço: ${produto.precoVenda}€
Categoria: ${produto.categoria}
Público: Portugal, 18-45 anos, tech enthusiasts

Requisitos por plataforma:
- TikTok: max 100 chars, casual, emojis, hashtags
- Instagram: max 2200 chars, visual, hashtags (20-30)
- Facebook: max 500 chars, informativo, link
- Google: título max 30 chars + descrição max 90 chars

Responde em JSON:
{
  "titulo": "...",
  "corpo": "...",
  "cta": "...",
  "hashtags": ["...", "..."]
}`
    };
}

function promptAnalisarCampanha(metricas) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Analisa estas métricas de campanha e sugere optimizações:

Plataforma: ${metricas.plataforma}
Gasto: ${metricas.gasto}€
Impressões: ${metricas.impressoes}
Cliques: ${metricas.cliques}
Conversões: ${metricas.conversoes}
ROAS: ${metricas.roas}
CTR: ${metricas.ctr}%

Responde em JSON:
{
  "performance": "boa" | "média" | "má",
  "acoes": ["ação 1", "ação 2"],
  "orcamentoSugerido": número,
  "continuar": true/false,
  "motivo": "..."
}`
    };
}

// =====================================================
// PREÇOS
// =====================================================

function promptAnalisarPreco(produto, concorrentes) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Analisa o pricing deste produto:

Produto: ${produto.nome}
Custo CJ: ${produto.precoCJ}€
Preço Atual: ${produto.precoVenda}€
Margem Atual: ${produto.margem || 'N/A'}%

Concorrentes:
${concorrentes.map(c => `- ${c.nome}: ${c.preco}€`).join('\n')}

Responde em JSON:
{
  "precoRecomendado": número,
  "precoCompare": número (preço "riscado"),
  "margemEstimada": número em %,
  "estrategia": "premium" | "competitivo" | "penetracao",
  "motivo": "..."
}`
    };
}

// =====================================================
// SUPORTE / CHATBOT
// =====================================================

function promptResponderCliente(pergunta, contexto = {}) {
    return {
        sistema: `${SYSTEM_PROMPT}
Estás a responder a um cliente da loja. Sê simpático, claro e resolve o problema.
Se não souberes a resposta, sugere contactar suporte@gadget-hub.com.`,
        prompt: `Pergunta do cliente: "${pergunta}"

${contexto.pedido ? `Pedido: #${contexto.pedido.id} — Status: ${contexto.pedido.status}` : ''}
${contexto.produto ? `Produto: ${contexto.produto.nome}` : ''}

Responde de forma concisa e útil em português europeu.`
    };
}

// =====================================================
// COMANDOS NATURAIS (para o router)
// =====================================================

function promptClassificarComando(texto) {
    return {
        sistema: SYSTEM_PROMPT,
        prompt: `Classifica este comando do operador da loja:

"${texto}"

Responde APENAS com JSON:
{
  "intencao": "status" | "executar_agente" | "adicionar_produto" | "ajustar_preco" | "criar_campanha" | "gerar_render" | "consultar_faq" | "relatorio" | "outro",
  "agente": "shopify" | "cj" | "precos" | "marketing" | "estoque" | "blender" | "automacao" | null,
  "parametros": { ... },
  "confianca": 0-100
}`
    };
}

export {
    SYSTEM_PROMPT,
    promptAnalisarProduto,
    promptGerarDescricao,
    promptGerarCopy,
    promptAnalisarCampanha,
    promptAnalisarPreco,
    promptResponderCliente,
    promptClassificarComando,
};
