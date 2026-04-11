// =====================================================
// MANAGER DE AGENTES — Orquestra múltiplos agentes autônomos
// =====================================================
// Responsabilidades:
// - Gerenciar ciclo de vida de todos os agentes
// - Coordinar comunicação entre agentes
// - Monitorar saúde do sistema
// - Executar scheduling das tarefas
// =====================================================

import { EventEmitter } from 'events';
import fs from 'fs/promises';
import path from 'path';
import { config } from './config.js';

class ManagerAgentes extends EventEmitter {
    constructor() {
        super();
        this.agentes = new Map();
        this.timers = new Map();
        this.eventosPendentes = [];
        this.arquivoEventos = path.join(config.paths.data, 'eventos.json');
    }

    // Registrar um novo agente no sistema
    registrar(agente) {
        if (this.agentes.has(agente.id)) {
            throw new Error(`Agente ${agente.id} já está registrado`);
        }

        this.agentes.set(agente.id, agente);
        
        // Forward events from agent to manager
        agente.on('notificacao', (notificacao) => {
            this._distribuirNotificacao(notificacao);
        });

        agente.on('tarefa_concluida', (resultado) => {
            this.emit('agente_tarefa_concluida', resultado);
            this._processarResultado(resultado);
        });

        agente.on('tarefa_erro', (erro) => {
            this.emit('agente_tarefa_erro', erro);
        });

        console.log(`✅ Agente registrado: ${agente.nome} (${agente.id})`);
    }

    // Inicializar todos os agentes
    async inicializarTodos() {
        console.log('\n🚀 Inicializando sistema de agentes...\n');
        
        for (const [id, agente] of this.agentes) {
            try {
                await agente.inicializar();
            } catch (erro) {
                console.error(`❌ Falha ao inicializar ${id}: ${erro.message}`);
            }
        }

        await this._carregarEventosPendentes();
        console.log('\n✨ Sistema de agentes pronto\n');
    }

    // Iniciar execução automática de todos os agentes
    iniciarTodos() {
        for (const [id, agente] of this.agentes) {
            this._agendarAgente(agente);
        }
        console.log(`⏰ ${this.agentes.size} agentes agendados`);
    }

    // Parar todos os agentes
    pararTodos() {
        for (const [id, timer] of this.timers) {
            clearTimeout(timer);
        }
        this.timers.clear();
        console.log('🛑 Todos os agentes parados');
    }

    // Executar agente específico imediatamente
    async executarAgente(id) {
        const agente = this.agentes.get(id);
        if (!agente) {
            throw new Error(`Agente ${id} não encontrado`);
        }
        return await agente.executar();
    }

    // Agendar execução contínua de um agente
    _agendarAgente(agente) {
        const executarCiclo = async () => {
            try {
                await agente.executar();
            } catch (erro) {
                console.error(`❌ Erro em ${agente.id}: ${erro.message}`);
            }

            // Reagendar
            const delayMs = agente.intervaloMinutos * 60000;
            const timer = setTimeout(executarCiclo, delayMs);
            this.timers.set(agente.id, timer);
        };

        // Primeira execução
        executarCiclo();
    }

    // Distribuir notificações entre agentes (comunicação inter-agentes)
    _distribuirNotificacao(notificacao) {
        // Salvar para persistência
        this._salvarEvento(notificacao);

        // Notificar agentes interessados
        for (const [id, agente] of this.agentes) {
            if (id !== notificacao.origem) {
                // Agente decide internamente se quer processar
                agente.emit('notificacao_recebida', notificacao);
            }
        }

        this.emit('notificacao_global', notificacao);
    }

    // Processar resultado de tarefa e trigger ações em cascata
    _processarResultado(resultado) {
        const { id, acoes } = resultado;
        
        // Exemplo: Se agente de produtos adicionou produtos,
        // notificar agente de site para criar páginas
        if (id === 'produtos' && resultado.acoes?.includes('produtos_adicionados')) {
            const agenteSite = this.agentes.get('shopify');
            if (agenteSite) {
                agenteSite.emit('notificacao_recebida', {
                    origem: 'produtos',
                    evento: 'novos_produtos_disponiveis',
                    dados: resultado.dados,
                    timestamp: new Date().toISOString()
                });
            }
        }
    }

    // Persistência de eventos
    async _salvarEvento(evento) {
        this.eventosPendentes.push(evento);
        if (this.eventosPendentes.length > 1000) {
            this.eventosPendentes = this.eventosPendentes.slice(-500);
        }

        try {
            await fs.writeFile(this.arquivoEventos, JSON.stringify(this.eventosPendentes, null, 2));
        } catch (erro) {
            console.error('Falha ao salvar eventos:', erro.message);
        }
    }

    async _carregarEventosPendentes() {
        try {
            const dados = await fs.readFile(this.arquivoEventos, 'utf8');
            this.eventosPendentes = JSON.parse(dados);
            console.log(`📨 ${this.eventosPendentes.length} eventos carregados`);
        } catch {
            // Arquivo não existe
        }
    }

    // Relatório de status de todos os agentes
    getStatusCompleto() {
        const status = {
            timestamp: new Date().toISOString(),
            totalAgentes: this.agentes.size,
            agentesAtivos: Array.from(this.agentes.values()).filter(a => a.status === 'pronto' || a.status === 'executando').length,
            agentes: Array.from(this.agentes.values()).map(a => a.getResumo())
        };
        return status;
    }

    // Exportar relatório para arquivo
    async exportarRelatorio() {
        const status = this.getStatusCompleto();
        const arquivo = path.join(config.paths.relatorios, `status-${Date.now()}.json`);
        
        await fs.mkdir(path.dirname(arquivo), { recursive: true });
        await fs.writeFile(arquivo, JSON.stringify(status, null, 2));
        
        return arquivo;
    }
}

export { ManagerAgentes };
