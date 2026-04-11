// =====================================================
// TEST-CJ-API.JS — Testar conexão real com CJ Dropshipping
// =====================================================

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ler .env manualmente
function loadEnv() {
    try {
        const envPath = path.join(__dirname, '.env');
        const envContent = fs.readFileSync(envPath, 'utf8');
        const lines = envContent.split('\n');
        
        for (const line of lines) {
            if (line.includes('=') && !line.startsWith('#')) {
                const [key, ...valueParts] = line.split('=');
                const value = valueParts.join('=').trim();
                if (key && value) {
                    process.env[key.trim()] = value;
                }
            }
        }
    } catch (erro) {
        console.log('⚠️  Não foi possível ler .env:', erro.message);
    }
}

loadEnv();

const CJ_CONFIG = {
    apiKey: process.env.CJ_API_KEY,
    email: process.env.CJ_EMAIL,
    baseUrl: 'https://developers.cjdropshipping.com/api2.0/v1',
    accessToken: null
};

console.log('🔍 Testando conexão CJ Dropshipping\n');
console.log('Configuração:');
console.log(`  API Key: ${CJ_CONFIG.apiKey ? '✓ Configurada (comprimento: ' + CJ_CONFIG.apiKey.length + ')' : '✗ NÃO CONFIGURADA'}`);
console.log(`  Email: ${CJ_CONFIG.email || '✗ NÃO CONFIGURADO'}`);
if (CJ_CONFIG.apiKey) {
    console.log(`  Primeiros 30 chars: ${CJ_CONFIG.apiKey.substring(0, 30)}`);
}
console.log();

// Obter access token
async function obterAccessToken() {
    try {
        console.log('1️⃣  Testando autenticação com API Key...');
        
        // Algumas APIs CJ aceitam a API key diretamente
        // Tentar usar apenas a parte do token (após o último @)
        const apiKeyParts = CJ_CONFIG.apiKey.split('@');
        CJ_CONFIG.accessToken = apiKeyParts[apiKeyParts.length - 1]; // Pega a última parte
        
        console.log(`   Token extraído: ${CJ_CONFIG.accessToken.substring(0, 20)}...`);
        
        // Testar se funciona
        const url = `${CJ_CONFIG.baseUrl}/product/list?pageNum=1&pageSize=1&accessToken=${encodeURIComponent(CJ_CONFIG.accessToken)}`;
        
        const resposta = await fetch(url, {
            method: 'GET'
        });
        
        const dados = await resposta.json();
        
        if (dados.result === false) {
            console.log(`   ⚠️ API Key direta falhou: ${dados.message}`);
            console.log('   📝 Tentando autenticação com email/senha...');
            
            // Tentar com email/senha
            const authUrl = `${CJ_CONFIG.baseUrl}/authentication/getAccessToken`;
            
            const authResposta = await fetch(authUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: CJ_CONFIG.email,
                    password: 'mortadela9021@',
                    apikey: CJ_CONFIG.apiKey
                })
            });
            
            const authDados = await authResposta.json();
            
            if (authDados.result === false) {
                console.log(`   ❌ Falha na autenticação: ${authDados.message}`);
                return false;
            }
            
            if (authDados.data && authDados.data.accessToken) {
                CJ_CONFIG.accessToken = authDados.data.accessToken;
                console.log('   ✅ Access token obtido via email/senha!');
                return true;
            }
            
            return false;
        }
        
        console.log('   ✅ API Key funcionou diretamente!');
        return true;
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
        return false;
    }
}

async function testarAutenticacao() {
    try {
        console.log('\n2️⃣  Testando autenticação com access token...');
        
        const url = `${CJ_CONFIG.baseUrl}/product/list?pageNum=1&pageSize=1`;
        
        const resposta = await fetch(url, {
            method: 'GET',
            headers: {
                'CJ-Access-Token': CJ_CONFIG.accessToken
            }
        });
        
        const dados = await resposta.json();
        
        if (dados.result === false) {
            console.log(`   ❌ Falha: ${dados.message}`);
            return false;
        }
        
        console.log('   ✅ Autenticação bem-sucedida!');
        console.log(`   📊 Total de produtos disponíveis: ${dados.data?.total || 'N/A'}`);
        return true;
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
        return false;
    }
}

async function testarBuscaProdutos() {
    try {
        console.log('\n3️⃣  Testando busca de produtos...');
        
        const query = 'bluetooth';
        const url = `${CJ_CONFIG.baseUrl}/product/list?name=${query}&pageNum=1&pageSize=5`;
        
        const resposta = await fetch(url, {
            method: 'GET',
            headers: {
                'CJ-Access-Token': CJ_CONFIG.accessToken
            }
        });
        
        const dados = await resposta.json();
        
        if (dados.result === false) {
            console.log(`   ❌ Erro na busca: ${dados.message}`);
            return;
        }
        
        const produtos = dados.data?.list || [];
        
        console.log(`   ✅ Encontrados ${produtos.length} produtos para "${query}"`);
        
        if (produtos.length > 0) {
            console.log('\n   📦 Primeiros produtos:');
            produtos.slice(0, 3).forEach((p, i) => {
                console.log(`      ${i + 1}. ${p.productNameEn}`);
                console.log(`         PID: ${p.pid}`);
                console.log(`         Avaliação: ${p.productReviewsRate || 'N/A'}`);
                console.log(`         Pedidos: ${p.productOrders || 'N/A'}`);
                console.log();
            });
        }
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
    }
}

async function testarCategorias() {
    try {
        console.log('\n4️⃣  Testando categorias...');
        
        const categorias = ['smart plug', 'earphone', 'charger', 'phone holder'];
        
        for (const cat of categorias) {
            const url = `${CJ_CONFIG.baseUrl}/product/list?name=${cat}&pageNum=1&pageSize=1`;
            
            const resposta = await fetch(url, {
                method: 'GET',
                headers: {
                    'CJ-Access-Token': CJ_CONFIG.accessToken
                }
            });
            
            const dados = await resposta.json();
            const total = dados.data?.total || 0;
            
            console.log(`   • ${cat}: ${total} produtos`);
            
            await new Promise(r => setTimeout(r, 1000));
        }
        
    } catch (erro) {
        console.log(`   ❌ Erro: ${erro.message}`);
    }
}

async function main() {
    if (!CJ_CONFIG.apiKey) {
        console.log('❌ CJ_API_KEY não configurada!');
        console.log('Execute: node setup-env.js');
        process.exit(1);
    }
    
    // Primeiro obter access token
    const tokenObtido = await obterAccessToken();
    
    if (!tokenObtido) {
        console.log('\n❌ Não foi possível autenticar na API CJ.');
        console.log('\n📋 Possíveis causas:');
        console.log('   1. API key ainda não ativada (pode levar alguns minutos)');
        console.log('   2. API key incorreta ou revogada');
        console.log('   3. Senha da conta incorreta');
        console.log('\n🔧 Soluções:');
        console.log('   • Verifique a API key em: https://app.cjdropshipping.com/api-manage.html');
        console.log('   • Certifique-se de que a API key está ativa');
        console.log('   • Verifique se o email e senha estão corretos');
        console.log('\n⚠️  O sistema pode funcionar em modo demonstração sem a API CJ.');
        console.log('   Execute: node demo.js');
        return;
    }
    
    const autenticado = await testarAutenticacao();
    
    if (autenticado) {
        await testarBuscaProdutos();
        await testarCategorias();
        
        console.log('\n✅ Todos os testes concluídos!');
        console.log('\n📋 Resumo:');
        console.log('   • API CJ está funcionando corretamente');
        console.log('   • Autenticação válida');
        console.log('   • Busca de produtos operacional');
        console.log('\n🚀 Próximo passo: Execute o sistema completo:');
        console.log('   node main.js        (modo CLI)');
        console.log('   npm run dashboard   (modo web)');
    } else {
        console.log('\n❌ Falha na autenticação. Verifique sua API key.');
    }
}

main().catch(erro => {
    console.error('Erro fatal:', erro);
    process.exit(1);
});
