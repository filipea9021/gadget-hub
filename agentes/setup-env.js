// =====================================================
// SETUP-ENV.JS — Configurar ambiente com credenciais CJ
// =====================================================
// Execute: node setup-env.js
// =====================================================

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envContent = `# Gadget Hub — Configuração de Ambiente
# Gerado automaticamente em ${new Date().toISOString()}

# =====================================================
# MODO DE OPERAÇÃO
# =====================================================
# manual    = Execução sob demanda
# semi      = Recomendado - sugere ações, aguarda confirmação
# autonomo  = Totalmente autônomo
MODO=semi

# =====================================================
# SHOPIFY API - OBRIGATÓRIO
# =====================================================
# Como obter:
# 1. https://admin.shopify.com/store/SUALOJA/apps
# 2. "Develop apps" → "Create an app"
# 3. Configure: read_products, write_products, read_orders
# 4. "Install app" → Copie "Admin API access token"
#
SHOPIFY_SHOP_DOMAIN=gadget-hub.myshopify.com
SHOPIFY_ACCESS_TOKEN=
SHOPIFY_API_VERSION=2024-01

# =====================================================
# CJ DROPSHIPPING API - CONFIGURADO ✓
# =====================================================
CJ_API_KEY=CJ5298786@api@7ca4cd0efbda4ba491c0496638cc3d6b
CJ_EMAIL=filipeazevedo791@gmail.com

# =====================================================
# DASHBOARD
# =====================================================
DASHBOARD_PORT=3001

# =====================================================
# NOTIFICAÇÕES - OPCIONAL
# =====================================================
WEBHOOK_URL=
NOTIFICATION_EMAIL=admin@gadget-hub.com

# =====================================================
# MARKETING - FUTURO
# =====================================================
META_ACCESS_TOKEN=
TIKTOK_ACCESS_TOKEN=

# =====================================================
# LOGGING
# =====================================================
LOG_LEVEL=info
`;

const envPath = path.join(__dirname, '.env');

try {
    fs.writeFileSync(envPath, envContent);
    console.log('✅ Arquivo .env criado com sucesso!');
    console.log('\n📋 Configuração atual:');
    console.log('   • CJ API Key: Configurada ✓');
    console.log('   • CJ Email: filipeazevedo791@gmail.com');
    console.log('   • Modo: semi');
    console.log('\n⚠️  Próximo passo: Configure SHOPIFY_ACCESS_TOKEN no .env');
    console.log('   (ou deixe em branco para testar apenas CJ)');
} catch (erro) {
    console.error('❌ Erro ao criar .env:', erro.message);
}
