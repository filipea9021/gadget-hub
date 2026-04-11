// =====================================================
// AGENTE BASE — Classe abstrata para todos os agentes
// =====================================================
// Cada agente opera de forma autônoma com:
// - Estado persistente (SQLite)
// - Scheduling de execuções
// - Comunicação via eventos
// - Logs estruturados no banco
// =====================================================

import { EventEmitter } from 'events';
import { getDatabase } from './database.js';

class AgenteBase extends EventEmitter {
    constructor(config) {
        super();
        this.id = config.id;
        this.nome = config.nome;
        this.descricao = config.descricao;
        this.intervaloMinutos = config.intervaloMinutos || 60;
        this.ultimaExecucao = null;
        this.proximaExecucao = null;
        this.status = 'parado';
        this.historico = [];
        this.maxHistorico = 100;
        this.db = null;
    }

    // Inicializa o agente carregando estado anterior do SQLite
    async inicializar() {
        try {
            this.db = await getDatabase();
            const estado = await this.db.carregarEstadoAgente(this.id);
            
            if (estado) {
                this.ultimaExecucao = estado.ultima_execucao;
                this.proximaExecucao = estado.proxima_execucao;
                this.historico = estado.historico || [];
                this.intervaloMinutos = estado.configuracao?.intervalo_minutos || this.intervaloMinutos;
                this.status = estado.status === 'executando' ? 'parado' : estado.status;
            }
            
            // Salvar estado inicial
            await this.db.salvarEstadoAgente(this);
            
            this.status = 'pronto';
            this._log('info', `Agente ${this.nome} inicializado`);
            this.emit('inicializado', { id: this.id, timestamp: new Date().toISOString() });
            return true;
        } catch (erro) {
            this.status = 'erro';
            this._log('erro', `Falha na inicialização: ${erro.message}`);
            return false;
        }
    }

    // Ciclo de vida principal do agente
    async executar() {
        if (this.status === 'executando') {
            this._log('aviso', 'Execução ignorada - agente já está processando');
            return;
        }

        this.status = 'executando';
        this.ultimaExecucao = new Date().toISOString();
        this._log('info', 'Iniciando ciclo de execução');

        try {
            const resultado = await this._tarefa();
            
            this.historico.unshift({
                timestamp: this.ultimaExecucao,
                status: resultado.sucesso ? 'sucesso' : 'erro',
                acoes: resultado.acoes || [],
                mensagem: resultado.mensagem
            });

            if (this.historico.length > this.maxHistorico) {
                this.historico = this.historico.slice(0, this.maxHistorico);
            }

            this.status = resultado.sucesso ? 'pronto' : 'erro';
            
            if (resultado.sucesso) {
                this.emit('tarefa_concluida', { id: this.id, resultado });
            } else {
                this.emit('tarefa_erro', { id: this.id, erro: resultado.mensagem });
            }

            await this._salvarEstado();
            
            // Agendar próxima execução
            this.proximaExecucao = new Date(Date.now() + this.intervaloMinutos * 60000).toISOString();
            
            // Persistir no SQLite
            await this.db.salvarEstadoAgente(this);
            
            return resultado;

        } catch (erro) {
            this.status = 'erro';
            this._log('erro', `Exceção não tratada: ${erro.message}`);
            this.emit('tarefa_erro', { id: this.id, erro: erro.message });
            if (this.db) await this.db.salvarEstadoAgente(this);
            throw erro;
        }
    }

    // Método abstrato - cada agente implementa sua lógica específica
    async _tarefa() {
        throw new Error('Método _tarefa deve ser implementado pelo agente específico');
    }

    // Comunicação com outros agentes via eventos
    notificar(evento, dados) {
        this.emit('notificacao', {
            origem: this.id,
            evento,
            dados,
            timestamp: new Date().toISOString()
        });
    }

    // Receber notificações de outros agentes
    onNotificacao(callback) {
        this.on('notificacao_recebida', callback);
    }

    // Logging estruturado no SQLite
    async _log(nivel, mensagem, dados = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [${this.id}] [${nivel.toUpperCase()}] ${mensagem}`);
        
        if (this.db) {
            await this.db.adicionarLog(this.id, nivel, mensagem, dados);
        }
    }

    // Métodos de persistência removidos - agora usam SQLite diretamente
    async _salvarEstado() {
        if (this.db) {
            await this.db.salvarEstadoAgente(this);
        }
    }

    async _carregarEstado() {
        if (this.db) {
            return await this.db.carregarEstadoAgente(this.id);
        }
        return null;
    }

    // Utilitários para requisições HTTP com retry
    async fetchComRetry(url, options = {}, maxTentativas = 3) {
        for (let tentativa = 1; tentativa <= maxTentativas; tentativa++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (erro) {
                this._log('aviso', `Tentativa ${tentativa}/${maxTentativas} falhou: ${erro.message}`);
                
                if (tentativa === maxTentativas) {
                    throw erro;
                }
                
                // Exponential backoff
                await new Promise(r => setTimeout(r, Math.pow(2, tentativa) * 1000));
            }
        }
    }

    getResumo() {
        return {
            id: this.id,
            nome: this.nome,
            descricao: this.descricao,
            status: this.status,
            ultimaExecucao: this.ultimaExecucao,
            proximaExecucao: this.proximaExecucao,
            totalExecucoes: this.historico.length,
            ultimasAcoes: this.historico.slice(0, 5)
        };
    }
}

export { AgenteBase };
