# Guia - Conectar Dominio GoDaddy ao Shopify

> **Dominio:** gadget-hub.com
> **Registador:** GoDaddy
> **Plataforma:** Shopify
> **Data:** Abril 2026

---

## Pre-requisitos

- [x] Dominio gadget-hub.com comprado no GoDaddy
- [ ] Loja Shopify criada (plano Basic ou superior)

---

## OPCAO A - Conectar via Shopify (Recomendado)

Este e o metodo mais simples. O Shopify guia-te em tudo.

### Passo 1: Adicionar dominio no Shopify

1. Acede ao **Shopify Admin** (admin.shopify.com)
2. Vai a **Configuracoes** > **Dominios**
3. Clica em **Conectar dominio existente**
4. Escreve `gadget-hub.com` e clica **Seguinte**
5. O Shopify vai mostrar os registos DNS que precisas configurar:
   - **Registo A:** `23.227.38.65`
   - **CNAME (www):** `shops.myshopify.com`

### Passo 2: Configurar DNS no GoDaddy

1. Abre o **GoDaddy** e faz login
2. Vai a **Meus Produtos** > **DNS** (ao lado do teu dominio)
3. Na seccao de **Registos DNS**, faz o seguinte:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | `23.227.38.65` | 600 segundos |
| CNAME | www | `shops.myshopify.com` | 1 hora |

**Para editar o registo A:**
- Encontra o registo A existente com nome `@`
- Clica no icone de editar (lapis)
- Altera o valor para `23.227.38.65`
- Guarda

**Para adicionar/editar o CNAME:**
- Encontra o registo CNAME com nome `www` (ou clica Adicionar)
- Altera o valor para `shops.myshopify.com`
- Guarda

**Importante:** Se existir "Forwarding" ou "Parking" activo no GoDaddy, desactiva-o primeiro. Isto pode interferir com a conexao.

### Passo 3: Verificar no Shopify

1. Volta ao **Shopify Admin** > **Configuracoes** > **Dominios**
2. Clica em **Verificar conexao**
3. Se os DNS ja propagaram, o estado muda para **Conectado**
4. O **certificado SSL (HTTPS)** e activado automaticamente pelo Shopify

> **Nota:** A propagacao DNS pode demorar entre 15 minutos a 48 horas. Se nao funcionar imediatamente, espera e tenta novamente mais tarde.

### Passo 4: Definir como dominio principal

1. Em **Configuracoes** > **Dominios**, clica em `gadget-hub.com`
2. Clica em **Definir como dominio principal**
3. Isto garante que `tua-loja.myshopify.com` redireciona para `gadget-hub.com`

---

## OPCAO B - Transferir dominio para Shopify

Se preferires gerir tudo num so sitio, podes transferir o dominio do GoDaddy para o Shopify.

1. No GoDaddy: **Meus Produtos** > **Dominios** > desbloquear dominio
2. Obter o **codigo de autorizacao** (EPP code) no GoDaddy
3. No Shopify: **Configuracoes** > **Dominios** > **Transferir dominio**
4. Inserir `gadget-hub.com` e colar o codigo de autorizacao
5. Pagar a taxa de transferencia (normalmente ~14 USD/ano)

> **Nota:** A transferencia pode demorar 5-7 dias. A Opcao A (conectar sem transferir) e mais rapida e funciona igualmente bem.

---

## Verificacao Final

### Como saber se tudo esta a funcionar

Apos configurar o DNS, verifica o seguinte:

| Teste | Como verificar | Resultado esperado |
|-------|---------------|-------------------|
| DNS propagado | Acede a `gadget-hub.com` no browser | Mostra a tua loja Shopify |
| HTTPS activo | Verifica se aparece o cadeado na barra de endereco | Conexao segura (HTTPS) |
| Redirect www | Acede a `www.gadget-hub.com` | Redireciona para `gadget-hub.com` |
| Dominio principal | Acede a `tua-loja.myshopify.com` | Redireciona para `gadget-hub.com` |

### Verificar DNS via terminal (opcional)

```bash
# Verificar registo A
nslookup gadget-hub.com

# Resultado esperado: Address: 23.227.38.65

# Verificar CNAME
nslookup www.gadget-hub.com

# Resultado esperado: shops.myshopify.com
```

---

## Problemas Comuns

| Problema | Solucao |
|----------|---------|
| "DNS nao verificado" no Shopify | Espera ate 48h para propagacao DNS |
| Erro de SSL / HTTPS | O Shopify gera o certificado automaticamente. Espera ate 48h |
| Pagina de parking do GoDaddy aparece | Desactiva o forwarding/parking no painel DNS do GoDaddy |
| www nao funciona | Confirma que o CNAME `www` aponta para `shops.myshopify.com` |

---

## Checklist

- [ ] Registo A configurado no GoDaddy (`23.227.38.65`)
- [ ] CNAME www configurado (`shops.myshopify.com`)
- [ ] Forwarding/parking desactivado no GoDaddy
- [ ] Dominio verificado no Shopify
- [ ] SSL/HTTPS activo
- [ ] gadget-hub.com definido como dominio principal
- [ ] Redirect www -> dominio principal a funcionar
- [ ] Loja acessivel via gadget-hub.com

---

## Proximos Passos

Apos o dominio estar conectado:
1. Importar produtos via CJ Dropshipping (ver `GUIA-APIs-E-PAGAMENTOS.md`)
2. Configurar pagamentos: Shopify Payments, MBWay, PayPal
3. Testar fluxo completo de compra
