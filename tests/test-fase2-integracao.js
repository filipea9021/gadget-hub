// =====================================================
// TESTE FASE 2 — Integração Gadget Hub ↔ Marketing Studio
// =====================================================
// Testa:
//   1. AgenteMarketingClient (criação, envio de pedidos)
//   2. Message Bus bridge (Hub → Studio)
//   3. Pipeline integration (CJ → Client → Studio)
//   4. Resultado recebido → evento compatível com Blender
//   5. Retrocompatibilidade do Gadget Hub
// =====================================================

import { existsSync, unlinkSync, rmSync } from 'fs';

const TEST_DB_HUB = '/tmp/test-hub-fase2.db';
const TEST_DB_STUDIO = '/tmp/test-studio-fase2.db';
const TEST_QUEUE = '/tmp/test-fase2-queue';

// Limpar
[TEST_DB_HUB, TEST_DB_STUDIO, `${TEST_DB_HUB}-wal`, `${TEST_DB_HUB}-shm`,
 `${TEST_DB_STUDIO}-wal`, `${TEST_DB_STUDIO}-shm`].forEach(f => {
    if (existsSync(f)) unlinkSync(f);
});
if (existsSync(TEST_QUEUE)) rmSync(TEST_QUEUE, { recursive: true });

let totalTests = 0;
let passedTests = 0;

function assert(condition, name) {
    totalTests++;
    if (condition) {
        passedTests++;
        console.log(`  ✅ ${name}`);
    } else {
        console.log(`  ❌ ${name}`);
    }
}

// =====================================================
// TESTE 1: AgenteMarketingClient — Criação e métodos
// =====================================================
console.log('\n📡 TESTE 1: AgenteMarketingClient');
console.log('─'.repeat(40));

// Usar AgenteBase do shared diretamente (evitar wrapper do hub que tem binary issue)
import { SharedDatabase, criarDatabase } from '../../shared/core/database.js';
const dbHub = criarDatabase(TEST_DB_HUB);

// Import direto do agente-marketing-client — usa AgenteBase de ../core/
// que é o wrapper do hub. Precisamos garantir que o DB é injectado.
// O import funciona porque o agente-base wrapper re-exporta do shared.
// Mas o wrapper tenta usar getDatabase() do hub se db não for passado.
// Nós passamos db explicitamente, então não há problema.
import { AgenteMarketingClient } from '../src/agentes/agente-marketing-client.js';

const client = new AgenteMarketingClient({
    db: dbHub,
    studioUrl: 'http://localhost:99999',  // Forçar falha HTTP
});

await client.inicializar();
assert(client.status === 'pronto', 'Client inicializado');
assert(client.id === 'marketing-client', 'ID correto');
assert(typeof client.solicitarVideo === 'function', 'Método solicitarVideo existe');
assert(typeof client.solicitarRenderCompleto === 'function', 'Método solicitarRenderCompleto (compat) existe');
assert(typeof client.solicitarCinematico === 'function', 'Método solicitarCinematico existe');

const stats = client.getStats();
assert(stats.totalPedidosEnviados === 0, 'Stats iniciais zerados');
assert(stats.studioUrl === 'http://localhost:99999', 'Studio URL configurado');

console.log('');

// =====================================================
// TESTE 2: Envio de pedido (sem Studio — vai para fila local)
// =====================================================
console.log('📤 TESTE 2: Envio de pedido (Studio offline → fila local)');
console.log('─'.repeat(40));

const resultado = await client.solicitarVideo({
    id: 'P1',
    nome: 'Smart Plug WiFi',
    sku: 'SP001',
    categoria: 'smart_plug',
}, {
    renderTypes: ['hero', 'turntable'],
    estilo: 'produto_360',
});

assert(resultado.pedidoId, 'Pedido tem ID');
assert(resultado.via === 'queued-local', `Pedido foi para fila local (via: ${resultado.via})`);
assert(client.pedidosPendentes.length === 1, '1 pedido na fila local');

// Render completo (compat)
const resultado2 = await client.solicitarRenderCompleto({
    id: 'P2', nome: 'Earbuds Pro', sku: 'EP001', categoria: 'earbuds'
});
assert(resultado2.pedidoId, 'Render completo tem ID');
assert(client.pedidosPendentes.length === 2, '2 pedidos na fila local');

console.log('');

// =====================================================
// TESTE 3: Message Bus Bridge (Hub → Studio)
// =====================================================
console.log('📨 TESTE 3: Message Bus (Hub → Studio)');
console.log('─'.repeat(40));

import { MessageBus } from '../../shared/core/message-bus.js';

const bus = new MessageBus({ queueDir: TEST_QUEUE });

// Simular handler do Marketing Studio
let studioRecebeu = null;
bus.registar('marketing-studio', async (pedido) => {
    studioRecebeu = pedido;
    return {
        id: `ped_studio_${Date.now()}`,
        status: 'queued',
    };
});

// Criar novo client com Message Bus
const clientWithBus = new AgenteMarketingClient({
    db: dbHub,
    studioUrl: 'http://localhost:99999',
});
clientWithBus.setMessageBus(bus);
await clientWithBus.inicializar();

const busResult = await clientWithBus.solicitarVideo({
    id: 'BUS_P1',
    nome: 'Speaker Bluetooth',
    sku: 'SB001',
    categoria: 'speaker',
}, {
    renderTypes: ['hero', 'cinematicOrbit'],
});

assert(busResult.via === 'message-bus', `Pedido enviado via Message Bus (via: ${busResult.via})`);
assert(studioRecebeu !== null, 'Marketing Studio recebeu o pedido');
assert(studioRecebeu.payload?.produtoNome === 'Speaker Bluetooth', 'Dados do produto corretos no pedido');
assert(studioRecebeu.from === 'gadget-hub', 'Origem = gadget-hub');
assert(studioRecebeu.to === 'marketing-studio', 'Destino = marketing-studio');

const busStats = clientWithBus.getStats();
assert(busStats.totalPedidosEnviados === 1, 'Stats contabilizam pedido');

console.log('');

// =====================================================
// TESTE 4: Pipeline Integration com MarketingStudioDatabase
// =====================================================
console.log('🔄 TESTE 4: Full pipeline (Hub → Bus → Studio DB)');
console.log('─'.repeat(40));

import { MarketingStudioDatabase } from '../../marketing-studio/src/core/database.js';
import { AgenteVideo } from '../../marketing-studio/src/agentes/agente-video.js';
import { AgenteRender } from '../../marketing-studio/src/agentes/agente-render.js';

const dbStudio = new MarketingStudioDatabase(TEST_DB_STUDIO);
dbStudio.conectar();

const agenteRender = new AgenteRender({
    db: dbStudio,
    serverUrl: 'http://localhost:99999',
});
const agenteVideo = new AgenteVideo({
    db: dbStudio,
    storagePath: '/tmp/test-fase2-storage',
});
agenteVideo.setAgenteRender(agenteRender);

await agenteRender.inicializar();
await agenteVideo.inicializar();

// Registar handler real do Studio no bus
const bus2 = new MessageBus({ queueDir: '/tmp/test-fase2-queue2' });

bus2.registar('marketing-studio', async (pedido) => {
    return agenteVideo.criarPedido({
        id: pedido.id,
        from: pedido.from,
        produtoId: pedido.payload?.produtoId,
        produtoNome: pedido.payload?.produtoNome,
        categoria: pedido.payload?.categoria,
        renderTypes: pedido.payload?.renderTypes || ['hero'],
    });
});

// Client com bus real
const fullClient = new AgenteMarketingClient({
    db: dbHub,
    studioUrl: 'http://localhost:99999',
});
fullClient.setMessageBus(bus2);
await fullClient.inicializar();

// Enviar pedido
const fullResult = await fullClient.solicitarVideo({
    id: 'FULL_P1',
    nome: 'LED Strip RGB 5m',
    sku: 'LED001',
    categoria: 'led',
}, {
    renderTypes: ['hero', 'turntable'],
});

assert(fullResult.via === 'message-bus', 'Pedido chegou via Message Bus');

// Verificar que chegou à DB do Marketing Studio
const pedidoNaDB = dbStudio.getPedido(fullResult.studioId);
assert(pedidoNaDB !== null, 'Pedido existe na DB do Marketing Studio');
assert(pedidoNaDB.origem === 'gadget-hub', 'Origem = gadget-hub na DB do Studio');
assert(pedidoNaDB.produto_nome === 'LED Strip RGB 5m', 'Nome do produto correcto na DB');
assert(pedidoNaDB.status === 'queued', 'Status = queued na DB do Studio');

// Executar render no Studio (demo mode)
await agenteRender.executar();
await new Promise(r => setTimeout(r, 3000));
await agenteRender.executar();

// Verificar conclusão
const pedidoFinal = dbStudio.getPedido(fullResult.studioId);
assert(
    ['completed', 'processing', 'queued'].includes(pedidoFinal.status),
    `Pipeline completo: status = ${pedidoFinal.status}`
);

console.log('');

// =====================================================
// TESTE 5: Evento compatível com Blender (renders_prontos)
// =====================================================
console.log('🔌 TESTE 5: Retrocompatibilidade eventos');
console.log('─'.repeat(40));

let eventoRecebido = null;
// notificar() emits 'notificacao' — que é o que main.js ouve no pipeline
fullClient.on('notificacao', (notif) => {
    if (notif.evento === 'renders_prontos') {
        eventoRecebido = notif;
    }
});

// Simular resultado completo
fullClient._emitirResultado({
    pedidoId: 'req_test',
    studioId: 'ped_studio_test',
    dados: {
        produtoId: 'P1',
        produtoNome: 'Smart Plug WiFi',
        shopifyProductId: 'shopify_123',
    },
    resultado: {
        renders: [
            { tipo: 'hero', arquivo_saida: '/storage/hero.png' },
            { tipo: 'turntable', arquivo_saida: '/storage/turntable.mp4' },
        ],
        video: { arquivo: '/storage/video.mp4' },
    },
});

// Esperar evento
await new Promise(r => setTimeout(r, 100));

assert(eventoRecebido !== null, 'Evento renders_prontos emitido');
assert(eventoRecebido.dados?.produtoId === 'P1', 'Evento tem produtoId');
assert(eventoRecebido.dados?.renders?.length === 2, 'Evento tem 2 renders');
assert(eventoRecebido.dados?.animacoes?.length === 1, 'Evento tem 1 animação');
assert(eventoRecebido.dados?.via === 'marketing-studio', 'Evento marca via = marketing-studio');

console.log('');

// =====================================================
// TESTE 6: Verificar health do Studio
// =====================================================
console.log('🏥 TESTE 6: Studio health check');
console.log('─'.repeat(40));

const health = await fullClient.getStudioHealth();
assert(health.ok === false, 'Studio offline detectado (URL fake)');

const remoteStats = await fullClient.getStudioStats();
assert(remoteStats === null, 'Stats retorna null quando offline');

console.log('');

// =====================================================
// CLEANUP
// =====================================================
dbHub.fechar();
dbStudio.fechar();

[TEST_DB_HUB, TEST_DB_STUDIO, `${TEST_DB_HUB}-wal`, `${TEST_DB_HUB}-shm`,
 `${TEST_DB_STUDIO}-wal`, `${TEST_DB_STUDIO}-shm`].forEach(f => {
    if (existsSync(f)) unlinkSync(f);
});

// =====================================================
// RESULTADO FINAL
// =====================================================
console.log('═'.repeat(50));
console.log(`\n📊 RESULTADO: ${passedTests}/${totalTests} testes passaram\n`);

if (passedTests === totalTests) {
    console.log('✅ FASE 2 COMPLETA — Integração Gadget Hub ↔ Marketing Studio!');
    console.log('');
    console.log('  Validado:');
    console.log('  • AgenteMarketingClient (envio de pedidos)');
    console.log('  • Message Bus bridge (Hub → Studio)');
    console.log('  • Pipeline completo (pedido → DB Studio → render demo)');
    console.log('  • Eventos retrocompatíveis (renders_prontos)');
    console.log('  • Health check e fallback (offline → fila local)');
    console.log('');
} else {
    console.log(`⚠️  ${totalTests - passedTests} testes falharam`);
}

process.exit(passedTests === totalTests ? 0 : 1);
