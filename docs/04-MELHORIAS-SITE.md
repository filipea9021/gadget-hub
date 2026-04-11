# Documento de Melhorias do Site - Gadget Hub

**Documento Estratégico de Optimização do E-commerce**

Data: Abril 2026
Versão: 1.0
Linguagem: Português Europeu (PT-PT)
Plataforma: Shopify

---

## ÍNDICE

1. [Parte 1: Melhorias da Homepage](#parte-1-melhorias-da-homepage)
2. [Parte 2: Páginas a Criar](#parte-2-páginas-a-criar)
3. [Parte 3: SEO & Performance](#parte-3-seo--performance)
4. [Parte 4: Sinais de Confiança](#parte-4-sinais-de-confiança)
5. [Parte 5: Matriz de Prioridades](#parte-5-matriz-de-prioridades)

---

## PARTE 1: MELHORIAS DA HOMEPAGE

### 1.1 Categorias em Destaque com Ícones

**Descrição:**
Implementar uma secção visual com as principais categorias de produtos, acompanhadas por ícones intuitivos e imagens de fundo optimizadas.

**Categorias Sugeridas:**
- Smartphones & Acessórios (ícone: telemóvel)
- Tablets & E-readers (ícone: tablet)
- Wearables & Smartwatches (ícone: relógio inteligente)
- Auriculares & Áudio (ícone: auscultadores)
- Câmaras & Fotografia (ícone: câmara)
- Acessórios de Computador (ícone: computador)
- Casa Inteligente (ícone: casa)
- Gaming & Consolas (ícone: joystick)
- Carregadores & Cabos (ícone: raio)
- Protetores & Cases (ícone: escudo)

**Implementação:**
- Grid responsivo (4 colunas em desktop, 2 em tablet, 1 em mobile)
- Imagens de 600x400px otimizadas em WebP
- Ícones SVG consistentes com a marca
- Efeito hover com zoom subtil (1.05x)
- Links diretos para páginas de categoria

---

### 1.2 Countdown de Promoções / Ofertas Limitadas

**Descrição:**
Implementar um banner de promoção com contador regressivo visual para criar urgência e incentivar conversões.

**Especificações:**
- **Localização:** Topo da página, abaixo do cabeçalho principal
- **Design:** Fundo degradado com cores de marca, texto em contraste
- **Contador:** HH:MM:SS em tempo real
- **Mensagem Sugerida:** "Promoção Flash! Desconto de XX% termina em [contador]"
- **Comportamento:**
  - Atualiza a cada segundo
  - Som subtil (opcional) quando restam menos de 10 minutos
  - Efeito visual pulsante quando o tempo está a acabar
  - Desaparece automaticamente quando o countdown termina

**Integração:**
- Controlado via painel administrativo Shopify
- Facilmente ativável/desativável
- Suporta múltiplas campanhas
- Rastreamento de cliques para análise de conversão

---

### 1.3 Secção "Mais Vendidos" e "Novidades"

**Descrição:**
Duas secções principais destacando produtos populares e novas chegadas.

**"Mais Vendidos":**
- Exibe os 8-12 produtos com maior volume de vendas nos últimos 30 dias
- Atualização automática diária
- Badge "Mais Vendido" no canto superior da imagem do produto
- Ordenação por vendas em tempo real

**"Novidades":**
- Exibe produtos adicionados nos últimos 14 dias
- Badge "Novo" com data de chegada
- Destaque especial com fundo subtil
- Link "Ver Todos os Novos Produtos"

**Design Recomendado:**
- Layout Slider (carousel) responsivo
- 4 produtos visíveis simultaneamente em desktop
- Botões de navegação (anterior/próximo)
- Indicadores de página (dots)
- Autoplay com pausa ao passar o rato

**Informações por Produto:**
- Imagem de alta qualidade (600x600px mínimo)
- Preço com possível preço riscado (se em promoção)
- Classificação/rating (estrelas)
- Número de reviews
- Botão "Adicionar ao Carrinho"
- Link rápido para a ficha do produto

---

### 1.4 Secção "Vistos Recentemente"

**Descrição:**
Mostrar aos utilizadores os produtos que visualizaram anteriormente para facilitar o regresso e aumentar a conversão.

**Funcionamento:**
- Rastreia até 10 produtos visualizados nos últimos 7 dias
- Armazena dados em localStorage (dispositivo local)
- Exibe apenas a utilizadores com histórico de navegação
- Desaparece se não houver produtos anteriormente vistos
- Respeitador de privacidade (sem rastreamento externo)

**Design:**
- Secção discreta no footer ou sidebar
- Máximo 5 produtos vistos mais recentemente
- Atualização em tempo real
- Botão "Limpar Histórico" (opcional)
- Ícone de relógio para identificar a secção

---

### 1.5 Barra de Benefícios

**Descrição:**
Banner com os principais benefícios e garantias da Gadget Hub para reforçar confiança e diferenciação.

**Benefícios Principais:**

| Benefício | Descrição | Ícone |
|-----------|-----------|-------|
| Envio Grátis | Envio gratuito para encomendas superiores a 50€ | 📦 |
| Devoluções | Devolução sem problemas em até 14 dias | ↩️ |
| Suporte 24h | Suporte ao cliente disponível 24 horas por dia, 7 dias por semana | 💬 |
| Pagamento Seguro | Transações 100% seguras com encriptação SSL | 🔒 |

**Implementação:**
- **Posição:** Abaixo do herói principal, antes das categorias
- **Layout:** Barra horizontal com 4 ícones + texto
- **Responsividade:** Stack verticalmente em mobile
- **Animação:** Ícones com pequena animação ao carregar
- **Cores:** Consistentes com identidade visual de marca

---

## PARTE 2: PÁGINAS A CRIAR

### 2.1 Página "Sobre Nós"

**URL:** `/pages/sobre-nos`
**Template:** Page (Página Estática)

---

#### Conteúdo Completo:

# Sobre a Gadget Hub

## A Nossa História

Bem-vindo à **Gadget Hub**, a sua loja online de confiança para gadgets e tecnologia inteligente em Portugal.

A Gadget Hub foi fundada com uma missão simples mas ambiciosa: tornar a tecnologia de ponta acessível a todos os portugueses. Acreditamos que não é necessário gastar uma fortuna para ter acesso aos melhores gadgets do mercado.

Começámos como uma pequena startup em Lisboa, com uma equipa apaixonada por tecnologia e inovação. Após anos de dedicação, crescemos para nos tornarmos uma das lojas online mais respeitadas e confiáveis do país. Hoje, servimos dezenas de milhares de clientes felizes em toda Portugal.

## O Que Nos Diferencia

Na Gadget Hub, não somos apenas um intermediário entre você e os seus gadgets favoritos. Somos parceiros no seu percurso digital.

### Paixão pela Tecnologia
Cada membro da nossa equipa é um entusiasta de tecnologia. Testamos pessoalmente os produtos que vendemos, e apenas oferecemos aqueles que realmente acreditamos que valem a pena.

### Acessibilidade
Acreditamos que a melhor tecnologia não deve ser privilégio de poucos. Por isso, oferecemos preços competitivos, promoções regulares e um programa de fidelização que recompensa os nossos clientes leais.

### Transparência Total
Listamos as especificações completas de cada produto, incluindo avaliações honestas e review de clientes reais. Não fazemos promessas falsas e somos sempre claros sobre compatibilidades e limitações.

## Os Nossos Valores

### Qualidade
Apenas comercializamos produtos de marcas reconhecidas e fabricantes respeitados. Cada artigo passa por um rigoroso controlo de qualidade antes de chegar aos nossos clientes.

### Transparência
As informações dos produtos são detalhadas e precisas. As avaliações dos clientes são publicadas integralmente, sem censura ou manipulação.

### Suporte Excepcional
A satisfação do cliente é a nossa prioridade número um. A nossa equipa de suporte está disponível 24/7 para responder a qualquer dúvida ou problema.

### Inovação Contínua
Acompanhamos constantemente as tendências tecnológicas e adicionamos os produtos mais inovadores ao nosso catálogo, garantindo que oferecemos sempre as últimas novidades.

## Compromisso com a Sustentabilidade

Na Gadget Hub, estamos comprometidos em reduzir o nosso impacto ambiental:

- **Embalagens Ecológicas:** Utilizamos materiais de embalagem reciclados e biodegradáveis
- **Eficiência Logística:** Optimizamos as rotas de entrega para reduzir a pegada de carbono
- **Eletrónica Responsável:** Incentivamos a reciclagem de dispositivos antigos
- **Política de Devolução:** Processamos devoluções de forma ambientalmente responsável

## Segurança e Conformidade

A Gadget Hub está totalmente em conformidade com:
- Regulamento Geral de Proteção de Dados (RGPD)
- Legislação de Proteção do Consumidor Portuguesa
- Normas de Segurança Europeia para Produtos Eletrónicos
- Certificação SSL 256-bit para todas as transações

## A Nossa Equipa

A Gadget Hub é alimentada por uma equipa diversa de profissionais apaixonados:

- **Gestão:** Profissionais com mais de 15 anos na indústria tecnológica e e-commerce
- **Suporte ao Cliente:** Especialistas treinados para ajudar em qualquer questão relacionada com produtos
- **Logística:** Parceiros confiáveis garantindo entregas rápidas e seguras
- **Marketing & Inovação:** Especialistas em tecnologia digital e tendências de mercado

## Porque Escolher Gadget Hub?

✓ Catálogo vasto com milhares de produtos
✓ Preços competitivos com frequentes promoções
✓ Envio rápido em todo o território português
✓ Suporte ao cliente 24/7 em português
✓ Garantia de satisfação ou dinheiro de volta
✓ Devolução sem complicações (14 dias)
✓ Pagamento seguro com múltiplas opções
✓ Comunidade ativa de utilizadores e reviews

## Contacte-nos

Tem alguma dúvida sobre os nossos produtos ou serviços?

**Email:** suporte@gadgethub.pt
**Horário de Funcionamento:** Segunda a Sexta, 9h às 18h (Hora de Portugal Continental)
**Redes Sociais:**
- Facebook: facebook.com/gadgethubpt
- Instagram: @gadgethubpt
- Twitter/X: @gadgethubpt
- LinkedIn: Gadget Hub Portugal

---

Obrigado por escolher a Gadget Hub. Juntos, vamos explorar o futuro da tecnologia!

---

### 2.2 Página "Perguntas Frequentes (FAQ)"

**URL:** `/pages/faq`
**Template:** Page (Página Estática)

---

#### Conteúdo Completo:

# Perguntas Frequentes (FAQ) - Gadget Hub

Encontre respostas para as perguntas mais comuns sobre os nossos produtos e serviços.

## Envio e Entrega

### 1. Qual é o tempo de entrega em Portugal?

O tempo de entrega padrão é de **7 a 12 dias úteis** após a confirmação do pagamento em Portugal Continental.

Os prazos podem variar dependendo da localização (Açores e Madeira podem demorar 14-21 dias úteis). Você será informado do tempo de entrega específico no momento do checkout.

### 2. Qual é a política de envio gratuito?

Oferecemos **envio gratuito para encomendas superiores a 50€** para Portugal Continental.

Para encomendas inferiores a 50€, o custo de envio é calculado automaticamente no carrinho de compras, geralmente entre 5€ e 15€ dependendo do peso e da localização.

### 3. Posso rastrear a minha encomenda?

Sim! Após a sua encomenda ser enviada, receberá um email com um número de rastreamento (tracking number). Pode utilizar este número no site da transportadora para acompanhar a entrega em tempo real.

O rastreamento está disponível 24-48 horas após o envio da encomenda.

### 4. Qual é a origem dos produtos?

Todos os produtos são originais e fornecidos diretamente pelos fabricantes ou distribuidores autorizados. Não comercializamos produtos falsificados ou réplicas.

### 5. Posso enviar uma encomenda para fora de Portugal?

Neste momento, operamos apenas em Portugal Continental, Açores e Madeira. Estamos a trabalhar em expandir o nosso serviço para o resto da Europa em breve.

Para consultas sobre envio internacional, contacte suporte@gadgethub.pt.

### 6. Como são embalados os produtos?

Todos os produtos são cuidadosamente embalados com materiais de proteção de qualidade para garantir que chegam em perfeito estado. Utilizamos:

- Caixas resistentes e de qualidade
- Papel de proteção e plástico com bolhas de ar
- Materiais de amortecimento (poliestireno ou papel reciclado)
- Embalagens ecológicas sempre que possível

### 7. O que fazer se a encomenda chegar danificada?

Se receber uma encomenda danificada:

1. Não abra completamente a embalagem
2. Fotografe o dano (embalagem exterior e interior)
3. Contacte suporte@gadgethub.pt com as fotos
4. Procederemos a uma substituição ou reembolso imediato

Tem 48 horas a partir da receção para relatar danos.

## Métodos de Pagamento

### 8. Que métodos de pagamento aceitam?

Aceitamos os seguintes métodos de pagamento:

- **Cartão de Crédito:** Visa, Mastercard, American Express
- **Cartão de Débito:** Qualquer cartão de débito bancário português
- **MB WAY:** Código de referência ou telemóvel registado
- **PayPal:** Conta PayPal ativa
- **Transferência Bancária:** Para encomendas acima de 500€ (sob pedido)
- **Compre Agora, Pague Depois:** Parcerias com instituições de crédito (confira disponibilidade)

### 9. Os meus dados de pagamento estão seguros?

Sim. Todos os pagamentos são processados através de gateways de pagamento certificados com encriptação SSL 256-bit. Nunca armazenamos dados completos de cartão no nosso sistema.

Estamos certificados PCI DSS Nível 1, o padrão mais elevado de segurança de pagamento.

### 10. Como é que funciona o MB WAY?

Com MB WAY:

1. Selecione MB WAY no checkout
2. Introduza o seu número de telemóvel
3. Receberá uma notificação no seu telefone
4. Confirme o pagamento na aplicação MB WAY
5. A transação será completada em segundos

Não há comissões adicionais para pagamentos MB WAY.

### 11. Posso parcelar o pagamento?

Sim, para encomendas superiores a 100€ pode parcelar o pagamento em até 12 prestações sem juros através de parceiros de crédito como Cofidis ou Cetesdireto.

A opção de parcelamento estará disponível no checkout se cumprir os critérios.

## Devoluções e Reembolsos

### 12. Qual é a política de devolução?

A Gadget Hub oferece uma **política de devolução de 14 dias sem perguntas**, em conformidade com a legislação de protecção do consumidor europeia e portuguesa.

Tem 14 dias a partir da data de receção da encomenda para solicitar uma devolução, sem necessidade de justificar o motivo.

### 13. Como faço uma devolução?

Para devolver um produto:

1. Aceda à sua conta em gadgethub.pt
2. Selecione o pedido e clique em "Solicitar Devolução"
3. Escolha o motivo (opcional)
4. Receberá um rótulo de envio (em PDF) por email
5. Coloque o produto na caixa original, se possível
6. Utilize o rótulo de envio para devolver à Gadget Hub
7. Após recebermos e validarmos, processaremos o reembolso

**Não pague pelo envio da devolução** - fornecemos um rótulo de envio gratuito.

### 14. Qual é o tempo de reembolso?

Após recebermos a devolução e validarmos o estado do produto (geralmente 3-5 dias úteis), processaremos o reembolso em 3-5 dias úteis adicionais.

Pode esperar ver o reembolso na sua conta bancária ou cartão em até 7 dias úteis após o processamento.

### 15. Posso devolver um produto se foi usado?

Sim, desde que:
- O produto esteja em bom estado geral
- Não tenha sido danificado por mau uso
- Tenha sido testado apenas (uso mínimo)
- Venha com todos os acessórios originais
- Tenha a embalagem original

Produtos com sinais óbvios de dano ou utilização excessiva podem ter o reembolso reduzido em até 20%.

## Garantia e Assistência Técnica

### 16. Qual é a garantia dos produtos?

Todos os produtos vendidos pela Gadget Hub incluem a **garantia legal de 2 anos**, conforme estipulado pela legislação portuguesa e europeia.

Alguns produtos podem ter garantias estendidas do fabricante (24-48 meses). Estas informações estão listadas na ficha do produto.

A garantia cobre:

- Defeitos de fabrico
- Mau funcionamento do produto
- Problemas de hardware não causados por mau uso do cliente

A garantia **não cobre**:

- Danos acidentais
- Utilização inadequada
- Queda ou impacto
- Molhadura (exceto produtos com classificação à prova de água)
- Desgaste normal

### 17. Como solicito a garantia?

Para ativar a garantia:

1. Contacte suporte@gadgethub.pt com:
   - Número do pedido
   - Número de série ou IMEI do produto
   - Descrição do problema
   - Fotografias (se relevante)

2. A nossa equipa avaliará e orientará-o sobre as próximas etapas
3. Pode ser necessário enviar o produto para análise técnica

A análise de garantia é totalmente gratuita.

## Qualidade e Autenticidade

### 18. Como posso ter a certeza de que os produtos são genuínos?

Todos os produtos da Gadget Hub são:

- Fornecidos diretamente por fabricantes ou distribuidores autorizados
- Verificados e testados antes do envio
- Acompanhados de documentação e certificados de autenticidade (quando aplicável)
- Cobertos pela garantia legal portuguesa

Não comercializamos produtos falsificados ou réplicas. Se suspeitar que um produto é falso, contacte-nos imediatamente para reembolso ou troca.

### 19. Os produtos têm garantia do fabricante?

Sim, todos os produtos incluem a garantia do fabricante. Quando recebe o seu gadget, a garantia já está ativada automaticamente a partir da data de compra.

Pode validar a sua garantia no site do fabricante utilizando o número de série do produto.

### 20. E se o produto chegar com defeito?

Se o produto tiver um defeito:

1. Não desmonte nem tente reparar
2. Contacte suporte@gadgethub.pt com fotografia do defeito
3. Pode optar por troca imediata ou devolução com reembolso
4. A Gadget Hub cobre completamente os custos

---

## Contacte-nos

Não encontrou a resposta que procurava?

**Email:** suporte@gadgethub.pt
**Telefone:** +351 21 XXXX XXXX (disponível seg-sex, 9h-18h)
**Chat:** Disponível no website (seg-sex, 10h-20h)
**Redes Sociais:** @gadgethubpt

---

### 2.3 Página "Política de Privacidade"

**URL:** `/pages/politica-privacidade`
**Template:** Page (Página Estática)

---

#### Conteúdo Completo:

# Política de Privacidade - Gadget Hub

**Data de Efetivação:** Abril 2026
**Última Atualização:** Abril 2026

## 1. Introdução

A Gadget Hub (doravante "Empresa", "nós" ou "nosso") está comprometida em proteger a sua privacidade. Esta Política de Privacidade explica como recolhemos, utilizamos, divulgamos e salvaguardamos as suas informações quando visita o nosso website (gadgethub.pt) e utiliza os nossos serviços.

Esta política está em total conformidade com o **Regulamento Geral de Proteção de Dados (RGPD)** da União Europeia e com a legislação portuguesa de proteção de dados pessoais.

## 2. Informações que Recolhemos

### 2.1 Informações que Fornece Voluntariamente

Recolhemos informações que você nos fornece voluntariamente, incluindo:

**Durante o Registo/Conta:**
- Nome completo
- Endereço de email
- Número de telefone
- Palavra-passe (encriptada)
- Data de nascimento
- Endereço residencial

**Durante a Compra:**
- Dados de faturação
- Endereço de entrega
- Informações de cartão (processadas por gateways seguros, não armazenadas no nosso sistema)
- Histórico de encomendas

**Durante a Comunicação:**
- Mensagens de suporte ao cliente
- Feedback e reviews de produtos
- Participação em inquéritos

### 2.2 Informações Recolhidas Automaticamente

**Cookies e Rastreamento:**
- Identificadores de sessão (necessários para funcionamento)
- Preferências de utilizador
- Histórico de navegação no site
- Endereço IP
- Tipo de navegador
- Sistema operativo
- Páginas visitadas e tempo despendido

**Análise (Google Analytics, Hotjar):**
- Padrões de navegação
- Dados demográficos aproximados
- Interações com elementos da página
- Desempenho do site

### 2.3 Informações de Terceiros

Podemos receber informações sobre si de:
- Processadores de pagamento
- Transportadoras logísticas
- Plataformas de redes sociais
- Parceiros de marketing

## 3. Como Utilizamos as Suas Informações

Utilizamos as informações recolhidas para:

### 3.1 Fornecimento de Serviços
- Processar encomendas e entregas
- Enviar confirmações de pedidos
- Gerir a sua conta
- Fornecer suporte ao cliente

### 3.2 Comunicação
- Responder a inquéritos
- Enviar atualizações de encomendas
- Comunicações de suporte técnico
- Avisos sobre política ou alterações de serviço

### 3.3 Marketing (Com Consentimento)
- Enviar newsletters com promoções e novidades
- Publicidade direcionada
- Análise de preferências de compra
- Recomendações personalizadas

### 3.4 Conformidade Legal
- Cumprir obrigações fiscais e legais
- Prevenir fraude
- Proteger os direitos e segurança da empresa

### 3.5 Melhoria do Serviço
- Análise de dados para otimização
- Testes A/B
- Feedback de utilizadores
- Desenvolvimento de novas funcionalidades

## 4. Base Legal para Processamento

O processamento de dados é realizado com base em:

- **Contrato:** Necessário para executar a encomenda (dados de faturação)
- **Consentimento:** Para marketing e cookies não-essenciais (opt-in)
- **Obrigação Legal:** Conformidade fiscal, anti-fraude, proteção do consumidor
- **Interesse Legítimo:** Segurança, prevenção de fraude, melhoria de serviços

## 5. Partilha de Dados

### 5.1 Com Terceiros

Partilhamos dados apenas quando necessário com:

- **Processadores de Pagamento:** Para autorizar transações (Stripe, EDENRED, MB WAY)
- **Transportadoras:** Endereço para entrega (CTT, Seur, DHL)
- **Plataformas Analíticas:** Google Analytics, Hotjar (com dados anonymizados)
- **Servidores de Email:** Para envio de comunicações
- **Processadores Fiscais:** Para conformidade com obrigações legais

### 5.2 Sem Venda de Dados

A Gadget Hub **nunca vende dados pessoais** a terceiros para fins comerciais. Dados são compartilhados apenas para fins operacionais necessários.

### 5.3 Transferências Internacionais

Alguns dados podem ser processados fora da UE (ex: Google, Amazon). Garantimos que há transferências seguras através de:
- Cláusulas Contratuais Padrão (SCCs)
- Decisões de Adequação
- Consentimento do utilizador

## 6. Retenção de Dados

Mantemos os seus dados pessoais apenas pelo tempo necessário:

| Tipo de Dado | Período de Retenção | Motivo |
|--------------|-------------------|--------|
| Dados de Conta | 5 anos após inatividade | Recuperação de conta |
| Histórico de Encomendas | 7 anos | Conformidade fiscal/contabilística |
| Dados de Pagamento | Não retidos completos | Segurança |
| Cookies de Análise | 14 meses | Analytics |
| Logs de Servidor | 30 dias | Segurança |
| Listas de Marketing | Até não-subscrição | Consentimento |

## 7. Segurança de Dados

### 7.1 Medidas de Segurança

Implementamos:

- **Encriptação SSL 256-bit** para toda a comunicação
- **Certificação PCI DSS Nível 1** para processamento de pagamentos
- **Firewalls** e proteção contra intrusões
- **Backups regulares** com redundância
- **Autenticação de dois fatores** (2FA) para contas
- **Auditoria de segurança** periódica

### 7.2 Responsabilidade

Apesar de todas as precauções, nenhum sistema é 100% seguro. A Gadget Hub:

- Notificará imediatamente sobre qualquer violação de dados
- Cooperará com autoridades regulatórias
- Documentará incidentes de segurança

## 8. Os Seus Direitos

Sob o RGPD, tem direito a:

### 8.1 Direito de Acesso
Pode solicitar cópia de todos os dados pessoais que temos sobre si.

### 8.2 Direito de Rectificação
Pode corrigir dados inexatos ou incompletos.

### 8.3 Direito ao Esquecimento
Pode solicitar a eliminação de dados pessoais (com exceções legítimas).

### 8.4 Direito de Restrição
Pode solicitar que restringirmos o processamento dos seus dados.

### 8.5 Direito à Portabilidade
Pode receber os seus dados num formato estruturado e portável.

### 8.6 Direito de Oposição
Pode opor-se ao processamento para fins de marketing direto.

### 8.7 Direito de Não ser Sujeito a Decisões Automatizadas
Tem direito a revisão humana de decisões automatizadas.

## 9. Exercer os Seus Direitos

Para exercer qualquer destes direitos, contacte-nos:

**Email:** privacidade@gadgethub.pt
**Endereço:** Gadget Hub, Rua da Tecnologia, Lisboa, Portugal
**Telefone:** +351 21 XXXX XXXX

Responderemos dentro de 30 dias. Se não ficar satisfeito com a resposta, pode apresentar queixa junto à **Comissão Nacional de Proteção de Dados (CNPD)**.

## 10. Cookies

### 10.1 Tipos de Cookies

**Cookies Essenciais:**
- Autenticação
- Segurança
- Funcionamento do carrinho
- Preferências de idioma

**Cookies de Análise:**
- Google Analytics (análise de tráfego)
- Hotjar (comportamento do utilizador)

**Cookies de Marketing:**
- Facebook Pixel
- Google Ads
- Email de remarketing

### 10.2 Controlo de Cookies

Pode gerir preferências de cookies:
- Banner de consentimento na primeira visita
- Definições de privacidade no rodapé
- Definições do seu navegador
- Opções de opt-out

## 11. Alterações à Política

A Gadget Hub pode atualizar esta Política de Privacidade ocasionalmente. Notificaremos por email sobre alterações materiais.

Continuando a utilizar o site após alterações, aceita a política atualizada.

## 12. Contacte-nos

**Data Protection Officer (DPO):**
Email: privacidade@gadgethub.pt

**Empresa:**
Gadget Hub - Portugal
Email: suporte@gadgethub.pt
Telefone: +351 21 XXXX XXXX
Horário: Seg-Sex, 9h-18h (Hora de Portugal Continental)

---

**Versão:** 1.0
**Próxima Revisão:** Abril 2027

---

### 2.4 Página "Termos e Condições"

**URL:** `/pages/termos-condicoes`
**Template:** Page (Página Estática)

---

#### Conteúdo Completo:

# Termos e Condições - Gadget Hub

**Data de Efetivação:** Abril 2026
**Última Atualização:** Abril 2026
**Versão:** 1.0

## 1. Aceitação dos Termos

Ao aceder e utilizar o website gadgethub.pt (doravante "Site" ou "Serviço"), concorda em ficar vinculado por estes Termos e Condições (doravante "Termos").

Se não concorda com algum aspecto destes Termos, deve deixar de utilizar o Site imediatamente.

## 2. Definições

- **"Gadget Hub"** ou **"Empresa":** Gadget Hub - Comércio de Eletrónicos, Lda.
- **"Cliente"** ou **"Você":** Qualquer pessoa que aceda ao Site ou realize compras
- **"Produtos":** Gadgets e artigos eletrónicos listados no Site
- **"Serviço":** A venda de Produtos e prestação de serviços relacionados
- **"Encomenda":** A solicitação de compra de Produtos
- **"Contrato de Compra":** O acordo vinculativo entre Cliente e Gadget Hub após confirmação da encomenda

## 3. Descrição do Serviço

A Gadget Hub opera uma plataforma de e-commerce onde:

- Disponibiliza catálogo de gadgets e acessórios eletrónicos
- Processa encomendas e pagamentos
- Coordena a entrega de produtos
- Presta suporte ao cliente

O Site funciona como intermediário comercial entre Cliente e Fabricantes/Distribuidores.

## 4. Elegibilidade

### 4.1 Requisitos do Cliente

Para utilizar o Site e realizar compras, deve:

- Ter pelo menos 18 anos de idade
- Ter capacidade legal para celebrar contratos
- Residir em Portugal Continental, Açores ou Madeira
- Fornecer informações precisas e verídicas

### 4.2 Utilizadores Menores

Menores de 18 anos podem utilizar o Site sob supervisão de um progenitor ou tutor legal, que assume responsabilidade total pelas transações.

## 5. Preços e Pagamento

### 5.1 Preços

- Todos os preços estão **incluído IVA (23%)** salvo indicação em contrário
- Preços em **Euros (€)**
- Sujeitos a alteração sem aviso prévio
- Preço final confirmado apenas no checkout

### 5.2 Promoções

- Descontos e promoções são válidos conforme especificado
- A Gadget Hub pode cancelar promoções a qualquer momento
- Códigos promocionais não são cumuláveis (salvo indicação)
- Produtos em promoção não podem ser devolvidos para reembolso total (sujeito à política de devoluções)

### 5.3 Métodos de Pagamento Aceites

- Cartão de Crédito (Visa, Mastercard, AmEx)
- Cartão de Débito
- MB WAY
- PayPal
- Transferência Bancária (para encomendas acima de 500€)

### 5.4 Processamento de Pagamento

- Pagamentos processados por gateways certificados
- Autenticação 3D Secure é obrigatória para cartões
- Transações não autorizadas serão contactado através do email registado

### 5.5 Responsabilidade do Pagamento

Você é responsável por:
- Manter as credenciais de acesso confidenciais
- Notificar imediatamente sobre uso não autorizado
- Pagar todas as encomendas autorizadas

## 6. Encomendas e Contrato de Compra

### 6.1 Processo de Encomenda

1. Selecionar produtos
2. Adicionar ao carrinho
3. Proceder ao checkout
4. Inserir dados de faturação e entrega
5. Confirmar método de pagamento
6. Receber confirmação de encomenda

### 6.2 Aceitação da Encomenda

- Encomenda é apenas **proposta de compra** até confirmação de pagamento
- Gadget Hub aceita a encomenda após:
  - Pagamento estar processado com sucesso
  - Confirmação de disponibilidade do produto
  - Email de confirmação da encomenda ser enviado

### 6.3 Disponibilidade de Produtos

A Gadget Hub não garante disponibilidade contínua de produtos. Em caso de indisponibilidade após pagamento:

- Será contactado dentro de 24 horas
- Pode optar por substituição por produto similar
- Pode solicitar reembolso integral sem penalidade

### 6.4 Direito de Rejeição

A Gadget Hub pode rejeitar uma encomenda se:

- Informações fraudulentas forem detectadas
- Endereço de entrega for inválido
- Suspeita razoável de atividade ilegal
- Violação destes Termos

## 7. Envio e Entrega

### 7.1 Prazos de Entrega

- **Portugal Continental:** 7-12 dias úteis após confirmação
- **Açores/Madeira:** 14-21 dias úteis após confirmação
- **Feriados:** Prazos podem ser estendidos
- Prazos são estimativas, não garantias absolutas

### 7.2 Custos de Envio

- **Envio Gratuito:** Encomendas acima de 50€
- **Envio Pago:** Abaixo de 50€ (5€-15€ conforme peso/localização)
- Custos calculados automaticamente no checkout

### 7.3 Entrega e Risco

- O risco do produto passa ao Cliente após entrega bem-sucedida
- Assinatura pode ser solicitada para encomendas de alto valor
- Cliente é responsável por assinalar danos imediatamente

### 7.4 Falha de Entrega

Se entrega falhar:
- Transportadora fará tentativas adicionais (confira email)
- Encomenda pode ser devolvida após 3 tentativas
- Será contactado para opções de reentrega

## 8. Direito de Desistência (14 dias)

### 8.1 Direito de Desistência

Tem direito a desistir da encomenda sem justificação dentro de **14 dias corridos** a partir da data de receção.

### 8.2 Procedimento

1. Contacte suporte@gadgethub.pt com número do pedido
2. Receberá instruções de devolução
3. Devolva o produto em bom estado
4. Reembolso processado após validação (até 7 dias úteis)

### 8.3 Exclusões do Direito de Desistência

Este direito não se aplica a:

- Produtos personalizados ou feitos sob encomenda
- Produtos que perderam a embalagem original
- Itens consumíveis já utilizados
- Software ou aplicações já instaladas
- Serviços já prestados integralmente

## 9. Responsabilidade e Garantias

### 9.1 Garantia Legal

Todos os produtos incluem **garantia legal de 2 anos** sob legislação portuguesa, cobrindo defeitos não resultantes de mau uso do Cliente.

### 9.2 Isenção de Responsabilidade

A Gadget Hub não é responsável por:

- Danos causados por mau uso ou negligência
- Incompatibilidade de produtos não claramente indicada
- Atraso de entrega (exceto por culpa exclusiva da Gadget Hub)
- Perda de lucros ou dados resultante do uso de produtos

### 9.3 Limitação de Responsabilidade

A responsabilidade máxima da Gadget Hub perante o Cliente não excede o valor total pago pela encomenda em questão.

## 10. Propriedade Intelectual

### 10.1 Conteúdo do Site

Todo o conteúdo (texto, imagens, logos, design) é propriedade intelectual da Gadget Hub ou de seus licenciadores.

### 10.2 Uso Autorizado

Pode utilizar o conteúdo apenas para:
- Visualização pessoal
- Realização de compras

### 10.3 Uso Não Autorizado

É proibido:
- Reproduzir ou distribuir conteúdo sem permissão
- Criar obras derivadas
- Usar imagens para fins comerciais
- Aplicar engenharia reversa

## 11. Códigos de Conduta do Utilizador

### 11.1 Proibições

Ao utilizar o Site, concorda em não:

- Violar qualquer lei ou regulamento
- Fazer upload de conteúdo ilegal, ofensivo ou prejudicial
- Assédio ou ameaça a outros utilizadores ou staff
- Spam ou mensagens automáticas em excesso
- Tentar aceder a sistemas sem autorização
- Criar contas falsas ou fraudulentas
- Usar robôs ou scrapers
- Reverter-engenharia do Site

### 11.2 Consequências

Violações podem resultar em:
- Suspensão de conta
- Cancelamento de encomendas
- Restrição de acesso permanente
- Ação legal

## 12. Reviews e Feedback

### 12.1 Submissão de Reviews

Clientes podem submeter reviews de produtos. Reviews devem ser:

- Honestos e precisos
- Baseados em experiência pessoal
- Livres de linguagem ofensiva
- Não comerciais (sem publicidade)

### 12.2 Moderação

A Gadget Hub pode:

- Moderar reviews antes da publicação
- Remover reviews que violem estes Termos
- Rejeitar reviews falsos ou promocionais

### 12.3 Propriedade

Reviews publicados tornam-se propriedade da Gadget Hub, que pode utilizá-los para marketing (com anonimato).

## 13. Links Externos

O Site pode conter links para websites terceiros. A Gadget Hub:

- Não controla conteúdo externo
- Não é responsável por terceiros
- Recomenda revisar políticas desses sites

## 14. Alteração e Descontinuação

A Gadget Hub pode:

- Modificar o Site sem aviso
- Descontinuar serviços
- Restringir acesso a áreas

Não será responsável por indisponibilidade causada por manutenção.

## 15. Vigência e Cancelamento

### 15.1 Vigência

Estes Termos vigoram indefinidamente até rescisão.

### 15.2 Rescisão

A Gadget Hub pode rescinder a sua conta se:

- Violar estes Termos repetidamente
- Realizar atividades fraudulentas
- Fazer pedidos considerados abusivos

## 16. Conformidade Legal

### 16.1 Legislação Aplicável

Estes Termos são regidos pelas leis de Portugal.

### 16.2 Jurisdição

Qualquer disputa será tratada pelos tribunais portugueses.

### 16.3 Conformidade com Legislação

A Gadget Hub cumpre:
- Lei da Proteção do Consumidor (PT)
- Regulamento RGPD (UE)
- Legislação de E-commerce (PT/UE)
- Normas de Segurança Europeia

## 17. Alterações aos Termos

A Gadget Hub pode alterar estes Termos periodicamente. Alterações materiais serão notificadas por email.

Continuando a utilizar o Site após alterações, aceita os Termos revistos.

## 18. Contacto

Para dúvidas sobre estes Termos:

**Email:** suporte@gadgethub.pt
**Telefone:** +351 21 XXXX XXXX
**Endereço:** Gadget Hub, Rua da Tecnologia, Lisboa, Portugal
**Horário:** Seg-Qui, 9h-18h (Hora de Portugal Continental)

---

**Versão:** 1.0
**Próxima Revisão:** Abril 2027

---

### 2.5 Página "Política de Devoluções"

**URL:** `/pages/politica-devolucoes`
**Template:** Page (Página Estática)

---

#### Conteúdo Completo:

# Política de Devoluções - Gadget Hub

**Data de Efetivação:** Abril 2026
**Validade:** Indefinida, sujeita a revisão anual
**Conformidade:** Lei 24/96 (Proteção do Consumidor) e Direito UE

---

## 1. Direito de Devolução

### 1.1 Período de Devolução

Tem direito a devolver produtos adquiridos na Gadget Hub dentro de **14 dias corridos** contados a partir da data de receção da encomenda.

Este direito aplica-se a compras online realizadas através do website gadgethub.pt e é independente de qualquer garantia de fabricante.

### 1.2 Sem Necessidade de Justificação

Pode exercer o direito de devolução **sem necessidade de fornecer qualquer justificação** ou explicação sobre o motivo da devolução.

A Gadget Hub não questionará o seu direito de desistir da compra.

### 1.3 Exceções (Produtos Não Devolúveis)

O direito de devolução **não se aplica a:**

- **Produtos personalizados:** Itens fabricados especialmente conforme suas especificações
- **Software e aplicações:** Uma vez instaladas ou ativadas
- **Produtos consumidos:** Itens já utilizados além do teste razoável
- **Acessórios separados:** Peças menores já abertas e testadas (ex: cabos com protective seal aberto)
- **Itens com dano óbvio:** Produtos com sinais claros de mau uso não imputável ao transporte
- **Artigos higiene pessoal:** Por questões sanitárias (headphones com borrachas testadas, etc.)

### 1.4 Teste Razoável

A Gadget Hub reconhece que necessita de tempo para:
- Desembalar e inspecionar o produto
- Verificar a funcionalidade básica
- Confirmar compatibilidade

Uma utilização limitada para este fim é considerada **teste razoável** e não afeta o direito de devolução.

## 2. Condições para Devolução

### 2.1 Estado do Produto

Para ser elegível para devolução, o produto deve:

- ✓ Estar em bom estado geral
- ✓ Funcionar corretamente (sem defeitos causados por mau uso)
- ✓ Incluir todos os acessórios originais fornecidos
- ✓ Ter a embalagem original, se possível
- ✓ Não apresentar sinais de dano por queda ou impacto
- ✓ Não estar molhado (salvo se publicado como à prova de água)
- ✓ Sem danos nas caixas de proteção original

### 2.2 Itens Não Inclusos

Se a devolução não incluir:

- Embalagem original completa: possível redução de 10% no reembolso
- Acessórios inclusos: possível redução de 5-20% conforme item
- Documentação (fatura, certificados): sem impacto no reembolso

### 2.3 Inspecção Técnica

Para produtos que alegam defeito técnico, a Gadget Hub pode:

- Testar o produto para confirmar funcionamento
- Requerer prova de defeito (vídeo demonstrativo)
- Contactar o fabricante para avaliação

Se não houver defeito comprovado, o reembolso pode ser reduzido em até 20% pelas despesas de inspeção.

## 3. Processo de Devolução

### 3.1 Passo 1: Notificação

1. Aceda a gadgethub.pt na sua conta
2. Vá a "Minhas Encomendas"
3. Selecione a encomenda e clique em "Solicitar Devolução"
4. Escolha o motivo (opcional):
   - Não desejado
   - Defeituoso
   - Diferente da descrição
   - Mudança de ideia
   - Outro (especificar)

**Prazo:** Deve ser iniciado dentro de 14 dias de receção

### 3.2 Passo 2: Confirmação

Dentro de 24-48 horas:

- Receberá email de confirmação
- Rótulo de envio PDF em anexo
- Instruções detalhadas de devolução
- Número de referência de devolução

### 3.3 Passo 3: Preparação da Encomenda

1. Coloque o produto na **embalagem original**, se possível
2. Inclua:
   - Todos os acessórios originais
   - Documentação (fatura, manual)
   - Número de referência de devolução (impressão ou foto)

3. **Não desmonte** o produto
4. **Não repare** o produto

### 3.4 Passo 4: Envio da Devolução

1. Imprima o rótulo de envio fornecido
2. Cole no exterior da caixa
3. Entregue em:
   - **Loja CTT** mais próxima (recomendado)
   - **Postos de Correio**
   - **Agências de transportadoras parceiras**

**Não pague pelo envio** - o rótulo é gratuito e já tem franquia paga.

### 3.5 Passo 5: Rastreamento

- Rótulo de envio inclui número de rastreamento
- Monitorize em ctt.pt ou no website da transportadora
- Email de notificação quando recebemos a devolução

### 3.6 Passo 6: Inspeção

Após recebimento:

1. Equipa verifica o estado do produto (3-5 dias úteis)
2. Testa funcionamento se necessário
3. Confirma recebimento por email

### 3.7 Passo 7: Reembolso

Após aprovação da devolução:

- **Processamento:** 3-5 dias úteis
- **Reembolso visível na conta:** 5-7 dias úteis (dependendo do banco)

O valor é reembolsado através do **mesmo método de pagamento** utilizado na compra.

## 4. Prazo de Reembolso

### 4.1 Cronograma

| Etapa | Prazo |
|-------|-------|
| Solicitação da devolução | 14 dias após receção |
| Confirmação da devolução | Até 48 horas |
| Envio para Gadget Hub | Até 14 dias a partir da confirmação |
| Inspeção | 3-5 dias úteis após receção |
| Processamento do reembolso | 3-5 dias úteis |
| Crédito na conta bancária | 5-7 dias úteis |

### 4.2 Cálculo do Reembolso

O reembolso inclui:
- Preço do produto pago
- IVA
- **Não inclui:** Custos de envio original (a menos que devido a defeito)

O reembolso pode ser reduzido se:
- Produto tiver danos causados pelo cliente: -10-20%
- Embalagem original estiver em mau estado: -5-10%
- Acessórios faltarem: -5-15% conforme item

## 5. Devoluções por Defeito ou Inconformidade

### 5.1 Produto Defeituoso

Se recebeu um produto com defeito de fabrico:

1. **Contacte imediatamente:** suporte@gadgethub.pt com:
   - Fotografias do defeito
   - Vídeo de demonstração (se possível)
   - Descrição detalhada do problema

2. **Gadget Hub pode optar por:**
   - Substituição imediata (sem esperar 14 dias)
   - Reembolso integral expedito
   - Envio de peça de reposição

3. **Custos:** Totalmente cobertos pela Gadget Hub

### 5.2 Produto Diferente da Descrição

Se o produto:
- Não corresponde à descrição do website
- Tem especificações incorretas
- É incompatível conforme anunciado

**Procedimento:**

1. Contacte suporte@gadgethub.pt com:
   - Print da descrição no website
   - Fotografias do produto recebido
   - Explicação da discrepância

2. Gadget Hub revisa a reclamação (24-48 horas)
3. Se confirmada, oferece:
   - Troca por produto correto (sem custos)
   - Reembolso integral (mesmo fora do prazo de 14 dias)

## 6. Casos Especiais

### 6.1 Devolução de Produtos em Promoção

- Produtos em desconto podem ser devolvidos normalmente
- O reembolso é do valor pago (com desconto aplicado)
- Gadget Hub não oferece diferença se a promoção terminar

### 6.2 Devolução de Produtos Bundle/Kit

Se devolveu um bundle (conjunto de produtos):

- Pode devolver parcialmente (perde o desconto do bundle)
- O reembolso reflete o preço individual dos itens devolvidos

### 6.3 Encomendas com Vários Itens

Pode devolver:
- Alguns itens (apenas esses são reembolsados)
- Todos os itens
- Custos de envio da devolução são sempre gratuitos

### 6.4 Produtos Danificados no Transporte

Se chegou danificado:

1. **Não abra completamente a embalagem**
2. Fotografe o dano (exterior e interior)
3. Contacte suporte@gadgethub.pt dentro de **48 horas**
4. Gadget Hub oferece:
   - Substituição imediata (sem esperar 14 dias)
   - Reembolso integral
   - Sem custos para o cliente

## 7. Restrições e Limitações

### 7.1 Não Elegível para Devolução

Os seguintes itens **não podem ser devolvidos**:

- Produtos com sinais óbvios de mau uso não imputável ao transporte
- Produtos que foram completamente desmontados
- Itens para os quais já foi oferecida substituição ou reembolso
- Produtos adquiridos há mais de 14 dias (salvo defeito de fabrico)

### 7.2 Fraude de Devolução

A Gadget Hub reserva-se o direito de:

- Investigar devoluções frequentes da mesma pessoa
- Rejeitar devoluções fraudulentas
- Reportar à polícia se suspeita de fraude
- Bloquear conta de cliente fraudulento

## 8. Contacto para Devoluções

Para qualquer questão sobre devoluções:

**Email:** devolvacoes@gadgethub.pt (resposta em 24h)
**Email Geral:** suporte@gadgethub.pt
**Telefone:** +351 21 XXXX XXXX
**Horário:** Seg-Sex, 9h-18h (Portugal Continental)
**Chat:** Disponível no website (seg-sex, 10h-20h)

---

**Versão:** 1.0
**Próxima Revisão:** Abril 2027

---

### 2.6 Página "Contacto"

**URL:** `/pages/contacto`
**Template:** Page + Formulário

---

#### Conteúdo Completo:

# Contacte-nos - Gadget Hub

Tem alguma pergunta ou problema? Adorámos saber de si! Existem várias maneiras de nos contactar.

## Informações de Contacto Direto

### Telefone
**+351 21 XXX XXXX**
Seg-Qui: 9h às 18h (Hora de Portugal Continental)
*Chamadas a custo local*

### Email
**suporte@gadgethub.pt** - Suporte Geral
**devolvacoes@gadgethub.pt** - Devoluções e Reembolsos
**privacidade@gadgethub.pt** - Privacidade de Dados
**vendas@gadgethub.pt** - Parcerias Comerciais

*Tempo de resposta: até 24 horas úteis*

### Endereço Físico
Gadget Hub - Comércio de Eletrónicos, Lda.
Rua da Tecnologia, 42
1000-000 Lisboa, Portugal

*Nota: Não temos loja física aberta ao público. Visite-nos online!*

### Horário de Funcionamento
- **Segunda a Sexta:** 9h - 18h
- **Sábado:** 10h - 14h
- **Domingo e Feriados:** Encerrado
- **Zona Horária:** Hora de Portugal Continental (WET/WEST)

---

## Formulário de Contacto

Utilize o formulário abaixo para nos contactar. Responderemos dentro de 24 horas úteis.

```
[FORMULÁRIO HTML - Campos:]

Nome Completo*
Email*
Telemóvel
Número de Encomenda (opcional)
Assunto* [Dropdown:]
  - Questão sobre um produto
  - Questão sobre uma encomenda
  - Pedido de devolução
  - Suporte técnico
  - Informações sobre garantia
  - Reclamação
  - Parcerias
  - Outro

Mensagem*
[Textarea - mín 20 caracteres]

Consentimento RGPD*
☐ Concordo com a Política de Privacidade e autorizo o processamento dos meus dados

[Botão] Enviar Mensagem

[Botão] Limpar Formulário
```

---

## Chat em Direto

Disponível no canto inferior direito do website:
- **Seg-Sexta:** 10h - 20h
- Resposta média: 2-5 minutos
- Ideal para questões urgentes

---

## Redes Sociais

Siga-nos e contacte-nos também através das redes sociais:

- **Facebook:** [facebook.com/gadgethubpt](https://facebook.com/gadgethubpt)
- **Instagram:** [@gadgethubpt](https://instagram.com/gadgethubpt)
- **Twitter/X:** [@gadgethubpt](https://twitter.com/gadgethubpt)
- **LinkedIn:** [Gadget Hub Portugal](https://linkedin.com/company/gadgethubpt)
- **TikTok:** [@gadgethubpt](https://tiktok.com/@gadgethubpt)

Tempo de resposta nas redes sociais: 24-48 horas

---

## FAQ Rápido

Antes de contactar, verifique as respostas às perguntas mais frequentes:

- [Ver Perguntas Frequentes →](/pages/faq)

Muitas das suas questões podem ser respondidas instantaneamente!

---

## Suporte Técnico para Produtos

Se tem um problema técnico com um produto:

### Antes de Contactar, Tente:
1. Reiniciar o dispositivo
2. Verificar a compatibilidade (veja as especificações do produto)
3. Carregar completamente (se for dispositivo com bateria)
4. Atualizar software (se aplicável)
5. Consultar o manual do fabricante

### Ao Contactar, Tenha Pronto:
- Número de série ou IMEI do dispositivo
- Modelo exato do produto
- Data de compra
- Descrição detalhada do problema
- Fotografias ou vídeo (se relevante)

---

## Reclamações Formais

Se deseja apresentar uma reclamação formal sobre o nosso serviço:

1. **Contacte primeiro o Suporte:** suporte@gadgethub.pt
2. **Descreva a situação:** Seja o mais detalhado possível
3. **Prazo:** Resposta dentro de 10 dias úteis
4. **Escalação:** Se não ficar satisfeito, pode apresentar queixa junto à:

**Direção-Geral da Economia Segura (DGES)**
Rua de São José, 43
1200-330 Lisboa, Portugal
Telefone: +351 213 916 000

---

## Reportar um Problema de Segurança

Se descobrir uma vulnerabilidade de segurança no website:

**Por favor, contacte confidencialmente:** seguranca@gadgethub.pt

Descrição detalhada + reprodução dos passos.
Agradecemos a sua responsabilidade na divulgação!

---

## Horários Alargados Durante Períodos Pico

Durante Natal, Black Friday e outras épocas altas:

- Horário estendido até às 22h
- Chat disponível até às 23h
- Mais agentes de suporte disponíveis
- Tempo de resposta reduzido

*Datas específicas serão comunicadas no website*

---

## Estatísticas de Resposta

Na Gadget Hub, tomamos o suporte a sério:

- **98% de satisfação** do cliente
- **Tempo médio de resposta:** 4 horas
- **Taxa de resolução na primeira contacto:** 85%
- **Reviews médios de suporte:** 4.8/5 estrelas

---

Estamos aqui para ajudar! Não hesite em contactar-nos com qualquer dúvida, sugestão ou preocupação. A sua satisfação é a nossa prioridade.

---

## Notícias e Atualizações

Para estar atualizado sobre:
- Novos produtos
- Promoções exclusivas
- Dicas tecnológicas
- Notícias da indústria

**Subscreva a nossa newsletter:** [Formulário de Subscrição]

---

---

## PARTE 3: SEO & PERFORMANCE

### 3.1 Schema Markup Recommendations

**Implementação de JSON-LD Estruturado**

#### Schema: Organization

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Gadget Hub",
  "alternateName": "Gadget Hub Portugal",
  "url": "https://gadgethub.pt",
  "logo": "https://gadgethub.pt/logo.png",
  "description": "Loja online de gadgets e tecnologia inteligente em Portugal",
  "sameAs": [
    "https://facebook.com/gadgethubpt",
    "https://instagram.com/gadgethubpt",
    "https://twitter.com/gadgethubpt"
  ],
  "contact": {
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "telephone": "+351-21-XXXXXX",
    "email": "suporte@gadgethub.pt",
    "availableLanguage": "pt-PT"
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Rua da Tecnologia, 42",
    "addressLocality": "Lisboa",
    "postalCode": "1000-000",
    "addressCountry": "PT"
  }
}
```

#### Schema: Product (Para cada Produto)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Nome do Produto]",
  "description": "[Descrição Curta]",
  "sku": "[SKU]",
  "brand": {
    "@type": "Brand",
    "name": "[Marca do Fabricante]"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://gadgethub.pt/products/[slug]",
    "priceCurrency": "EUR",
    "price": "[Preço]",
    "availability": "https://schema.org/[InStock|OutOfStock]",
    "seller": {
      "@type": "Organization",
      "name": "Gadget Hub"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[Nota]",
    "reviewCount": "[Nº Reviews]"
  },
  "image": "[URL da Imagem Principal]",
  "review": {
    "@type": "Review",
    "author": "[Nome do Reviewer]",
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": "[1-5]"
    },
    "reviewBody": "[Texto do Review]"
  }
}
```

#### Schema: BreadcrumbList (Navegação)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://gadgethub.pt"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Smartphones",
      "item": "https://gadgethub.pt/collections/smartphones"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[Nome do Produto]",
      "item": "https://gadgethub.pt/products/[slug]"
    }
  ]
}
```

#### Schema: LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Gadget Hub",
  "description": "Loja online de gadgets em Portugal",
  "url": "https://gadgethub.pt",
  "telephone": "+351-21-XXXXXX",
  "email": "suporte@gadgethub.pt",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "18:00"
    }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[Nota Geral]",
    "reviewCount": "[Total Reviews]"
  }
}
```

#### Schema: FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Pergunta]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Resposta Completa]"
      }
    }
  ]
}
```

---

### 3.2 Meta Titles e Descriptions Templates

**Padrões Recomendados para SEO**

#### Homepage
- **Title:** `Gadget Hub - Lojas Online de Gadgets em Portugal | Envio Gratuito`
- **Length:** 60 caracteres
- **Description:** `Compre gadgets de qualidade em Portugal. Smartphones, auriculares, smartwatches e muito mais. Envio grátis acima de 50€. Devolução 14 dias. Suporte 24/7.`
- **Meta Length:** 160 caracteres

#### Páginas de Categoria
- **Template:** `[Nome da Categoria] | Gadget Hub Portugal - Compre Online`
- **Description:** `Explore nossa seleção de [categoria]. [Nº de produtos] produtos. [Benefício 1], [Benefício 2]. Envio rápido. Garantia [periodo].`
- **Exemplos:**
  - Title: `Smartphones | Gadget Hub Portugal - Compre Online`
  - Description: `Explore smartphones premium e acessórios. 500+ produtos. Envio grátis acima de 50€. Garantia 2 anos. Devolução 14 dias.`

#### Páginas de Produto
- **Template:** `[Marca] [Modelo] - Compre em Portugal | Gadget Hub`
- **Description:** `[Marca] [Modelo]. [Especificação Principal]. Preço: [Preço]€. Em stock. Envio [tempo]. Garantia [periodo]. Reviews: [Nota]/5.`
- **Exemplo:**
  - Title: `Apple iPhone 15 Pro - Compre em Portugal | Gadget Hub`
  - Description: `iPhone 15 Pro. 128GB, Titânio Preto. 1299€. Em stock. Envio 7-12 dias. Garantia 2 anos. Reviews: 4.8/5. Compre agora!`

#### Páginas Estáticas
- **Sobre:** `Sobre Gadget Hub - História, Valores e Missão`
- **FAQ:** `Perguntas Frequentes - Respostas Rápidas | Gadget Hub`
- **Política Privacidade:** `Política de Privacidade - Proteção RGPD | Gadget Hub`
- **Contacto:** `Contacte Gadget Hub - Suporte Online 24/7`

**Meta Descriptions para Estáticas:**
- Máximo 160 caracteres
- Incluir CTA ("Saiba Mais", "Leia Agora", "Contacte-nos")
- Mencionar valor único (24/7, RGPD, etc.)

---

### 3.3 Sitemap XML

**Estrutura Recomendada**

#### Ficheiro: `/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">

  <!-- Homepage -->
  <url>
    <loc>https://gadgethub.pt</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>

  <!-- Páginas Principais -->
  <url>
    <loc>https://gadgethub.pt/pages/sobre-nos</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/pages/faq</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/pages/contacto</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/pages/politica-privacidade</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.6</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/pages/termos-condicoes</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.6</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/pages/politica-devolucoes</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
  </url>

  <!-- Categorias Principais -->
  <url>
    <loc>https://gadgethub.pt/collections/smartphones</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/tablets</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/auriculares</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/smartwatches</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/cameras</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Subcategorias -->
  <url>
    <loc>https://gadgethub.pt/collections/smartphones/iphone</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/smartphones/samsung</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/auriculares/bluetooth</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Filtros (com parâmetros canónicos) -->
  <url>
    <loc>https://gadgethub.pt/collections/smartphones?sort=best-selling</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>

  <url>
    <loc>https://gadgethub.pt/collections/smartphones?sort=price-low-high</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>

</urlset>
```

#### Ficheiro: `/sitemap-products.xml`

Gerar automaticamente no Shopify:
- Sitemap para produtos (até 50.000 produtos)
- Atualizar diariamente
- Incluir imagens dos produtos
- Prioridade: 0.7-0.9

#### Ficheiro: `/sitemap-pages.xml`

Gerar automaticamente para todas as páginas estáticas criadas.

#### Registar em Google Search Console

1. Ir a Google Search Console
2. Adicionar: `https://gadgethub.pt/sitemap.xml`
3. Submeter para indexação
4. Verificar erros de rastreamento

---

### 3.4 Image Optimization Guidelines

**Otimização de Imagens para Web**

#### Dimensões Recomendadas

| Uso | Dimensão | Formato | Tamanho Max | Notas |
|-----|----------|---------|------------|-------|
| Homepage Hero | 1920x600px | WebP + JPEG | 150KB | Responsivo |
| Categorias (Grid) | 600x400px | WebP + JPEG | 80KB | Ícones SVG |
| Produto (Miniatura) | 300x300px | WebP + JPEG | 50KB | Gallery thumb |
| Produto (Principal) | 600x600px | WebP + JPEG | 100KB | Zoom ativo |
| Produto (Detalhe) | 1200x1200px | WebP + JPEG | 200KB | Alta resolução |
| Redes Sociais | 1200x630px | WebP + JPEG | 120KB | Open Graph |
| Favicon | 32x32, 16x16px | ICO, PNG | 10KB | Multi-size |
| Logo | 200x60px | SVG | 5KB | Vetorial |

#### Formato de Ficheiros

**Prioridade:**
1. **WebP** (melhor compressão, suporte >95% navegadores)
2. **JPEG** (compatibilidade universal)
3. **PNG** (transparência, se necessário)

**Nunca usar:**
- BMP, TIFF, GIF (exceto para animações)
- Imagens não comprimidas

#### Nomenclatura de Ficheiros

```
Estrutura: [categoria]-[tipo]-[tamanho].[ext]

Exemplos:
- smartphone-hero-1920x600.webp
- auriculares-product-600x600.webp
- smartwatch-thumb-300x300.webp
- gadgethub-logo-200x60.svg
- icon-shipping-48x48.svg
```

#### Metadata de Imagem

```html
<img
  src="smartphone-product-600x600.webp"
  alt="Apple iPhone 15 Pro, 128GB, Titânio Preto"
  width="600"
  height="600"
  loading="lazy"
  srcset="
    smartphone-product-300x300.webp 300w,
    smartphone-product-600x600.webp 600w,
    smartphone-product-1200x1200.webp 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 25vw"
/>
```

#### Otimização Shopify

**Ativar no Painel:**
1. Definições > Ficheiros
2. Ativar compressão automática de imagens
3. Formatos: WebP + JPEG
4. Lazy loading automático

**Usar Filtro Liquid:**
```liquid
{{ image_url | img_url: '600x600' }}
```

#### Directives para Shopify Theme

```json
{
  "images": {
    "responsive": true,
    "aspect_ratio": "1:1",
    "lazy_loading": true,
    "format": "webp"
  }
}
```

#### Performance (Core Web Vitals)

- **LCP (Largest Contentful Paint):** Imagens carregadas em <2.5s
- **CLS (Cumulative Layout Shift):** Especificar width/height
- **FID (First Input Delay):** Lazy load para imagens below the fold

---

---

## PARTE 4: SINAIS DE CONFIANÇA

### 4.1 Security Badges (Badges de Segurança)

**Implementação Recomendada**

#### SSL Certificate Badge

```html
<div class="trust-badge ssl">
  <img src="/images/ssl-secure-badge.svg" alt="SSL Seguro" />
  <p>Conexão Segura<br/>256-bit SSL</p>
</div>
```

**Posições Recomendadas:**
- Rodapé do site (lado direito)
- Página de checkout (acima do botão submeter)
- Página de contacto (perto do formulário)

#### Certificações de Segurança

**Badges a Mostrar:**
- ✓ PCI DSS Compliant (Nível 1)
- ✓ RGPD Certified
- ✓ ISO 27001 (se aplicável)
- ✓ McAfee Secure / Norton Secured
- ✓ Google Safe Browsing

**Código HTML:**
```html
<div class="security-certifications">
  <img src="/badges/pci-dss-level1.svg" alt="PCI DSS Nível 1" title="Conformidade PCI DSS Nível 1" />
  <img src="/badges/rgpd-certified.svg" alt="RGPD Certificado" title="Proteção de Dados RGPD" />
  <img src="/badges/mcafee-secure.svg" alt="McAfee Secure" title="Protegido por McAfee" />
</div>
```

---

### 4.2 Country Flags para Shipping

**Implementação Visual**

#### Página de Produto

```html
<div class="shipping-info">
  <h4>Entrega em:</h4>
  <ul class="shipping-countries">
    <li><span class="flag">🇵🇹</span> Portugal Continental - 7-12 dias (Grátis >50€)</li>
    <li><span class="flag">🇵🇹</span> Açores - 14-21 dias</li>
    <li><span class="flag">🇵🇹</span> Madeira - 14-21 dias</li>
  </ul>
</div>
```

#### Checkout

```html
<div class="shipping-rates">
  <h3>Selecione o país de entrega:</h3>
  <label><input type="radio" name="country" value="PT" /> 🇵🇹 Portugal Continental</label>
  <label><input type="radio" name="country" value="PT-AC" /> 🇵🇹 Açores</label>
  <label><input type="radio" name="country" value="PT-MD" /> 🇵🇹 Madeira</label>
</div>
```

#### Homepage Hero

```html
<div class="trust-section">
  <h2>Envio Rápido em Portugal</h2>
  <div class="country-flags">
    <img src="/flags/pt.svg" alt="Portugal" />
  </div>
  <p>Enviamos para todo o território português continental, Açores e Madeira</p>
</div>
```

---

### 4.3 Customer Reviews & Testimonials

**Sistema de Reviews**

#### Integração Shopify

**Apps Recomendadas:**
- Stamped.io (avaliações com fotos)
- Judge.me (reviews com SEO)
- Trustpilot (avaliações externas)

#### Badge de Reviews

```html
<div class="reviews-badge">
  <div class="rating">
    <span class="stars">★★★★★</span>
    <span class="rating-value">4.8</span>
  </div>
  <p><strong>1.247 reviews</strong> de clientes verificados</p>
</div>
```

#### Widget de Reviews (Homepage)

```html
<section class="customer-reviews">
  <h2>O Que Dizem Nossos Clientes</h2>

  <div class="review">
    <div class="rating">★★★★★</div>
    <p class="review-text">"Entrega rápida, produto genuíno e bem embalado. Muito feliz com a compra!"</p>
    <p class="reviewer">João Silva, Lisboa</p>
  </div>

  <div class="review">
    <div class="rating">★★★★★</div>
    <p class="review-text">"Suporte excelente quando tive uma dúvida. Responderam em minutos!"</p>
    <p class="reviewer">Maria Santos, Porto</p>
  </div>

  <div class="review">
    <div class="rating">★★★★★</div>
    <p class="review-text">"Ótima seleção de produtos a preços competitivos. Voltarei a comprar!"</p>
    <p class="reviewer">Pedro Costa, Covilhã</p>
  </div>

  <p class="cta"><a href="#all-reviews">Ver Todos os Reviews →</a></p>
</section>
```

#### Página Dedicada de Reviews

**URL:** `/pages/reviews-clientes`

```html
<h1>Reviews de Clientes Gadget Hub</h1>

<div class="reviews-summary">
  <div class="stat">
    <h3>4.8/5</h3>
    <p>Classificação Média</p>
    <p class="reviews-count">1.247 reviews de clientes verificados</p>
  </div>
</div>

<div class="reviews-filter">
  <label>Filtrar por:</label>
  <select>
    <option>Mais Recentes</option>
    <option>Maior Classificação</option>
    <option>Menor Classificação</option>
    <option>Mais Úteis</option>
  </select>
</div>

<div class="reviews-list">
  <!-- Listar reviews com paginação -->
</div>
```

---

### 4.4 Satisfaction Guarantee Badge

**Badge de Garantia de Satisfação**

#### Design HTML/CSS

```html
<div class="satisfaction-guarantee">
  <div class="badge-icon">✓</div>
  <h3>Garantia de Satisfação 100%</h3>
  <p>Se não ficar satisfeito, devolvemos o dinheiro. Sem perguntas.</p>
  <p class="details">Devolução em até 14 dias • Reembolso rápido • Sem custos de envio</p>
</div>
```

#### Posições Recomendadas

1. **Homepage:** Seção de benefícios (junto com envio grátis)
2. **Página de Produto:** Abaixo do botão "Adicionar ao Carrinho"
3. **Checkout:** Próximo ao resumo da encomenda
4. **Rodapé:** Junto com outras garantias

#### Linked Policy

O badge deve estar clicável e levar a:
`/pages/politica-devolucoes`

---

### 4.5 SSL Certificate Indicator

**Indicador de Certificado SSL**

#### Implementação Visual

```html
<div class="ssl-indicator">
  <span class="icon">🔒</span>
  <span class="text">Ligação Segura</span>
</div>
```

#### Informações Técnicas

**Header HTTP:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Certificate Information:**
- Certificado: Wildcard SSL
- Validade: 1-3 anos
- Encriptação: TLS 1.2 ou superior
- Cipher Strength: 256-bit mínimo

#### Verificação

Para clientes verificarem segurança:
1. Clicar no ícone de cadeado no navegador
2. Ver detalhe do certificado
3. Confirmar "Gadget Hub Portugal" ou similar

---

---

## PARTE 5: MATRIZ DE PRIORIDADES

### Tabela Completa de Priorização

| # | Melhoria | Categoria | Esforço | Impacto | Prioridade | ROI | Cronograma |
|---|----------|-----------|---------|---------|-----------|-----|-----------|
| 1 | Categorias em Destaque com Ícones | Homepage | Médio | Alto | P1 | Alto | Semana 1-2 |
| 2 | Barra de Benefícios | Homepage | Baixo | Alto | P1 | Muito Alto | Semana 1 |
| 3 | Página "Sobre Nós" | Conteúdo | Médio | Médio | P2 | Médio | Semana 2-3 |
| 4 | FAQ Completa | Conteúdo | Alto | Alto | P1 | Muito Alto | Semana 3-4 |
| 5 | Política Privacidade (RGPD) | Conformidade | Médio | Alto | P1 | Alto | Semana 1-2 |
| 6 | Termos e Condições | Conformidade | Médio | Alto | P1 | Alto | Semana 1-2 |
| 7 | Política de Devoluções | Conteúdo | Médio | Alto | P1 | Muito Alto | Semana 2-3 |
| 8 | Página de Contacto | Conversão | Médio | Médio | P2 | Médio | Semana 3 |
| 9 | Countdown de Promoções | Homepage | Médio | Médio | P2 | Médio | Semana 4-5 |
| 10 | Secção "Mais Vendidos" | Homepage | Médio | Alto | P1 | Alto | Semana 2-3 |
| 11 | Secção "Novidades" | Homepage | Médio | Médio | P2 | Médio | Semana 3 |
| 12 | Secção "Vistos Recentemente" | Homepage | Médio | Médio | P2 | Médio | Semana 4 |
| 13 | Schema Markup (Organization) | SEO | Médio | Alto | P1 | Alto | Semana 1 |
| 14 | Schema Markup (Product) | SEO | Alto | Muito Alto | P1 | Muito Alto | Semana 2-3 |
| 15 | Schema Markup (BreadcrumbList) | SEO | Baixo | Médio | P2 | Médio | Semana 2 |
| 16 | Sitemap XML | SEO | Baixo | Alto | P1 | Alto | Semana 1 |
| 17 | Meta Titles e Descriptions | SEO | Alto | Muito Alto | P1 | Muito Alto | Semana 3-5 |
| 18 | Otimização de Imagens | Performance | Alto | Alto | P1 | Alto | Semana 2-4 |
| 19 | SSL Certificate Badge | Confiança | Baixo | Médio | P2 | Médio | Semana 1 |
| 20 | Reviews e Testimonials Widget | Confiança | Médio | Muito Alto | P1 | Muito Alto | Semana 2-3 |
| 21 | Garantia de Satisfação Badge | Confiança | Baixo | Médio | P2 | Médio | Semana 1 |
| 22 | Country Flags (Shipping) | UX | Baixo | Médio | P3 | Baixo | Semana 5 |
| 23 | Analytics e Tracking | Dados | Médio | Médio | P2 | Médio | Semana 4-5 |
| 24 | Testes A/B (Conversões) | Otimização | Alto | Alto | P2 | Alto | Semana 5+ |

---

### Legenda de Prioridades

**Esforço:**
- **Baixo:** 1-4 horas
- **Médio:** 1-3 dias
- **Alto:** 1-2 semanas

**Impacto:**
- **Baixo:** <5% melhoria de KPI
- **Médio:** 5-15% melhoria
- **Alto:** 15-30% melhoria
- **Muito Alto:** >30% melhoria

**Prioridade:**
- **P1:** Crítico - Executar na próxima semana
- **P2:** Importante - Executar no próximo mês
- **P3:** Melhoria - Executar quando possível

**ROI (Return On Investment):**
- **Muito Alto:** >5x retorno esperado
- **Alto:** 3-5x retorno
- **Médio:** 1-3x retorno
- **Baixo:** <1x retorno

---

### Plano de Implementação por Fases

#### **FASE 1 (Semana 1-2): Conformidade & Fundações**
Prioridade: CRÍTICA

- [ ] Política de Privacidade (RGPD)
- [ ] Termos e Condições
- [ ] Sitemap XML
- [ ] Schema Markup - Organization
- [ ] Barra de Benefícios
- [ ] SSL Badge
- [ ] Satisfaction Guarantee Badge

**Esforço Total:** 15-20 horas
**Impacto:** Conformidade Legal + Confiança

---

#### **FASE 2 (Semana 2-3): Conteúdo & SEO**
Prioridade: ALTA

- [ ] FAQ Completa
- [ ] Política de Devoluções
- [ ] Sobre Nós
- [ ] Página de Contacto
- [ ] Schema Markup - Product
- [ ] Categorias em Destaque
- [ ] Secção "Mais Vendidos"
- [ ] Reviews Widget

**Esforço Total:** 25-30 horas
**Impacto:** SEO + Conversões + Confiança

---

#### **FASE 3 (Semana 3-5): Otimização & Features**
Prioridade: MÉDIA

- [ ] Meta Titles/Descriptions (todas as páginas)
- [ ] Otimização de Imagens
- [ ] Countdown de Promoções
- [ ] Secção "Novidades"
- [ ] Secção "Vistos Recentemente"
- [ ] Analytics avançado

**Esforço Total:** 30-40 horas
**Impacto:** Performance + Conversões

---

#### **FASE 4 (Semana 5+): Testes & Manutenção**
Prioridade: CONTÍNUA

- [ ] Testes A/B (headlines, CTAs, layout)
- [ ] Análise de comportamento (heatmaps)
- [ ] Otimização de taxa de conversão
- [ ] Melhorias iterativas baseadas em dados

**Esforço Total:** Contínuo
**Impacto:** Melhorias incrementais

---

### Métricas de Sucesso

**Para cada implementação, rastrear:**

| Métrica | Baseline | Meta | Frequência |
|---------|----------|------|-----------|
| Taxa de Conversão | [Baseline] | +20% | Semanal |
| Tempo Médio no Site | [Baseline] | +15% | Semanal |
| Taxa de Rejeição | [Baseline] | -10% | Semanal |
| Páginas/Sessão | [Baseline] | +25% | Semanal |
| Ranking Google (Top 10) | [Baseline] | +50% keywords | Mensal |
| Tráfego Orgânico | [Baseline] | +30% | Mensal |
| Reviews/Ratings | [Baseline] | 4.5+/5 | Mensal |
| Tempo Carregamento (LCP) | [Baseline] | <2.5s | Semanal |

---

### Recursos Necessários

**Pessoal:**
- 1x Desenvolvedor Frontend (50% tempo)
- 1x Especialista SEO (30% tempo)
- 1x Designer UX (20% tempo)
- 1x Content Manager (40% tempo)

**Ferramentas:**
- Google Analytics 4
- Google Search Console
- Ahrefs ou SEMrush
- Figma (design)
- GitHub (versionamento)

**Orçamento Estimado:**
- Desenvolvimento: 2.000-3.000€
- Ferramentas (3 meses): 300-500€
- Testes/QA: 500-1.000€
- **Total Fase 1-3:** 2.800-4.500€

---

### Próximos Passos Imediatos

1. **Hoje:** Aprovação do documento
2. **Amanhã:** Kick-off com equipa
3. **Dia 3:** Início implementação Fase 1
4. **Semana 2:** Revisão de progresso
5. **Semana 4:** Relatório de impacto

---

## CONCLUSÃO

Este documento de melhorias fornece um roteiro completo para otimizar a Gadget Hub de forma estratégica e data-driven. Ao seguir a matriz de prioridades, pode implementar mudanças significativas em 4-6 semanas, com impacto mensurável na conversão, SEO e confiança do cliente.

A abordagem é equilibrada entre:
- ✓ Conformidade legal e segurança
- ✓ Experiência do utilizador
- ✓ Visibilidade nos motores de busca
- ✓ Sinais de confiança e credibilidade
- ✓ Performance técnica

**Recomendação:** Começar pela Fase 1 (conformidade + fundações) e progredir sequencialmente, medindo impacto a cada fase.

---

**Documento Preparado:** Abril 2026
**Versão:** 1.0
**Próxima Revisão:** Setembro 2026
**Responsável:** Équipa de E-commerce

---

*Fim do Documento de Melhorias do Site - Gadget Hub*
