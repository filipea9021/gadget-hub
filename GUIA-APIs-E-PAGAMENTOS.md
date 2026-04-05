# Guia de Configuracao - APIs de Fornecedores + Pagamentos no Shopify

## Visao Geral da Arquitetura

Como o site vai rodar no Shopify, a estrutura fica muito mais simples.
O Shopify ja tem loja de apps com integracoes directas para fornecedores e pagamentos.

## PARTE A - Fornecedor: CJ Dropshipping

Tu ja tens conta no CJ. Agora e ligar ao Shopify.

Passo 1: Instalar a App do CJ no Shopify
- Acede ao painel do Shopify > Apps > Shopify App Store
- Pesquisa por "CJ Dropshipping"
- Clica em Instalar e autoriza a conexao
- Faz login com a tua conta CJ existente

Passo 2: Importar produtos
-> Na app CJ, vai a Produtos
-> Usa filtros: Avaliacao 4+, Armazens Europa
-> Clica "Adicionar a lista" e "Publicar na loja"

Passo 3: Fluxo automatico de pedidos
- Cliente compra > pedido aparece no Shopify E na app CJ
- CJ processa e envia o produto
- Codigo de rastreamento enviado automaticamente

## PARTE B - Pagamentos no Shopify

Shopify Payments (Cartoes):
1. Shopify Admin > Configuracoes > Pagamentos
2. Clica "Activar Shopify Payments"
3. Preenche NIF, IBAN, morada
4. Apos verificacoes (1-2 dias), ja aceitas cartoes

MBWay (EuPago ou ifthenpay):
1. Shopify App Store > pesquisa "EuPago" ou "ifthenpay"
2. Instalar a app e criar conta
3. Activar MBWay e Multibanco

PayPal:
1. Shopify Admin > Configuracoes > Pagamentos
2. Seccao "Pagamentos adicionais" > PayPal
3. Ligar conta PayPal Business

## Checklist de Contas

- [x] CJ Dropshipping (ja tens)
- [ ] Loja Shopify (Basic ~39 EU/mes)
- [ ] EuPago ou ifthenpay (MBWay + Multibanco)
- [ ] PayPal Business

## Ordem de Configuracao

| Passo | Tarefa | Tempo |
|-------|--------|-------|
| 1 | Criar loja Shopify | 1-2 h |
| 2 | Instalar app CJ Dropshipping | 15 min |
| 3 | Importar produtos | 1 h |
| 4 | Activar Shopify Payments | 30 min |
| 5 | Activar MBWay (EuPago) | 1-2 dias |
| 6 | Ligar PayPal | 15 min |
| 7 | Testar fluxo completo | 30 min |
