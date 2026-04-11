// =====================================================
// LOGGER — Sistema de logging centralizado
// =====================================================
// Substitui console.log por logs estruturados com níveis,
// timestamps e contexto de agente.
// =====================================================

import { config } from './config.js';

const LEVELS = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
    silent: 99,
};

const ICONS = {
    debug: '🔍',
    info: 'ℹ️',
    warn: '⚠️',
    error: '❌',
};

const COLORS = {
    debug: '\x1b[90m',   // cinza
    info: '\x1b[36m',    // ciano
    warn: '\x1b[33m',    // amarelo
    error: '\x1b[31m',   // vermelho
    reset: '\x1b[0m',
    bold: '\x1b[1m',
};

class Logger {
    constructor(context = 'sistema') {
        this.context = context;
        this.level = LEVELS[config.logLevel] ?? LEVELS.info;
    }

    _format(level, msg, data) {
        const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
        const icon = ICONS[level] || '';
        const color = COLORS[level] || '';
        const reset = COLORS.reset;

        let line = `${color}[${ts}] ${icon} [${this.context}] ${msg}${reset}`;

        if (data !== undefined) {
            const extra = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
            line += `\n${color}${extra}${reset}`;
        }

        return line;
    }

    debug(msg, data) {
        if (this.level <= LEVELS.debug) {
            console.log(this._format('debug', msg, data));
        }
    }

    info(msg, data) {
        if (this.level <= LEVELS.info) {
            console.log(this._format('info', msg, data));
        }
    }

    warn(msg, data) {
        if (this.level <= LEVELS.warn) {
            console.warn(this._format('warn', msg, data));
        }
    }

    error(msg, data) {
        if (this.level <= LEVELS.error) {
            console.error(this._format('error', msg, data));
        }
    }

    // Log de sucesso (sempre visível se info está ativo)
    ok(msg, data) {
        if (this.level <= LEVELS.info) {
            const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
            let line = `\x1b[32m[${ts}] ✅ [${this.context}] ${msg}\x1b[0m`;
            if (data !== undefined) {
                line += `\n\x1b[32m${JSON.stringify(data, null, 2)}\x1b[0m`;
            }
            console.log(line);
        }
    }

    // Criar sub-logger com contexto filho
    child(subContext) {
        return new Logger(`${this.context}:${subContext}`);
    }
}

// Logger padrão do sistema
const logger = new Logger('sistema');

// Factory para agentes
function criarLogger(nomeAgente) {
    return new Logger(nomeAgente);
}

export { Logger, logger, criarLogger };
export default logger;
