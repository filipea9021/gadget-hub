# Guia Passo-a-Passo — Configurar o Supabase

Este guia vai-te levar do zero ate ter o Data Core funcional.
Tempo estimado: 10-15 minutos.

---

## Passo 1 — Criar conta no Supabase

1. Vai a https://supabase.com
2. Clica em "Start your project" (ou "Sign Up")
3. Regista-te com o teu email ou conta GitHub
4. Confirma o email se necessario

## Passo 2 — Criar um projeto

1. No dashboard, clica em "New Project"
2. Preenche:
   - Nome: `dpll-data-core` (ou o nome que quiseres)
   - Password do banco: escolhe uma password forte e GUARDA-A
   - Regiao: escolhe a mais perto de ti (ex: West EU)
3. Clica em "Create new project"
4. Espera 1-2 minutos enquanto o projeto e criado

## Passo 3 — Copiar as chaves

1. No dashboard do projeto, vai a: Settings → API
2. Copia estes 3 valores:
   - **Project URL** → este e o SUPABASE_URL
   - **anon (public)** → este e o SUPABASE_ANON_KEY
   - **service_role (secret)** → este e o SUPABASE_SERVICE_KEY

⚠️ O service_role e SECRETO. Nunca partilhes este valor.

## Passo 4 — Criar o ficheiro .env

1. Vai a pasta `data-core/scripts/`
2. Copia o ficheiro `.env.example` para `.env`
3. Abre o `.env` e preenche com os valores do Passo 3:

```
SUPABASE_URL=https://abcdefg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJI...
SUPABASE_SERVICE_KEY=eyJhbGciOiJI...
```

## Passo 5 — Criar as tabelas

1. No dashboard do Supabase, vai a: SQL Editor
2. Clica em "New query"
3. Copia TODO o conteudo do ficheiro `setup_supabase.sql`
4. Cola no editor
5. Clica em "Run"
6. Deves ver uma tabela com 3 linhas, todas com 0 registros — isso significa sucesso

## Passo 6 — Criar os buckets de storage

1. No dashboard, vai a: Storage
2. Clica em "New bucket"
3. Cria 3 buckets:
   - `images` → marcar como Public
   - `videos` → marcar como Public
   - `documents` → deixar como Private
4. Para cada bucket publico, vai a Policies e adiciona:
   - Policy name: "Public read access"
   - Allowed operation: SELECT
   - Target roles: anon
   - Policy: `true`

(Isto permite que as URLs publicas funcionem)

## Passo 7 — Instalar dependencias Python

No teu terminal, executa:

```bash
pip install -r data-core/scripts/requirements.txt --break-system-packages
```

## Passo 8 — Testar

Executa o health check:

```bash
cd data-core/scripts && python health_check.py
```

Se tudo estiver correto, vais ver:
```json
{
  "system_status": "healthy",
  "passed": 9,
  "failed": 0
}
```

Se houver problemas, o health check diz exatamente o que falta.

## Passo 9 — Primeiro teste real

Armazena um dado de teste:

```bash
python pipeline.py '{
    "action": "log_action",
    "module": "memory",
    "params": {
        "title": "Data Core inicializado com sucesso",
        "category": "system"
    },
    "origin_skill": "data_core"
}'
```

Se receberes `"status": "success"`, o sistema esta pronto.

---

## Problemas Comuns

| Problema | Solucao |
|----------|---------|
| "Variaveis de ambiente em falta" | Verificar ficheiro .env |
| "Conexao ao Supabase falhou" | Verificar URL e chaves no .env |
| "Tabela nao existe" | Executar setup_supabase.sql no SQL Editor |
| "ModuleNotFoundError" | Executar pip install -r requirements.txt |
| "Bucket not found" | Criar buckets no dashboard → Storage |
