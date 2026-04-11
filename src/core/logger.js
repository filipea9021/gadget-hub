// =====================================================
// LOGGER — Gadget Hub (re-export do shared)
// =====================================================
// Retrocompatibilidade: todos os imports existentes
// continuam a funcionar sem alteração.
// =====================================================

export { Logger, logger, criarLogger } from '../../../shared/core/logger.js';
import logger from '../../../shared/core/logger.js';
export default logger;
