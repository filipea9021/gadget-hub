# Data Core Agent — Plano Tecnico Detalhado

**Projeto:** DPLL — Sistema Modular de Skills para E-commerce/Dropshipping
**Data:** 7 de Abril de 2026
**Versao:** 1.1
**Stack:** Supabase (PostgreSQL + Storage) + Claude Skill + Scripts Python/Node.js

---

## 1. ANALISE CRITICA — O que a conversa original errou

Antes de construir, e essencial corrigir os problemas da ideia original. Aqui estao os pontos que precisam de correcao:

### 1.1 Problemas Identificados

**P1 — Excesso de abstração, falta de concretude.**
A conversa falou em "Decision Engine", "Auto-CEO", "benchmarking automático" — conceitos que soam bem mas nao tem definicao tecnica. Sem schemas concretos, isso nao se transforma em codigo.

**P2 — Escopo descontrolado.**
Tentou definir 10+ skills de uma vez (Product Manager, Dev, Design, SEO, Video, Data Analyst, Automacao, Teste, Monetizacao). Isso paralisa a execucao. O Data Core deve nascer simples e crescer.

**P3 — "system_boot.json" mistura configuracao com comportamento.**
Um unico arquivo JSON nao pode ser ao mesmo tempo: configuracao do sistema, definicao de skills, regras de decisao, e automacoes. Isso precisa ser separado em camadas.

**P4 — Nenhuma estrategia de erros.**
O que acontece quando o upload de imagem falha? Quando o Supabase esta offline? Sem fallback, o sistema inteiro para.

**P5 — Sem modelo de permissoes.**
"Qualquer skill acessa tudo" e um problema. A skill de marketing nao deveria poder apagar dados de memoria do sistema.

**P6 — Metadata de imagens demasiado simples.**
Apenas "nome, origem, uso, data, tags" nao e suficiente. Falta: dimensoes, formato, tamanho, hash (para evitar duplicatas), status de uso, performance.

**P7 — "Inteligencia" prematura.**
Falar em "sistema que decide sozinho" antes de ter um banco de dados funcional e colocar o telhado antes das paredes.

### 1.2 Correcoes Aplicadas Neste Plano

| Problema | Correcao |
|----------|----------|
| P1 — Abstracoes vagas | Schemas concretos com tipos de dados |
| P2 — Escopo enorme | Foco exclusivo no Data Core (3 modulos) |
| P3 — JSON monolitico | Separacao em camadas (config, schema, behavior) |
| P4 — Sem tratamento de erros | Protocolo de resposta com codigos de status |
| P5 — Sem permissoes | Sistema de roles por skill |
| P6 — Metadata pobre | Schema completo de metadata com 15+ campos |
| P7 — IA prematura | Fase 1 = armazenamento puro, IA vem depois |

---

## 2. ARQUITETURA DO DATA CORE

### 2.1 Visao Geral

O Data Core e composto por **3 modulos independentes** que partilham a mesma infraestrutura (Supabase):

```
┌─────────────────────────────────────────────┐
│              DATA CORE AGENT                │
│         (Skill Claude + Scripts)            │
├──────────┬──────────────┬───────────────────┤
│  MEMORY  │    MEDIA     │      DATA         │
│ MANAGER  │   MANAGER    │    MANAGER        │
│          │  (Galeria)   │                   │
├──────────┴──────────────┴───────────────────┤
│          COMMUNICATION LAYER                │
│     (Protocolo padrao de requisicoes)       │
├─────────────────────────────────────────────┤
│              SUPABASE                       │
│   PostgreSQL  │  Storage  │  Auth (futuro)  │
└─────────────────────────────────────────────┘
```

### 2.2 Como funciona na pratica

O Data Core sera **dois componentes trabalhando juntos**:

1. **SKILL.md** — O "cerebro" que o Claude le e segue. Define COMO operar o sistema, QUANDO usar cada modulo, e COMO responder a outras skills.

2. **Scripts** — Codigo real (Python) que executa operacoes no Supabase: upload de imagens, queries ao banco, registro de logs. O Claude chama estes scripts via Bash.

```
Outra Skill pede dados
        ↓
Claude le a Data Core Skill
        ↓
Decide qual modulo usar
        ↓
Executa script Python correspondente
        ↓
Retorna resultado formatado
```

### 2.3 Principio Fundamental

> **Toda informacao que entra ou sai do sistema passa pelo Data Core.**
> Nenhuma skill grava arquivos diretamente. Nenhuma skill acessa o Supabase diretamente.
> O Data Core e o unico porteiro.

---

## 3. MODULO 1 — MEMORY MANAGER

### 3.1 O que faz

Armazena tudo o que o sistema faz, decide e aprende. E o historico vivo do projeto.

### 3.2 Tipos de Memoria

| Tipo | Descricao | Exemplo |
|------|-----------|---------|
| `action_log` | Registro de acoes executadas | "Marketing gerou 3 imagens para campanha X" |
| `decision_log` | Decisoes tomadas e razoes | "Campanha A foi priorizada porque CTR > 5%" |
| `learning` | Padroes aprendidos | "Imagens com fundo azul convertem 20% mais" |
| `error_log` | Falhas e como foram resolvidas | "Upload falhou, retry apos 5s resolveu" |
| `config_snapshot` | Estado do sistema num momento | "Skills ativas: marketing, seo, data_core" |

### 3.3 Schema — Tabela `memory_logs`

```sql
CREATE TABLE memory_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Classificacao
    type TEXT NOT NULL CHECK (type IN (
        'action_log', 'decision_log', 'learning',
        'error_log', 'config_snapshot'
    )),
    category TEXT,                    -- ex: 'marketing', 'seo', 'system'
    severity TEXT DEFAULT 'info' CHECK (severity IN (
        'debug', 'info', 'warning', 'error', 'critical'
    )),

    -- Conteudo
    title TEXT NOT NULL,              -- resumo curto
    description TEXT,                 -- detalhes completos
    metadata JSONB DEFAULT '{}',     -- dados extras flexiveis

    -- Contexto
    origin_skill TEXT NOT NULL,       -- qual skill gerou este registro
    related_ids UUID[],              -- links para outros registros
    session_id TEXT,                  -- sessao em que aconteceu

    -- Busca
    tags TEXT[] DEFAULT '{}'
);

-- Indices para performance
CREATE INDEX idx_memory_type ON memory_logs(type);
CREATE INDEX idx_memory_origin ON memory_logs(origin_skill);
CREATE INDEX idx_memory_created ON memory_logs(created_at DESC);
CREATE INDEX idx_memory_tags ON memory_logs USING GIN(tags);
CREATE INDEX idx_memory_metadata ON memory_logs USING GIN(metadata);
```

### 3.4 Exemplos de Uso

**Registrar uma acao:**
```json
{
    "type": "action_log",
    "category": "marketing",
    "title": "Geracao de imagens para campanha Black Friday",
    "description": "Geradas 5 imagens promocionais com tema escuro",
    "origin_skill": "marketing",
    "tags": ["imagem", "campanha", "black-friday"],
    "metadata": {
        "num_images": 5,
        "campaign_id": "bf-2026",
        "style": "dark-theme"
    }
}
```

**Registrar um aprendizado:**
```json
{
    "type": "learning",
    "category": "marketing",
    "title": "Imagens com pessoas convertem mais",
    "description": "Analise de 30 campanhas: imagens com rostos humanos tiveram CTR 34% superior",
    "origin_skill": "data_core",
    "tags": ["insight", "imagem", "conversao"],
    "metadata": {
        "sample_size": 30,
        "confidence": "high",
        "metric": "CTR",
        "improvement": "+34%"
    }
}
```

---

## 4. MODULO 2 — MEDIA MANAGER (Galeria)

### 4.1 O que faz

Armazena, organiza e distribui todos os ficheiros de midia (imagens, videos, etc.). Este modulo resolve o problema principal: **imagens nunca mais vao para a pasta Downloads**.

### 4.2 Fluxo de Armazenamento

```
Skill gera imagem
      ↓
Chama Data Core: "armazena esta imagem"
      ↓
Script Python:
  1. Faz upload para Supabase Storage
  2. Gera metadata completa
  3. Salva registro na tabela media_files
  4. Retorna URL publica + ID do ficheiro
      ↓
Skill recebe confirmacao + URL
```

### 4.3 Estrutura do Storage (Supabase Buckets)

```
Buckets no Supabase:
├── images/
│   ├── marketing/          ← imagens de campanhas
│   ├── products/           ← fotos de produtos
│   ├── branding/           ← logos, banners
│   └── temp/               ← temporarias (auto-limpeza)
├── videos/
│   ├── marketing/
│   ├── tutorials/
│   └── temp/
└── documents/
    ├── reports/
    └── exports/
```

### 4.4 Schema — Tabela `media_files`

```sql
CREATE TABLE media_files (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Identificacao
    original_name TEXT NOT NULL,       -- nome original do ficheiro
    storage_path TEXT NOT NULL UNIQUE, -- caminho no Supabase Storage
    public_url TEXT,                   -- URL publica para acesso

    -- Tipo e formato
    file_type TEXT NOT NULL CHECK (file_type IN (
        'image', 'video', 'document', 'other'
    )),
    mime_type TEXT,                     -- ex: 'image/png', 'video/mp4'
    file_extension TEXT,               -- ex: 'png', 'mp4', 'pdf'
    file_size_bytes BIGINT,           -- tamanho em bytes
    file_hash TEXT,                    -- SHA-256 para detectar duplicatas

    -- Dimensoes (imagens e videos)
    width INTEGER,
    height INTEGER,
    duration_seconds FLOAT,            -- so para videos

    -- Organizacao
    bucket TEXT NOT NULL,              -- ex: 'images', 'videos'
    folder TEXT NOT NULL,              -- ex: 'marketing', 'products'
    tags TEXT[] DEFAULT '{}',
    category TEXT,                     -- classificacao principal

    -- Origem e contexto
    origin_skill TEXT NOT NULL,        -- qual skill fez upload
    purpose TEXT,                      -- ex: 'instagram-post', 'thumbnail'
    campaign_id TEXT,                  -- referencia a campanha (se aplicavel)
    description TEXT,                  -- descricao do conteudo

    -- Estado
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'archived', 'temp', 'deleted'
    )),
    used_in JSONB DEFAULT '[]',       -- onde ja foi usado
    usage_count INTEGER DEFAULT 0,     -- quantas vezes foi utilizado

    -- Performance (preenchido depois)
    performance_data JSONB DEFAULT '{}' -- CTR, engagement, etc.
);

-- Indices
CREATE INDEX idx_media_type ON media_files(file_type);
CREATE INDEX idx_media_origin ON media_files(origin_skill);
CREATE INDEX idx_media_status ON media_files(status);
CREATE INDEX idx_media_folder ON media_files(bucket, folder);
CREATE INDEX idx_media_tags ON media_files USING GIN(tags);
CREATE INDEX idx_media_hash ON media_files(file_hash);
CREATE INDEX idx_media_created ON media_files(created_at DESC);
```

### 4.5 Protecao contra Duplicatas

Antes de qualquer upload, o sistema calcula o SHA-256 do ficheiro e verifica se ja existe no banco. Se existir, retorna a referencia existente em vez de criar duplicata.

### 4.6 Auto-limpeza

Ficheiros na pasta `temp/` com mais de 7 dias sao automaticamente removidos. Isto sera um script agendado (cron ou scheduled task).

---

## 5. MODULO 3 — DATA MANAGER

### 5.1 O que faz

Armazena dados estruturados do sistema: metricas, resultados de campanhas, dados de performance, configuracoes.

### 5.2 Schema — Tabela `system_data`

```sql
CREATE TABLE system_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Classificacao
    data_type TEXT NOT NULL,           -- ex: 'metric', 'config', 'result'
    namespace TEXT NOT NULL,           -- ex: 'marketing', 'seo', 'system'
    key TEXT NOT NULL,                 -- identificador unico dentro do namespace

    -- Conteudo
    value JSONB NOT NULL,             -- os dados em si (flexivel)
    description TEXT,

    -- Versionamento simples
    version INTEGER DEFAULT 1,

    -- Constraint de unicidade
    UNIQUE(namespace, key)
);

-- Indice
CREATE INDEX idx_data_namespace ON system_data(namespace);
CREATE INDEX idx_data_type ON system_data(data_type);
```

### 5.3 Exemplos de Dados

**Configuracao do sistema:**
```json
{
    "data_type": "config",
    "namespace": "system",
    "key": "active_skills",
    "value": {
        "skills": ["marketing", "data_core", "site_creator"],
        "last_updated": "2026-04-07"
    }
}
```

**Resultado de campanha:**
```json
{
    "data_type": "result",
    "namespace": "marketing",
    "key": "campaign_bf_2026_results",
    "value": {
        "impressions": 15000,
        "clicks": 450,
        "ctr": 3.0,
        "conversions": 23,
        "cost": 150.00,
        "revenue": 920.00
    }
}
```

---

## 6. PROTOCOLO DE COMUNICACAO ENTRE SKILLS

### 6.1 Formato Padrao de Requisicao

Toda comunicacao com o Data Core segue este formato:

```json
{
    "api_version": "1.0",
    "action": "string",
    "module": "memory | media | data",
    "params": { },
    "origin_skill": "string",
    "request_id": "string (opcional)"
}
```

### 6.2 Formato Padrao de Resposta

```json
{
    "status": "success | error | partial",
    "code": 200,
    "message": "string",
    "data": { },
    "request_id": "string"
}
```

### 6.3 Codigos de Status

| Codigo | Significado |
|--------|-------------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisicao invalida (parametros errados) |
| 404 | Nao encontrado |
| 403 | Sem permissao para esta operacao |
| 409 | Conflito (ex: duplicata) |
| 413 | Ficheiro excede limite de tamanho |
| 500 | Erro interno |
| 503 | Servico indisponivel (Supabase offline, apos retry) |
| 507 | Sem espaco (storage ou disco cheio) |

### 6.4 Acoes Disponiveis

**Memory Manager:**

| Acao | Descricao | Parametros obrigatorios |
|------|-----------|------------------------|
| `log_action` | Registrar uma acao | title, origin_skill |
| `log_decision` | Registrar decisao | title, description, origin_skill |
| `log_learning` | Registrar aprendizado | title, description, origin_skill |
| `log_error` | Registrar erro | title, severity, origin_skill |
| `log_config` | Registrar estado do sistema | title, origin_skill |
| `search_memory` | Buscar no historico | query (texto ou filtros) |
| `get_recent` | Ultimos N registros | limit, type (opcional) |

Nota: O campo `type` na tabela e preenchido automaticamente com base na acao chamada:
- `log_action` → type = `action_log`
- `log_decision` → type = `decision_log`
- `log_learning` → type = `learning`
- `log_error` → type = `error_log`
- `log_config` → type = `config_snapshot`

**Media Manager:**

| Acao | Descricao | Parametros obrigatorios |
|------|-----------|------------------------|
| `store_image` | Armazenar imagem | file_path, folder, origin_skill (max 10MB) |
| `store_video` | Armazenar video | file_path, folder, origin_skill (max 50MB) |
| `get_media` | Buscar midia por ID | id |
| `search_media` | Buscar por filtros | tags, folder, type, etc. |
| `list_media` | Listar midia de pasta | bucket, folder |
| `update_media` | Atualizar metadata | id, campos a atualizar |
| `archive_media` | Arquivar ficheiro | id |
| `get_media_url` | Obter URL publica | id |

**Data Manager:**

| Acao | Descricao | Parametros obrigatorios |
|------|-----------|------------------------|
| `store_data` | Guardar dado | namespace, key, value |
| `get_data` | Buscar dado | namespace, key |
| `update_data` | Atualizar dado | namespace, key, value |
| `delete_data` | Remover dado | namespace, key |
| `list_data` | Listar dados de namespace | namespace |

### 6.5 Exemplo Completo de Interacao

**Skill de Marketing quer armazenar uma imagem:**

Requisicao:
```json
{
    "action": "store_image",
    "module": "media",
    "params": {
        "file_path": "/tmp/campanha_promo_01.png",
        "folder": "marketing",
        "tags": ["promocao", "black-friday", "instagram"],
        "purpose": "instagram-post",
        "campaign_id": "bf-2026",
        "description": "Banner promocional Black Friday com fundo escuro"
    },
    "origin_skill": "marketing"
}
```

Resposta:
```json
{
    "status": "success",
    "code": 201,
    "message": "Imagem armazenada com sucesso",
    "data": {
        "id": "a1b2c3d4-...",
        "storage_path": "images/marketing/campanha_promo_01.png",
        "public_url": "https://xxxxx.supabase.co/storage/v1/object/public/images/marketing/campanha_promo_01.png",
        "file_size_bytes": 245760,
        "file_hash": "sha256:abc123..."
    }
}
```

---

## 7. ESTRUTURA DE FICHEIROS DO PROJETO

```
data-core/
├── SKILL.md                              ← Instrucoes para o Claude
├── scripts/
│   ├── requirements.txt                  ← Dependencias com versoes fixas
│   ├── .env.example                      ← Template de variaveis de ambiente
│   ├── config.py                         ← Conexao Supabase + constantes
│   ├── validators.py                     ← Validacao (params, ficheiros, permissoes)
│   ├── permissions.py                    ← Mapa de permissoes por skill
│   ├── retry.py                          ← Logica de retry e cache
│   ├── memory_manager.py                 ← Operacoes de memoria
│   ├── media_manager.py                  ← Operacoes de midia
│   ├── data_manager.py                   ← Operacoes de dados
│   ├── health_check.py                   ← Verificacao completa do sistema
│   ├── auto_repair.py                    ← Auto-reparacao
│   ├── integrity_check.py               ← Consistencia storage <-> banco
│   ├── cleanup.py                        ← Limpeza de temp e cache
│   ├── pipeline.py                       ← Pipeline de execucao segura
│   ├── utils.py                          ← Funcoes auxiliares (hash, format, etc.)
│   └── setup_supabase.sql               ← SQL completo
├── references/
│   ├── api_protocol.md                   ← Protocolo completo
│   ├── schemas.md                        ← Schemas detalhados
│   ├── error_codes.md                    ← Todos os codigos de erro
│   └── troubleshooting.md               ← Guia de resolucao de problemas
└── tests/
    ├── test_memory.py
    ├── test_media.py
    ├── test_data.py
    ├── test_validators.py
    ├── test_permissions.py
    └── test_health_check.py
```

> **Documento complementar:** Ver `DATA_CORE_BLINDAGEM_ERROS.md` para o sistema
> completo de prevencao, detecao e resolucao de TODAS as falhas possiveis,
> incluindo codigo de cada protecao e o pipeline de execucao segura.

---

## 8. PERMISSOES POR SKILL

### 8.1 Modelo de Acesso

Cada skill tem um nivel de acesso definido:

| Skill | Memory | Media (leitura) | Media (escrita) | Data |
|-------|--------|-----------------|-----------------|------|
| marketing | log + read | sim | sim (pasta marketing/) | read propria namespace |
| site_creator | log + read | sim | sim (pasta products/) | read propria namespace |
| data_core | total | total | total | total |
| seo (futuro) | log + read | sim | nao | read propria namespace |

### 8.2 Regra de Ouro

> Uma skill so pode ESCREVER na sua propria area.
> Uma skill pode LER de qualquer area (com justificacao).
> So o Data Core pode APAGAR dados.

### 8.3 Como as Permissoes sao Aplicadas

A validacao de permissoes acontece dentro dos scripts Python, no inicio de cada operacao:

1. O script recebe `origin_skill` na requisicao
2. Consulta uma tabela de permissoes (ou config local) para verificar se a skill tem acesso
3. Se permitido → executa a operacao
4. Se negado → retorna erro com code `403` e message explicativa

Isto sera implementado na **Fase 2** como parte do modulo `utils.py` (funcao `check_permission`).

---

## 9. CONFIGURACAO DO SUPABASE

### 9.1 O que criar no Supabase

1. **Projeto** — Criar projeto no supabase.com
2. **Tabelas** — Executar o SQL da seccao 3, 4 e 5
3. **Storage Buckets:**
   - `images` (publico para leitura)
   - `videos` (publico para leitura)
   - `documents` (privado)
4. **API Keys** — Guardar:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (para leitura publica)
   - `SUPABASE_SERVICE_KEY` (para escrita — NUNCA expor)

### 9.2 Seguranca

- A `SERVICE_KEY` fica apenas nos scripts Python, nunca no SKILL.md
- As URLs publicas de imagens podem ser partilhadas livremente
- Dados sensíveis ficam em buckets privados

---

## 10. PLANO DE IMPLEMENTACAO (Fases)

### Fase 1 — Fundacao (o que construir PRIMEIRO)

**Objetivo:** Sistema funcional minimo que armazena e recupera dados.

1. Criar projeto no Supabase
2. Executar SQL para criar as 3 tabelas
3. Criar buckets de storage
4. Escrever `config.py` com conexao ao Supabase
5. Escrever `memory_manager.py` (log + search)
6. Escrever `media_manager.py` (upload + search + get_url)
7. Escrever `data_manager.py` (store + get + list)
8. Escrever testes basicos
9. Escrever SKILL.md inicial

**Resultado:** Consigo armazenar uma imagem, registrar uma acao, e buscar dados.

### Fase 2 — Robustez

**Objetivo:** Sistema confiavel com tratamento de erros.

1. Adicionar tratamento de erros em todos os scripts
2. Implementar detecao de duplicatas (hash)
3. Adicionar validacao de parametros
4. Criar sistema de retry para falhas de rede
5. Implementar auto-limpeza de ficheiros temporarios (pasta temp/, >7 dias)
6. Implementar sistema de permissoes (`check_permission` em utils.py)
7. Adicionar validacao de tamanho de ficheiros (10MB imagens, 50MB videos)
8. Testes mais completos

**Resultado:** Sistema que nao quebra com erros comuns e respeita permissoes.

### Fase 3 — Inteligencia Basica

**Objetivo:** Sistema que organiza e sugere.

1. Busca por tags inteligente
2. Sugestao de tags automatica (baseada em nome/tipo)
3. Estatisticas de uso (imagens mais usadas, etc.)
4. Dashboard simples de estado do sistema

**Resultado:** Sistema que ajuda a encontrar e organizar conteudo.

### Fase 4 — Integracao

**Objetivo:** Plugar o Data Core no sistema principal.

1. Testar comunicacao com skill de Marketing
2. Testar comunicacao com skill de Criacao de Site
3. Ajustar permissoes
4. Documentar API para as outras skills

**Resultado:** Data Core funcionando como agente dentro do ecossistema.

---

## 11. RISCOS E MITIGACOES

| Risco | Impacto | Mitigacao | Documento |
|-------|---------|-----------|-----------|
| Supabase fora do ar | Sistema inteiro para | Cache local + retry 3x | BLINDAGEM F2.1 |
| Imagens muito grandes | Upload lento/falha | Limitar 10MB + validacao magic bytes | BLINDAGEM F3.2 |
| Tabelas ficam enormes | Queries lentas | Indices + paginacao obrigatoria | Plano seccao 3-5 |
| Skill tenta acessar direto | Dados inconsistentes | Permissoes + validacao em pipeline | BLINDAGEM F4.3 |
| Perda de credenciais | Seguranca comprometida | .env + check_env() obrigatorio | BLINDAGEM F1.4 |
| Duplicatas de ficheiros | Espaco desperdicado | SHA-256 + comparacao tamanho | BLINDAGEM F3.3 |
| Dados corrompidos | Inconsistencia banco/storage | Upload atomico + rollback | BLINDAGEM F2.6 |
| Ficheiros orfaos | Espaco desperdicado | integrity_check() periodico | BLINDAGEM F2.7 |
| Parametros invalidos | Operacoes erradas | Validacao schema por acao | BLINDAGEM F3.1 |
| Storage cheio | Uploads falham | Monitorizar uso + alertas 80% | BLINDAGEM F2.4 |
| Erro nao previsto | Sistema para | safe_execute() global | BLINDAGEM F3.5 |

> **Ver documento completo:** `DATA_CORE_BLINDAGEM_ERROS.md` com TODAS as protecoes detalhadas.

---

## 12. DEPENDENCIAS TECNICAS

### Python

```
supabase-py>=2.0.0       # Cliente Supabase para Python
python-dotenv>=1.0.0      # Variaveis de ambiente
Pillow>=10.0.0            # Processamento de imagens (dimensoes, etc.)
hashlib                   # Ja incluso no Python (para hashes)
```

### Supabase (plano gratuito inclui)

- 500MB de base de dados
- 1GB de storage
- 50,000 requests/mes
- Suficiente para comecar

---

## 13. RESUMO EXECUTIVO

**O que estamos construindo:**
Um sistema centralizado de dados, memoria e galeria de midia que funciona como skill independente e depois sera integrado como agente no sistema principal.

**O que NAO estamos construindo (agora):**
- Sistema de criacao de sites (ja existe)
- Skill de marketing (ja em desenvolvimento)
- Motor de decisao automatica (vem no futuro)
- Interface grafica / dashboard (vem no futuro)

**Tecnologia escolhida:** Supabase (nuvem) + Python (scripts) + Claude Skill (operador)

**Formato:** Skill do Claude que opera scripts Python que interagem com o Supabase.

**Prioridade de construcao:** Memory Manager → Media Manager → Data Manager → Testes → Integracao
