// =====================================================
// AGENTE BASE — Gadget Hub (wrapper + auto-inject DB)
// =====================================================
// Re-exporta a classe do shared com auto-injeção da
// database do Gadget Hub. Retrocompatibilidade total.
// =====================================================

import { AgenteBase as SharedAgenteBase } from '../../../shared/core/agente-base.js';
import { getDatabase } from './database.js';

class AgenteBase extends SharedAgenteBase {
    constructor(config) {
        // Auto-injetar database se não foi passado
        if (!config.db) {
            config.db = getDatabase();
        }
        super(config);
    }
}

export { AgenteBase };
