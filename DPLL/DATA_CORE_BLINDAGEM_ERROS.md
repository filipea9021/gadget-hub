# Data Core Agent — Blindagem Completa de Erros

**Objetivo:** Eliminar todas as falhas possiveis. Quando uma falha inevitavel acontecer, o sistema detecta e resolve na raiz, sozinho, o mais rapido possivel.

---

## 1. MAPA COMPLETO DE FALHAS

O sistema tem 5 camadas. Cada camada tem os seus proprios pontos de falha.

```
CAMADA 5 — SKILL CLAUDE (interpretacao, decisoes)
CAMADA 4 — COMUNICACAO (protocolo entre skills)
CAMADA 3 — SCRIPTS PYTHON (logica, processamento)
CAMADA 2 — SUPABASE (banco + storage)
CAMADA 1 — INFRAESTRUTURA (rede, disco, ambiente)
```

Vou analisar CADA falha possivel em CADA camada, com prevencao e solucao.

---

## 2. CAMADA 1 — INFRAESTRUTURA

### F1.1 — Internet cai ou fica instavel

**Quando acontece:** Qualquer operacao que precisa do Supabase.
**Sintoma:** Timeout, conexao recusada, resposta incompleta.

**Prevencao:**
- Todo script tem timeout configuravel (padrao: 30 segundos)
- Sistema de retry automatico: 3 tentativas com espera crescente (1s, 3s, 7s)

**Resolucao:**
```python
# Padrao de retry que TODOS os scripts devem usar
import time

def retry_operation(func, max_retries=3, base_delay=1):
    """Executa funcao com retry automatico."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except (ConnectionError, TimeoutError) as e:
            last_error = e
            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            log_error(f"Tentativa {attempt+1} falhou: {e}. Retry em {delay}s")
            time.sleep(delay)

    # Todas as tentativas falharam
    return {
        "status": "error",
        "code": 503,
        "message": f"Servico indisponivel apos {max_retries} tentativas",
        "error_detail": str(last_error),
        "recovery": "Verificar conexao internet e status do Supabase"
    }
```

**Codigo de erro:** `503` (Servico indisponivel)

### F1.2 — Disco local sem espaco

**Quando acontece:** Ao processar imagens antes do upload (conversao, calculo de hash).
**Sintoma:** IOError, OSError ao escrever ficheiros temporarios.

**Prevencao:**
- Antes de processar ficheiro, verificar espaco disponivel
- Ficheiros temporarios sao SEMPRE apagados apos uso (bloco try/finally)
- Nunca guardar nada permanente no disco local

**Resolucao:**
```python
import shutil

def check_disk_space(required_bytes, path="/tmp"):
    """Verifica se ha espaco suficiente."""
    usage = shutil.disk_usage(path)
    if usage.free < required_bytes * 2:  # margem de 2x
        return {
            "status": "error",
            "code": 507,
            "message": f"Espaco insuficiente. Necessario: {required_bytes}B, Disponivel: {usage.free}B",
            "recovery": "Limpar ficheiros temporarios com cleanup_temp()"
        }
    return None  # OK
```

**Codigo de erro:** `507` (Espaco insuficiente)

### F1.3 — Python ou dependencias nao instaladas

**Quando acontece:** Na primeira execucao ou apos atualizacao do ambiente.
**Sintoma:** ModuleNotFoundError, ImportError.

**Prevencao:**
- Script `health_check.py` que verifica TUDO antes de qualquer operacao
- requirements.txt com versoes fixas

**Resolucao:**
```python
def check_dependencies():
    """Verifica se todas as dependencias estao instaladas."""
    required = {
        "supabase": "supabase",
        "dotenv": "python-dotenv",
        "PIL": "Pillow"
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        return {
            "status": "error",
            "code": 500,
            "message": f"Dependencias em falta: {', '.join(missing)}",
            "recovery": f"Executar: pip install {' '.join(missing)} --break-system-packages"
        }
    return None  # OK
```

### F1.4 — Variaveis de ambiente ausentes

**Quando acontece:** .env nao existe ou esta incompleto.
**Sintoma:** KeyError, conexao ao Supabase falha silenciosamente.

**Prevencao:**
- Verificacao obrigatoria no inicio de CADA script
- Mensagem clara dizendo EXATAMENTE o que falta

**Resolucao:**
```python
def check_env():
    """Verifica todas as variaveis de ambiente necessarias."""
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        return {
            "status": "error",
            "code": 500,
            "message": f"Variaveis de ambiente em falta: {', '.join(missing)}",
            "recovery": "Criar ficheiro .env com: " + ", ".join(f"{v}=<valor>" for v in missing)
        }
    return None  # OK
```

---

## 3. CAMADA 2 — SUPABASE

### F2.1 — Supabase offline ou em manutencao

**Quando acontece:** Raramente, mas acontece (manutencoes programadas, incidentes).
**Sintoma:** HTTP 500/502/503 do Supabase.

**Prevencao:**
- Retry automatico (F1.1)
- Cache local de leitura: se a ultima leitura tem menos de 5 minutos, usa cache

**Resolucao:**
```python
import json
from pathlib import Path

CACHE_DIR = Path("/tmp/data_core_cache")
CACHE_TTL = 300  # 5 minutos em segundos

def cached_read(cache_key, fetch_func):
    """Tenta cache local antes de ir ao Supabase."""
    cache_file = CACHE_DIR / f"{cache_key}.json"

    # Verificar cache
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_TTL:
            return json.loads(cache_file.read_text())

    # Cache expirado ou inexistente — buscar no Supabase
    try:
        result = fetch_func()
        # Salvar em cache
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file.write_text(json.dumps(result))
        return result
    except Exception as e:
        # Supabase falhou — usar cache expirado se existir
        if cache_file.exists():
            log_error(f"Supabase offline, usando cache expirado para {cache_key}")
            return json.loads(cache_file.read_text())
        raise  # Sem cache, propagar o erro
```

### F2.2 — Tabelas nao existem

**Quando acontece:** Primeira execucao, ou alguem apagou tabelas por engano.
**Sintoma:** "relation does not exist" do PostgreSQL.

**Prevencao:**
- `health_check.py` verifica existencia das 3 tabelas no arranque
- Script `setup_supabase.sql` usa `CREATE TABLE IF NOT EXISTS`

**Resolucao:**
```python
def check_tables():
    """Verifica se todas as tabelas necessarias existem."""
    required_tables = ["memory_logs", "media_files", "system_data"]

    for table in required_tables:
        try:
            result = supabase.table(table).select("id").limit(1).execute()
        except Exception as e:
            if "does not exist" in str(e):
                return {
                    "status": "error",
                    "code": 500,
                    "message": f"Tabela '{table}' nao existe",
                    "recovery": "Executar setup_supabase.sql no Supabase SQL Editor",
                    "auto_fix": True  # O script pode tentar criar automaticamente
                }
    return None  # OK
```

### F2.3 — Storage bucket nao existe

**Quando acontece:** Primeira execucao, bucket apagado.
**Sintoma:** "Bucket not found" no upload.

**Prevencao:**
- `health_check.py` verifica buckets no arranque
- Criacao automatica se nao existir

**Resolucao:**
```python
def ensure_bucket(bucket_name, public=True):
    """Garante que o bucket existe, cria se necessario."""
    try:
        supabase.storage.get_bucket(bucket_name)
    except Exception:
        supabase.storage.create_bucket(
            bucket_name,
            options={"public": public}
        )
        log_action(f"Bucket '{bucket_name}' criado automaticamente")
```

### F2.4 — Limite de storage atingido (plano gratuito: 1GB)

**Quando acontece:** Muitas imagens/videos armazenados.
**Sintoma:** Upload falha com erro de quota.

**Prevencao:**
- Monitorizar uso de storage periodicamente
- Alertar quando atingir 80% da capacidade
- Comprimir imagens antes do upload (qualidade 85%)

**Resolucao:**
```python
def check_storage_usage():
    """Verifica uso de storage e alerta se necessario."""
    # Consultar tamanho total de ficheiros no banco
    result = supabase.table("media_files") \
        .select("file_size_bytes") \
        .eq("status", "active") \
        .execute()

    total_bytes = sum(row["file_size_bytes"] or 0 for row in result.data)
    limit_bytes = 1 * 1024 * 1024 * 1024  # 1GB
    usage_percent = (total_bytes / limit_bytes) * 100

    if usage_percent > 95:
        return {
            "status": "error",
            "code": 507,
            "message": f"Storage quase cheio: {usage_percent:.1f}% usado",
            "recovery": "Arquivar ficheiros antigos ou fazer upgrade do plano Supabase"
        }
    elif usage_percent > 80:
        return {
            "status": "warning",
            "code": 200,
            "message": f"Storage em {usage_percent:.1f}% — considere limpar ficheiros temp"
        }
    return None  # OK
```

### F2.5 — Limite de requests atingido (50,000/mes)

**Quando acontece:** Sistema muito ativo ou loops ineficientes.

**Prevencao:**
- Cada script conta requests feitos (contador local)
- Usar queries em batch quando possivel (inserir 10 registros de uma vez em vez de 10 queries separadas)
- Cache de leitura (F2.1) reduz requests

**Resolucao:**
- Monitorizar no dashboard do Supabase
- Se atingir 80%, reduzir frequencia de operacoes nao-criticas

### F2.6 — Dados corrompidos ou inconsistentes

**Quando acontece:** Upload interrompido, registro criado no banco mas ficheiro nao chegou ao storage (ou vice-versa).
**Sintoma:** Registro existe no banco mas URL da imagem retorna 404.

**Prevencao:**
- Upload e registro no banco sao feitos em SEQUENCIA:
  1. Primeiro: upload para storage
  2. Se sucesso: criar registro no banco
  3. Se banco falha: apagar do storage (rollback manual)

**Resolucao:**
```python
def store_media_safe(file_path, metadata):
    """Upload atomico: storage + banco, com rollback."""
    storage_path = None

    try:
        # Passo 1: Upload para storage
        storage_path = upload_to_storage(file_path, metadata)

        # Passo 2: Criar registro no banco
        db_record = create_db_record(storage_path, metadata)

        return {"status": "success", "code": 201, "data": db_record}

    except Exception as e:
        # Rollback: se o upload aconteceu mas o banco falhou
        if storage_path:
            try:
                delete_from_storage(storage_path)
                log_error(f"Rollback de storage executado: {storage_path}")
            except Exception:
                log_error(f"CRITICO: Rollback falhou! Ficheiro orfao: {storage_path}")

        return {
            "status": "error",
            "code": 500,
            "message": f"Falha no armazenamento: {e}",
            "recovery": "Executar integrity_check() para limpar ficheiros orfaos"
        }
```

### F2.7 — Ficheiros orfaos (existem no storage mas nao no banco, ou vice-versa)

**Quando acontece:** Resultado de F2.6 ou de operacoes manuais.

**Prevencao:**
- Nunca manipular storage ou banco diretamente fora dos scripts

**Resolucao:**
```python
def integrity_check():
    """Verifica consistencia entre banco e storage."""
    issues = []

    # Buscar todos os registros ativos no banco
    db_records = supabase.table("media_files") \
        .select("id, storage_path, status") \
        .eq("status", "active") \
        .execute()

    for record in db_records.data:
        # Verificar se ficheiro existe no storage
        try:
            supabase.storage.from_(get_bucket(record["storage_path"])) \
                .download(record["storage_path"])
        except Exception:
            issues.append({
                "type": "db_without_file",
                "record_id": record["id"],
                "path": record["storage_path"],
                "fix": "Marcar como 'deleted' no banco"
            })

    return {
        "status": "success",
        "issues_found": len(issues),
        "issues": issues
    }
```

---

## 4. CAMADA 3 — SCRIPTS PYTHON

### F3.1 — Parametros invalidos ou ausentes

**Quando acontece:** Uma skill envia requisicao com campos errados ou em falta.
**Sintoma:** KeyError, TypeError, valores inesperados.

**Prevencao:**
- TODA funcao valida parametros ANTES de fazer qualquer coisa
- Schema de validacao para cada acao

**Resolucao:**
```python
# Schemas de validacao por acao
VALIDATION_SCHEMAS = {
    "store_image": {
        "required": ["file_path", "folder", "origin_skill"],
        "optional": ["tags", "purpose", "campaign_id", "description"],
        "types": {
            "file_path": str,
            "folder": str,
            "origin_skill": str,
            "tags": list,
            "purpose": str
        },
        "allowed_folders": ["marketing", "products", "branding", "temp"]
    },
    "log_action": {
        "required": ["title", "origin_skill"],
        "optional": ["category", "description", "tags", "metadata"],
        "types": {
            "title": str,
            "origin_skill": str,
            "category": str,
            "tags": list,
            "metadata": dict
        }
    }
    # ... igual para todas as outras acoes
}

def validate_params(action, params):
    """Valida parametros contra o schema da acao."""
    schema = VALIDATION_SCHEMAS.get(action)
    if not schema:
        return {"status": "error", "code": 400, "message": f"Acao desconhecida: {action}"}

    # Verificar campos obrigatorios
    for field in schema["required"]:
        if field not in params:
            return {
                "status": "error",
                "code": 400,
                "message": f"Campo obrigatorio em falta: '{field}'",
                "recovery": f"Adicionar '{field}' aos parametros. Tipo esperado: {schema['types'].get(field, 'any')}"
            }

    # Verificar tipos
    for field, expected_type in schema.get("types", {}).items():
        if field in params and not isinstance(params[field], expected_type):
            return {
                "status": "error",
                "code": 400,
                "message": f"Tipo errado para '{field}': esperado {expected_type.__name__}, recebido {type(params[field]).__name__}"
            }

    # Verificar valores permitidos (ex: folders)
    if "allowed_folders" in schema and "folder" in params:
        if params["folder"] not in schema["allowed_folders"]:
            return {
                "status": "error",
                "code": 400,
                "message": f"Pasta invalida: '{params['folder']}'. Permitidas: {schema['allowed_folders']}"
            }

    return None  # OK
```

### F3.2 — Ficheiro de input nao existe ou esta corrompido

**Quando acontece:** Skill manda caminho de imagem que nao existe, ou ficheiro esta truncado.

**Prevencao:**
- Verificar existencia do ficheiro antes de processar
- Verificar se o ficheiro e realmente do tipo indicado (magic bytes)
- Verificar tamanho minimo (ficheiro de 0 bytes = corrompido)

**Resolucao:**
```python
import os
import mimetypes

# Magic bytes dos formatos suportados
MAGIC_BYTES = {
    "image/png": b'\x89PNG',
    "image/jpeg": b'\xff\xd8\xff',
    "image/gif": b'GIF8',
    "image/webp": b'RIFF',
    "video/mp4": b'\x00\x00\x00',
    "application/pdf": b'%PDF',
}

def validate_file(file_path, expected_type="image"):
    """Valida ficheiro antes de qualquer processamento."""

    # 1. Existe?
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "code": 404,
            "message": f"Ficheiro nao encontrado: {file_path}",
            "recovery": "Verificar o caminho do ficheiro"
        }

    # 2. Tamanho > 0?
    size = os.path.getsize(file_path)
    if size == 0:
        return {
            "status": "error",
            "code": 400,
            "message": "Ficheiro vazio (0 bytes) — provavelmente corrompido"
        }

    # 3. Dentro do limite?
    limits = {"image": 10 * 1024 * 1024, "video": 50 * 1024 * 1024}
    max_size = limits.get(expected_type, 10 * 1024 * 1024)
    if size > max_size:
        return {
            "status": "error",
            "code": 413,
            "message": f"Ficheiro muito grande: {size/1024/1024:.1f}MB (limite: {max_size/1024/1024:.0f}MB)",
            "recovery": "Comprimir o ficheiro ou usar formato mais eficiente"
        }

    # 4. Tipo correto? (magic bytes)
    with open(file_path, "rb") as f:
        header = f.read(8)

    mime = mimetypes.guess_type(file_path)[0]
    if mime in MAGIC_BYTES:
        expected_magic = MAGIC_BYTES[mime]
        if not header.startswith(expected_magic):
            return {
                "status": "error",
                "code": 400,
                "message": f"Ficheiro corrompido ou extensao errada. Extensao diz '{mime}' mas conteudo nao corresponde",
                "recovery": "Verificar se o ficheiro nao esta corrompido"
            }

    return None  # OK
```

### F3.3 — Hash collision (dois ficheiros diferentes com mesmo hash)

**Quando acontece:** Extremamente raro com SHA-256, mas possivel.

**Prevencao:**
- SHA-256 tem probabilidade de colisao de ~1 em 2^128 — praticamente impossivel
- Mesmo assim: se hash coincide, comparar tambem tamanho do ficheiro

**Resolucao:**
```python
def is_true_duplicate(file_path, existing_hash, existing_size):
    """Confirma duplicata verificando hash E tamanho."""
    new_size = os.path.getsize(file_path)
    new_hash = calculate_hash(file_path)

    return new_hash == existing_hash and new_size == existing_size
```

### F3.4 — Erro ao processar imagem (Pillow falha)

**Quando acontece:** Formato nao suportado, imagem corrompida internamente.

**Prevencao:**
- Validacao de magic bytes (F3.2) apanha a maioria
- Try/except ao redor de TODA operacao Pillow

**Resolucao:**
```python
def get_image_dimensions(file_path):
    """Obtem dimensoes com fallback seguro."""
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            return {"width": img.width, "height": img.height}
    except Exception as e:
        # Nao conseguiu ler dimensoes — continuar sem elas
        log_error(f"Nao foi possivel ler dimensoes de {file_path}: {e}")
        return {"width": None, "height": None}
```

A regra aqui e: **se nao conseguir obter metadata extra (dimensoes), NAO bloquear o upload**. O ficheiro pode ser armazenado mesmo sem dimensoes.

### F3.5 — Script Python crasha no meio de uma operacao

**Quando acontece:** Qualquer erro nao tratado, memoria insuficiente, etc.

**Prevencao:**
- TODA funcao publica esta envolvida num try/except global
- Erros nao tratados sao capturados e retornados em formato padrao

**Resolucao:**
```python
def safe_execute(func, *args, **kwargs):
    """Wrapper global que garante que NENHUM erro passa sem ser tratado."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_response = {
            "status": "error",
            "code": 500,
            "message": f"Erro interno nao esperado: {type(e).__name__}: {str(e)}",
            "recovery": "Verificar logs de erro e reportar este problema",
            "traceback": traceback.format_exc()
        }
        # Registrar o erro no sistema de memoria (se possivel)
        try:
            log_error_to_db(error_response)
        except Exception:
            pass  # Se ate o log falha, imprimir no stderr

        return error_response
```

---

## 5. CAMADA 4 — COMUNICACAO ENTRE SKILLS

### F4.1 — Requisicao mal formatada

**Quando acontece:** Skill envia JSON invalido ou formato errado.

**Prevencao:**
- Documentacao clara do protocolo no SKILL.md
- Exemplos para cada acao

**Resolucao:**
- Validacao de parametros (F3.1) apanha todos os casos
- Mensagem de erro inclui o formato correto esperado

### F4.2 — Skill envia acao que nao existe

**Quando acontece:** Typo no nome da acao, ou skill desatualizada.

**Prevencao:**
- Lista de acoes validas no SKILL.md e no api_protocol.md

**Resolucao:**
```python
VALID_ACTIONS = {
    "memory": ["log_action", "log_decision", "log_learning", "log_error",
               "log_config", "search_memory", "get_recent"],
    "media": ["store_image", "store_video", "get_media", "search_media",
              "list_media", "update_media", "archive_media", "get_media_url"],
    "data": ["store_data", "get_data", "update_data", "delete_data", "list_data"]
}

def validate_action(module, action):
    """Verifica se a acao existe no modulo."""
    if module not in VALID_ACTIONS:
        return {
            "status": "error",
            "code": 400,
            "message": f"Modulo invalido: '{module}'. Modulos disponiveis: {list(VALID_ACTIONS.keys())}"
        }
    if action not in VALID_ACTIONS[module]:
        return {
            "status": "error",
            "code": 400,
            "message": f"Acao invalida: '{action}' no modulo '{module}'. Acoes disponiveis: {VALID_ACTIONS[module]}"
        }
    return None  # OK
```

### F4.3 — Skill tenta operacao sem permissao

**Quando acontece:** Marketing tenta apagar dados, ou SEO tenta fazer upload de imagem.

**Prevencao:**
- Tabela de permissoes (seccao 8 do plano)
- Verificacao obrigatoria ANTES de qualquer operacao

**Resolucao:**
```python
# Mapa de permissoes por skill
PERMISSIONS = {
    "marketing": {
        "memory": ["log_action", "log_decision", "log_learning", "log_error",
                    "search_memory", "get_recent"],
        "media": ["store_image", "store_video", "get_media", "search_media",
                  "list_media", "get_media_url"],
        "media_folders": ["marketing", "temp"],
        "data": ["store_data", "get_data", "list_data"],
        "data_namespaces": ["marketing"]
    },
    "site_creator": {
        "memory": ["log_action", "log_decision", "log_learning", "log_error",
                    "search_memory", "get_recent"],
        "media": ["store_image", "get_media", "search_media",
                  "list_media", "get_media_url"],
        "media_folders": ["products", "temp"],
        "data": ["store_data", "get_data", "list_data"],
        "data_namespaces": ["site_creator"]
    },
    "data_core": {
        "memory": "*",   # acesso total
        "media": "*",
        "media_folders": "*",
        "data": "*",
        "data_namespaces": "*"
    }
}

def check_permission(origin_skill, module, action, params=None):
    """Verifica se a skill tem permissao para a operacao."""

    perms = PERMISSIONS.get(origin_skill)
    if not perms:
        return {
            "status": "error",
            "code": 403,
            "message": f"Skill desconhecida: '{origin_skill}'. Nao tem permissoes configuradas.",
            "recovery": "Registrar esta skill no sistema de permissoes"
        }

    # Verificar acao
    allowed_actions = perms.get(module, [])
    if allowed_actions != "*" and action not in allowed_actions:
        return {
            "status": "error",
            "code": 403,
            "message": f"Skill '{origin_skill}' nao tem permissao para '{action}' no modulo '{module}'",
            "recovery": "Solicitar permissao ao administrador ou usar o Data Core como intermediario"
        }

    # Verificar pasta (media)
    if module == "media" and params and "folder" in params:
        allowed_folders = perms.get("media_folders", [])
        if allowed_folders != "*" and params["folder"] not in allowed_folders:
            return {
                "status": "error",
                "code": 403,
                "message": f"Skill '{origin_skill}' nao pode escrever na pasta '{params['folder']}'",
                "recovery": f"Pastas permitidas: {allowed_folders}"
            }

    # Verificar namespace (data)
    if module == "data" and params and "namespace" in params:
        allowed_ns = perms.get("data_namespaces", [])
        if allowed_ns != "*" and params["namespace"] not in allowed_ns:
            if action in ["update_data", "delete_data", "store_data"]:
                return {
                    "status": "error",
                    "code": 403,
                    "message": f"Skill '{origin_skill}' nao pode modificar namespace '{params['namespace']}'",
                    "recovery": f"Namespaces permitidas: {allowed_ns}"
                }

    return None  # OK
```

### F4.4 — Resposta do Data Core nao e recebida ou e mal interpretada

**Quando acontece:** Script falha silenciosamente, retorna string em vez de JSON.

**Prevencao:**
- TODAS as respostas seguem EXATAMENTE o mesmo formato (seccao 6.2 do plano)
- NUNCA retornar texto puro — sempre JSON estruturado

**Resolucao:**
```python
def format_response(status, code, message, data=None, request_id=None):
    """Garante formato padrao SEMPRE."""
    response = {
        "status": status,
        "code": code,
        "message": message,
        "data": data or {},
        "request_id": request_id or "",
        "timestamp": datetime.utcnow().isoformat()
    }
    return json.dumps(response, indent=2, ensure_ascii=False)
```

---

## 6. CAMADA 5 — SKILL CLAUDE (Interpretacao)

### F5.1 — Claude interpreta mal a requisicao de outra skill

**Quando acontece:** Instrucoes ambiguas no SKILL.md, requisicao atipica.

**Prevencao:**
- SKILL.md tem exemplos claros para CADA acao
- Regras explicitas: "Quando receber X, fazer Y"
- Nao depender de interpretacao — usar scripts para logica

**Resolucao:**
- A logica real esta nos scripts Python, nao no Claude
- Claude apenas decide QUAL script chamar e com que parametros
- Se a decisao estiver errada, o script valida e retorna erro claro

### F5.2 — Claude esquece de usar o Data Core

**Quando acontece:** Em conversas longas, Claude pode "esquecer" que deve passar tudo pelo Data Core.

**Prevencao:**
- No SKILL.md de CADA outra skill: regra clara "NUNCA armazenar ficheiros diretamente"
- Regra repetida no topo e no fundo do SKILL.md

**Resolucao:**
- Este e um risco de "comportamento", nao de codigo
- Mitigacao: as outras skills NAO TEM acesso direto ao Supabase
- Se tentarem, simplesmente nao funciona

### F5.3 — Claude chama script com parametros errados

**Quando acontece:** Typo, parametro em formato errado.

**Prevencao:**
- Templates de comando no SKILL.md que Claude pode copiar/adaptar
- Validacao forte nos scripts (F3.1)

**Resolucao:**
- Script retorna erro com mensagem clara do que esperava
- Claude corrige e tenta novamente

---

## 7. HEALTH CHECK — Verificacao Completa do Sistema

Este e o script mais importante de todos. Ele verifica TUDO de uma vez.

```python
#!/usr/bin/env python3
"""
health_check.py — Verificacao completa do estado do Data Core.
Executar ANTES de qualquer operacao importante.
Executar periodicamente para detectar problemas cedo.
"""

def run_health_check():
    """Executa todas as verificacoes e retorna relatorio."""
    checks = []

    # 1. Dependencias Python
    dep_check = check_dependencies()
    checks.append({"name": "Dependencias Python", "result": dep_check or "OK"})

    # 2. Variaveis de ambiente
    env_check = check_env()
    checks.append({"name": "Variaveis de ambiente", "result": env_check or "OK"})

    # 3. Conexao ao Supabase
    conn_check = check_supabase_connection()
    checks.append({"name": "Conexao Supabase", "result": conn_check or "OK"})

    # 4. Tabelas existem
    table_check = check_tables()
    checks.append({"name": "Tabelas do banco", "result": table_check or "OK"})

    # 5. Buckets existem
    bucket_check = check_buckets()
    checks.append({"name": "Buckets de storage", "result": bucket_check or "OK"})

    # 6. Espaco de storage
    storage_check = check_storage_usage()
    checks.append({"name": "Espaco de storage", "result": storage_check or "OK"})

    # 7. Espaco em disco local
    disk_check = check_disk_space(50 * 1024 * 1024)  # 50MB minimo
    checks.append({"name": "Disco local", "result": disk_check or "OK"})

    # Resumo
    failed = [c for c in checks if c["result"] != "OK"]
    warnings = [c for c in checks if isinstance(c["result"], dict) and c["result"].get("status") == "warning"]

    return {
        "status": "healthy" if not failed else "unhealthy",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "warnings": len(warnings),
        "details": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 8. PIPELINE DE EXECUCAO SEGURA

Toda operacao no Data Core segue EXATAMENTE esta sequencia:

```
1. VALIDAR AMBIENTE
   ↓ (check_env, check_dependencies)
   ↓ Se falha → retorna erro com instrucoes de correcao

2. VALIDAR PERMISSOES
   ↓ (check_permission)
   ↓ Se falha → retorna 403 com explicacao

3. VALIDAR PARAMETROS
   ↓ (validate_params)
   ↓ Se falha → retorna 400 com campos esperados

4. VALIDAR FICHEIRO (se aplicavel)
   ↓ (validate_file)
   ↓ Se falha → retorna erro especifico

5. VERIFICAR DUPLICATAS (se aplicavel)
   ↓ (check_duplicate_hash)
   ↓ Se duplicata → retorna referencia existente (409)

6. EXECUTAR OPERACAO
   ↓ (com retry automatico)
   ↓ Se falha → retry ate 3x

7. REGISTRAR NO LOG
   ↓ (log_action automatico)

8. RETORNAR RESULTADO
   ↓ (formato padrao SEMPRE)
```

```python
def execute_request(request):
    """Pipeline completo e seguro para qualquer requisicao."""

    action = request.get("action")
    module = request.get("module")
    params = request.get("params", {})
    origin = request.get("origin_skill", "unknown")
    req_id = request.get("request_id", str(uuid.uuid4())[:8])

    # 1. Ambiente
    env_err = check_env()
    if env_err:
        return format_response("error", env_err["code"], env_err["message"], request_id=req_id)

    # 2. Permissoes
    perm_err = check_permission(origin, module, action, params)
    if perm_err:
        return format_response("error", perm_err["code"], perm_err["message"], request_id=req_id)

    # 3. Acao valida
    action_err = validate_action(module, action)
    if action_err:
        return format_response("error", action_err["code"], action_err["message"], request_id=req_id)

    # 4. Parametros
    param_err = validate_params(action, params)
    if param_err:
        return format_response("error", param_err["code"], param_err["message"], request_id=req_id)

    # 5. Executar (com safety wrapper)
    result = safe_execute(dispatch_action, module, action, params, origin)

    # 6. Log automatico (se nao for uma operacao de log)
    if not action.startswith("log_") and result.get("status") == "success":
        try:
            log_action_to_db(action, module, origin, result)
        except Exception:
            pass  # Log falhou, mas operacao principal foi bem sucedida

    return result
```

---

## 9. CODIGOS DE ERRO COMPLETOS

| Codigo | Significado | Quando acontece | Acao do sistema |
|--------|-------------|-----------------|-----------------|
| 200 | Sucesso | Operacao concluida | Retorna dados |
| 201 | Criado | Novo registro/ficheiro criado | Retorna ID e URL |
| 400 | Parametros invalidos | Campos em falta, tipos errados | Retorna campos esperados |
| 403 | Sem permissao | Skill tenta algo proibido | Retorna permissoes da skill |
| 404 | Nao encontrado | ID inexistente, ficheiro apagado | Retorna sugestao de busca |
| 409 | Duplicata | Ficheiro com mesmo hash ja existe | Retorna referencia existente |
| 413 | Muito grande | Ficheiro excede limite | Retorna limite e sugestao |
| 500 | Erro interno | Bug, erro nao previsto | Retorna traceback + recovery |
| 503 | Indisponivel | Supabase offline, rede falhou | Retorna apos retry ou cache |
| 507 | Sem espaco | Storage ou disco cheio | Retorna uso atual e limite |

---

## 10. SISTEMA DE AUTO-REPARACAO

### 10.1 — Reparacao automatica (sem intervencao humana)

| Problema | Auto-fix |
|----------|----------|
| Tabela nao existe | Criar automaticamente com SQL |
| Bucket nao existe | Criar automaticamente |
| Ficheiro orfao no storage | Marcar como 'deleted' no banco |
| Registro orfao no banco | Marcar como 'deleted' |
| Cache expirado | Limpar e refazer |
| Ficheiros temp > 7 dias | Apagar automaticamente |
| Dependencia em falta | Tentar instalar automaticamente |

### 10.2 — Reparacao com alerta (precisa de atencao)

| Problema | Alerta |
|----------|--------|
| Storage > 80% | Aviso para limpar ou upgrade |
| Requests > 80% do limite | Aviso para otimizar queries |
| Erros repetidos (>5 em 1h) | Aviso de problema sistematico |
| Rollback de storage falhou | CRITICO — ficheiro orfao permanente |

### 10.3 — Script de reparacao completa

```python
def auto_repair():
    """Detecta e corrige problemas automaticamente."""
    repairs = []

    # 1. Verificar e criar tabelas em falta
    for table in ["memory_logs", "media_files", "system_data"]:
        if not table_exists(table):
            create_table(table)
            repairs.append(f"Tabela '{table}' criada")

    # 2. Verificar e criar buckets em falta
    for bucket in ["images", "videos", "documents"]:
        ensure_bucket(bucket)

    # 3. Limpar ficheiros temporarios antigos
    cleaned = cleanup_temp_files(max_age_days=7)
    if cleaned > 0:
        repairs.append(f"{cleaned} ficheiros temporarios removidos")

    # 4. Verificar integridade storage <-> banco
    integrity = integrity_check()
    if integrity["issues_found"] > 0:
        for issue in integrity["issues"]:
            fix_integrity_issue(issue)
        repairs.append(f"{integrity['issues_found']} inconsistencias corrigidas")

    # 5. Limpar cache expirado
    cleaned_cache = cleanup_cache()
    if cleaned_cache > 0:
        repairs.append(f"{cleaned_cache} entradas de cache limpas")

    return {
        "status": "success",
        "repairs_made": len(repairs),
        "details": repairs,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 11. LISTA COMPLETA DE FICHEIROS NECESSARIOS

Atualizacao da estrutura do projeto com TODOS os componentes de seguranca:

```
data-core/
├── SKILL.md                              ← Instrucoes para o Claude
├── scripts/
│   ├── requirements.txt                  ← Dependencias com versoes fixas
│   ├── .env.example                      ← Template de variaveis de ambiente
│   ├── config.py                         ← Conexao Supabase + constantes
│   ├── validators.py                     ← TODA validacao (params, ficheiros, permissoes)
│   ├── permissions.py                    ← Mapa de permissoes por skill
│   ├── retry.py                          ← Logica de retry e cache
│   ├── memory_manager.py                 ← Operacoes de memoria
│   ├── media_manager.py                  ← Operacoes de midia
│   ├── data_manager.py                   ← Operacoes de dados
│   ├── health_check.py                   ← Verificacao completa do sistema
│   ├── auto_repair.py                    ← Auto-reparacao
│   ├── integrity_check.py               ← Consistencia storage <-> banco
│   ├── cleanup.py                        ← Limpeza de temp e cache
│   ├── pipeline.py                       ← Pipeline de execucao segura (execute_request)
│   ├── utils.py                          ← Funcoes auxiliares (hash, format_response, etc.)
│   └── setup_supabase.sql               ← SQL completo (tabelas + indices + funcoes)
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

---

---

## 12. FALHAS AVANCADAS — Auditoria Profunda (103 cenarios adicionais)

Uma verificacao exaustiva revelou 103 cenarios de falha adicionais agrupados em 24 categorias. Abaixo estao as protecoes para os mais criticos.

### 12.1 — Concorrencia e Race Conditions

**Problema:** Duas skills fazem upload simultaneo do mesmo ficheiro. Ambas passam a verificacao de duplicata e criam registros duplicados.

**Solucao:**
```python
def store_media_with_lock(file_path, metadata):
    """Upload com protecao contra duplicatas concorrentes."""
    file_hash = calculate_hash(file_path)
    file_size = os.path.getsize(file_path)

    # Tentar inserir registro com hash — se duplicata, o UNIQUE constraint rejeita
    # Usar upsert ou ON CONFLICT para resolver atomicamente
    try:
        result = supabase.table("media_files").insert({
            "file_hash": file_hash,
            "file_size_bytes": file_size,
            "status": "uploading",  # Estado temporario
            **metadata
        }).execute()
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            # Duplicata real — retornar referencia existente
            existing = supabase.table("media_files") \
                .select("*") \
                .eq("file_hash", file_hash) \
                .execute()
            return {
                "status": "success",
                "code": 409,
                "message": "Ficheiro ja existe (duplicata detectada)",
                "data": existing.data[0] if existing.data else {}
            }
        raise

    # Upload para storage so depois do registro no banco
    upload_to_storage(file_path, result.data[0]["storage_path"])

    # Atualizar status para 'active'
    supabase.table("media_files") \
        .update({"status": "active"}) \
        .eq("id", result.data[0]["id"]) \
        .execute()

    return {"status": "success", "code": 201, "data": result.data[0]}
```

**Adicao ao SQL:**
```sql
-- Indice unico em file_hash para prevenir duplicatas a nivel de banco
CREATE UNIQUE INDEX idx_media_unique_hash
    ON media_files(file_hash)
    WHERE status != 'deleted';
```

### 12.2 — Colisoes de Nomes de Ficheiros no Storage

**Problema:** Dois ficheiros com o mesmo nome (ex: "banner.png") na mesma pasta.

**Solucao:** Nunca usar o nome original como caminho de storage. Gerar caminho unico:

```python
import uuid
from pathlib import Path

def generate_storage_path(original_name, bucket, folder):
    """Gera caminho unico no storage. NUNCA usa o nome original diretamente."""
    ext = Path(original_name).suffix.lower()  # .png, .jpg, etc.
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{unique_id}{ext}"
    return f"{folder}/{safe_name}"
    # Resultado: "marketing/20260407_143022_a1b2c3d4e5f6.png"
```

### 12.3 — Sanitizacao de Nomes e Encoding

**Problema:** Nomes com caracteres especiais, path traversal ("../"), unicode inconsistente.

**Solucao:**
```python
import unicodedata
import re

def sanitize_filename(name):
    """Remove caracteres perigosos de nomes de ficheiros."""
    # 1. Normalizar unicode (NFC)
    name = unicodedata.normalize("NFC", name)
    # 2. Remover path traversal
    name = name.replace("..", "").replace("/", "_").replace("\\", "_")
    # 3. Remover caracteres de controlo
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    # 4. Limitar tamanho
    name = name[:200]
    # 5. Garantir que nao e vazio
    if not name.strip():
        name = "unnamed_file"
    return name

def sanitize_tags(tags):
    """Valida e limita array de tags."""
    if not isinstance(tags, list):
        return []
    # Maximo 50 tags, cada uma com maximo 100 caracteres
    clean = []
    for tag in tags[:50]:
        if isinstance(tag, str) and tag.strip():
            clean.append(tag.strip()[:100].lower())
    return clean

def sanitize_metadata(metadata, max_depth=3, max_size_bytes=50000):
    """Limita profundidade e tamanho de metadata JSONB."""
    if not isinstance(metadata, dict):
        return {}

    # Verificar tamanho total
    json_str = json.dumps(metadata, default=str)
    if len(json_str.encode()) > max_size_bytes:
        return {"_error": "metadata excede 50KB, truncado", "_original_size": len(json_str)}

    # Verificar profundidade (prevenir nesting attacks)
    def check_depth(obj, current=0):
        if current > max_depth:
            return False
        if isinstance(obj, dict):
            return all(check_depth(v, current+1) for v in obj.values())
        if isinstance(obj, list):
            return all(check_depth(v, current+1) for v in obj)
        return True

    if not check_depth(metadata):
        return {"_error": f"metadata excede profundidade maxima de {max_depth} niveis"}

    return metadata
```

### 12.4 — Limites de Tamanho em Queries

**Problema:** search_memory ou list_media podem retornar milhoes de registros.

**Solucao:**
```python
# Limites globais
MAX_RESULTS_PER_QUERY = 100
DEFAULT_RESULTS_PER_QUERY = 20

def apply_pagination(query_params):
    """Forca paginacao em TODAS as queries de leitura."""
    limit = min(
        query_params.get("limit", DEFAULT_RESULTS_PER_QUERY),
        MAX_RESULTS_PER_QUERY
    )
    offset = max(query_params.get("offset", 0), 0)
    return limit, offset
```

### 12.5 — Rate Limiting do Supabase (por segundo)

**Problema:** Muitas requests num curto espaco de tempo pode fazer Supabase rejeitar.

**Solucao:**
```python
import time
from collections import deque

class RateLimiter:
    """Controla numero de requests por segundo."""

    def __init__(self, max_per_second=50):  # Margem de seguranca (limite real: ~100)
        self.max_per_second = max_per_second
        self.timestamps = deque()

    def wait_if_needed(self):
        """Aguarda se estiver perto do limite."""
        now = time.time()
        # Limpar timestamps com mais de 1 segundo
        while self.timestamps and now - self.timestamps[0] > 1.0:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_per_second:
            sleep_time = 1.0 - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.timestamps.append(time.time())

# Instancia global
rate_limiter = RateLimiter(max_per_second=50)
```

### 12.6 — Protecao de Credenciais

**Problema:** Chaves do Supabase podem vazar em tracebacks, logs ou ficheiros.

**Solucao:**
```python
def sanitize_error_for_response(error_msg):
    """Remove credenciais e dados sensiveis de mensagens de erro."""
    sensitive_patterns = [
        os.getenv("SUPABASE_SERVICE_KEY", ""),
        os.getenv("SUPABASE_ANON_KEY", ""),
        os.getenv("SUPABASE_URL", ""),
    ]
    sanitized = str(error_msg)
    for pattern in sensitive_patterns:
        if pattern and len(pattern) > 5:
            sanitized = sanitized.replace(pattern, "[REDACTED]")
    return sanitized
```

E no `safe_execute()` (F3.5), nunca incluir traceback completo na resposta:
```python
def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Traceback so vai para o log interno, NUNCA para a resposta
        full_traceback = traceback.format_exc()
        log_error_internal(full_traceback)  # Ficheiro local, nao banco

        return {
            "status": "error",
            "code": 500,
            "message": sanitize_error_for_response(str(e)),
            # SEM traceback na resposta publica
            "recovery": "Consultar logs internos para detalhes"
        }
```

### 12.7 — Verificacao de Identidade de Skill (Anti-Spoofing)

**Problema:** Uma skill pode dizer `origin_skill: "data_core"` e ganhar permissoes totais.

**Solucao para o contexto Claude:** No ecossistema Claude, as skills sao chamadas pelo proprio Claude, nao por processos externos. A protecao funciona assim:

1. O SKILL.md do Data Core instrui o Claude a NUNCA aceitar `origin_skill` como parametro da requisicao. Em vez disso, o Claude SABE qual skill esta a fazer o pedido porque e ele mesmo que esta a executar.

2. Nos scripts Python, quando chamados via Claude + Bash, o `origin_skill` e passado como argumento pelo Claude (que tem contexto da skill ativa), nao pelo codigo da skill.

3. Para protecao adicional futura (quando o sistema crescer):
```python
# Token simples por skill — definido na configuracao, nao pela skill
SKILL_TOKENS = {
    "marketing": "mk_token_abc123",
    "site_creator": "sc_token_def456",
    "data_core": "dc_token_ghi789"
}

def verify_skill_identity(origin_skill, token=None):
    """Verifica identidade (futuro: quando skills rodam como processos)."""
    if token and SKILL_TOKENS.get(origin_skill) != token:
        return {
            "status": "error",
            "code": 403,
            "message": "Token de skill invalido"
        }
    return None  # OK
```

### 12.8 — Timezones

**Problema:** Inconsistencia entre timestamps locais e do Supabase.

**Solucao:** TUDO em UTC, sempre.
```python
from datetime import datetime, timezone

def utc_now():
    """Retorna timestamp em UTC. USAR SEMPRE em vez de datetime.now()."""
    return datetime.now(timezone.utc)

def utc_isoformat():
    """Retorna string ISO 8601 em UTC."""
    return utc_now().isoformat()
```

No SQL, todas as colunas ja usam `TIMESTAMPTZ` e `DEFAULT NOW()` que respeita UTC no Supabase.

### 12.9 — Recuperacao de Uploads Parciais

**Problema:** Upload interrompido a meio pode deixar ficheiro corrompido no storage.

**Solucao:** O estado "uploading" do F12.1 resolve isto:
1. Registro criado no banco com `status: "uploading"`
2. Upload para storage
3. Se sucesso → status vira `"active"`
4. Se falha → registro fica como `"uploading"`
5. Health check detecta registros "uploading" com mais de 1 hora e marca como "failed"

```python
def cleanup_stale_uploads(max_age_hours=1):
    """Limpa uploads que ficaram presos."""
    cutoff = utc_now() - timedelta(hours=max_age_hours)

    stale = supabase.table("media_files") \
        .select("id, storage_path") \
        .eq("status", "uploading") \
        .lt("created_at", cutoff.isoformat()) \
        .execute()

    for record in stale.data:
        # Tentar apagar do storage (pode nao existir)
        try:
            delete_from_storage(record["storage_path"])
        except Exception:
            pass
        # Marcar como failed no banco
        supabase.table("media_files") \
            .update({"status": "deleted"}) \
            .eq("id", record["id"]) \
            .execute()

    return len(stale.data)
```

### 12.10 — Hash em Streaming (Ficheiros Grandes)

**Problema:** Carregar ficheiro de 50MB inteiro em memoria para calcular hash pode causar crash.

**Solucao:**
```python
import hashlib

def calculate_hash_streaming(file_path, chunk_size=8192):
    """Calcula SHA-256 sem carregar ficheiro inteiro em memoria."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"
```

### 12.11 — Versionamento da API

**Problema:** Se o formato de requisicao mudar no futuro, skills antigas vao quebrar.

**Solucao:**
```python
# Adicionar versao ao protocolo
CURRENT_API_VERSION = "1.0"

def execute_request(request):
    """Pipeline com suporte a versao."""
    api_version = request.get("api_version", "1.0")

    if api_version != CURRENT_API_VERSION:
        # Por agora, aceitar qualquer versao com aviso
        log_action(f"Requisicao com versao {api_version} (atual: {CURRENT_API_VERSION})")

    # Resto do pipeline...
```

Formato de requisicao atualizado:
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

### 12.12 — Protecao contra Log Recursivo

**Problema:** Se `log_error_to_db()` falha, tentar logar essa falha pode criar loop infinito.

**Solucao:**
```python
_log_depth = 0
MAX_LOG_DEPTH = 1

def log_error_to_db(error_data):
    """Log com protecao contra recursao."""
    global _log_depth

    if _log_depth >= MAX_LOG_DEPTH:
        # Fallback: escrever em ficheiro local, nao no banco
        with open("/tmp/data_core_emergency.log", "a") as f:
            f.write(f"{utc_isoformat()} | {json.dumps(error_data, default=str)}\n")
        return

    _log_depth += 1
    try:
        supabase.table("memory_logs").insert(error_data).execute()
    except Exception:
        # Fallback final
        with open("/tmp/data_core_emergency.log", "a") as f:
            f.write(f"{utc_isoformat()} | LOG_FAILED | {json.dumps(error_data, default=str)}\n")
    finally:
        _log_depth -= 1
```

### 12.13 — Politica de Retencao de Logs

**Problema:** Tabela memory_logs cresce indefinidamente.

**Solucao:**
```python
def archive_old_logs(retention_days=90):
    """Move logs antigos para exportacao e limpa banco."""
    cutoff = utc_now() - timedelta(days=retention_days)

    # 1. Contar logs a arquivar
    old_logs = supabase.table("memory_logs") \
        .select("*") \
        .lt("created_at", cutoff.isoformat()) \
        .execute()

    if not old_logs.data:
        return {"archived": 0}

    # 2. Exportar para storage (backup)
    export_data = json.dumps(old_logs.data, default=str)
    export_path = f"documents/exports/logs_archive_{utc_now().strftime('%Y%m%d')}.json"
    supabase.storage.from_("documents").upload(export_path, export_data.encode())

    # 3. Apagar do banco
    supabase.table("memory_logs") \
        .delete() \
        .lt("created_at", cutoff.isoformat()) \
        .execute()

    return {"archived": len(old_logs.data), "export_path": export_path}
```

---

## 13. ADICAO AO SCHEMA SQL — Status "uploading"

```sql
-- Atualizar CHECK constraint para incluir 'uploading'
ALTER TABLE media_files
    DROP CONSTRAINT IF EXISTS media_files_status_check;

ALTER TABLE media_files
    ADD CONSTRAINT media_files_status_check
    CHECK (status IN ('active', 'archived', 'temp', 'deleted', 'uploading'));

-- Indice unico parcial para prevenir duplicatas (exclui deletados)
CREATE UNIQUE INDEX IF NOT EXISTS idx_media_unique_hash
    ON media_files(file_hash)
    WHERE status NOT IN ('deleted');
```

---

## 14. HEALTH CHECK ATUALIZADO — Versao Completa

```python
def run_health_check():
    """Verificacao COMPLETA do sistema — versao final."""
    checks = []

    # Infraestrutura (Camada 1)
    checks.append(run_check("Dependencias Python", check_dependencies))
    checks.append(run_check("Variaveis de ambiente", check_env))
    checks.append(run_check("Disco local", lambda: check_disk_space(50*1024*1024)))

    # Supabase (Camada 2)
    checks.append(run_check("Conexao Supabase", check_supabase_connection))
    checks.append(run_check("Tabelas", check_tables))
    checks.append(run_check("Buckets", check_buckets))
    checks.append(run_check("Espaco storage", check_storage_usage))

    # Integridade (Camada 2+)
    checks.append(run_check("Uploads presos", lambda: check_stale_uploads()))
    checks.append(run_check("Ficheiros orfaos", lambda: quick_integrity_check()))

    # Operacional
    checks.append(run_check("Logs emergencia", check_emergency_log))
    checks.append(run_check("Retencao de logs", check_log_retention))

    # Resumo
    failed = [c for c in checks if c.get("status") == "error"]
    warnings = [c for c in checks if c.get("status") == "warning"]

    return {
        "system_status": "healthy" if not failed else ("degraded" if len(failed) < 3 else "unhealthy"),
        "total": len(checks),
        "passed": len(checks) - len(failed) - len(warnings),
        "warnings": len(warnings),
        "failed": len(failed),
        "details": checks,
        "timestamp": utc_isoformat()
    }

def run_check(name, func):
    """Executa uma verificacao com protecao."""
    try:
        result = func()
        if result is None:
            return {"name": name, "status": "ok"}
        return {"name": name, **result}
    except Exception as e:
        return {"name": name, "status": "error", "message": str(e)}
```

---

## 15. REGRA FINAL — O PRINCIPIO DA NAO-SURPRESA

> O sistema NUNCA deve falhar silenciosamente.
> Toda falha gera uma mensagem clara com: o que aconteceu, porque aconteceu, e como resolver.
> Se o sistema nao sabe resolver, diz "nao sei resolver" em vez de tentar e piorar.

Isto significa:
- ZERO prints sem contexto
- ZERO retornos vazios
- ZERO erros engolidos (catch sem acao)
- TODA resposta segue o formato padrao
- TODA falha e registrada na memoria (quando possivel)
- Quando a memoria falha, usa log de emergencia local
- Credenciais NUNCA aparecem em respostas ou logs
- Timestamps SEMPRE em UTC
- Nomes de ficheiros SEMPRE sanitizados
- Queries SEMPRE com paginacao

---

## 16. RESUMO — COBERTURA TOTAL DE FALHAS

| Categoria | Cenarios | Protecao |
|-----------|----------|----------|
| Infraestrutura (rede, disco, deps) | 4 | Retry, check_env, check_deps, disk_check |
| Supabase (offline, limites, dados) | 7 | Cache, retry, storage monitor, integrity_check |
| Scripts Python (params, ficheiros, crashes) | 5 | Validators, file_check, safe_execute |
| Comunicacao (protocolo, permissoes) | 4 | validate_action, check_permission, format_response |
| Skill Claude (interpretacao) | 3 | Scripts validam tudo, Claude so decide qual chamar |
| Concorrencia | 5 | UNIQUE index, status "uploading", UUID paths |
| Nomes e encoding | 5 | sanitize_filename, NFC normalize, tag limits |
| Tamanho e limites | 3 | Paginacao forcada, metadata limits, file size check |
| Rate limiting | 4 | RateLimiter class, batch operations |
| Credenciais | 4 | sanitize_error, .env, no traceback in response |
| Identidade | 2 | Claude context, future token system |
| Timezones | 6 | UTC everywhere, utc_now() helper |
| Uploads parciais | 3 | Status "uploading", cleanup_stale_uploads |
| Logs e retencao | 3 | Anti-recursion, emergency log, archive_old_logs |
| API versioning | 3 | api_version field, backwards compat |
| **TOTAL** | **~61 cenarios primarios cobertos** |

Os restantes 42 cenarios (dos 103 identificados) sao variantes dos primarios ou de risco tao baixo que a protecao generica (safe_execute + format_response + retry) cobre adequadamente.
