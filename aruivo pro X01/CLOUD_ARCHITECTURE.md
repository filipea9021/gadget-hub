# CIS — Cloud Architecture Blueprint v1.0
## Preparação para Automação 100% do Pipeline de Vídeo

---

## 1. O PROBLEMA ATUAL

O pipeline atual tem um gargalo crítico no Estágio 4→5 (Imagem → Vídeo):

```
Geração de Imagem (Upsampler) → Download Local → Upload Manual → Geração de Vídeo (Kling/Hailuo)
                                      ↑                ↑
                                  BLOQUEIO         BLOQUEIO
                              (segurança do       (extensão Chrome
                               browser)            sem acesso a
                                                   ficheiros locais)
```

**Causa raiz:** Os assets (imagens, vídeos) passam pelo computador local como intermediário. O Claude não tem acesso direto ao filesystem do Windows, e as extensões de browser bloqueiam uploads por segurança.

---

## 2. A SOLUÇÃO: CLOUD STORAGE COMO HUB CENTRAL

```
┌──────────────────────────────────────────────────────────┐
│                    CLOUD STORAGE HUB                      │
│              (Google Drive / S3 / R2 / Supabase)          │
│                                                          │
│   /cis-assets/                                           │
│   ├── /projects/{project_id}/                            │
│   │   ├── /images/          ← imagens geradas            │
│   │   ├── /videos/          ← vídeos animados            │
│   │   ├── /audio/           ← voiceover, música, SFX     │
│   │   ├── /exports/         ← vídeos finais              │
│   │   └── manifest.json     ← metadados do projeto       │
│   └── /templates/           ← configs reutilizáveis      │
└──────────────┬───────────────────────┬───────────────────┘
               │                       │
     ┌─────────▼──────────┐   ┌───────▼──────────┐
     │   GERAÇÃO (APIs)    │   │   CLAUDE (Cowork) │
     │                     │   │                    │
     │ • Upsampler API     │   │ • Lê assets        │
     │ • Kling AI API      │   │ • Escreve assets   │
     │ • Hailuo API        │   │ • Orquestra tudo   │
     │ • Higgsfield API    │   │ • Sem bloqueios    │
     └────────────────────┘   └────────────────────┘
```

**Fluxo novo (100% automático):**
```
Claude gera prompt → API gera imagem → URL salva no cloud →
Claude pega URL do cloud → API anima em vídeo → URL salva no cloud →
Claude monta timeline → Exporta vídeo final → Cloud → Usuário acessa
```

**Zero downloads locais. Zero uploads manuais. Zero bloqueios de browser.**

---

## 3. OPÇÕES DE CLOUD STORAGE

### 3.1 Google Drive (via MCP conectado)
- **Vantagem:** Já integrado no Cowork (mcp__google_drive), o utilizador já tem conta Google
- **Acesso:** Claude lê/escreve diretamente via MCP
- **Limite:** 15GB grátis, APIs de upload/download disponíveis
- **Ideal para:** MVP, uso pessoal

### 3.2 Supabase Storage
- **Vantagem:** URLs públicas diretas, fácil integração via API REST
- **Acesso:** Qualquer API pode ler/escrever com service key
- **Limite:** 1GB grátis, storage barato depois
- **Ideal para:** Quando o sistema tiver APIs próprias (Fase 2+)

### 3.3 Cloudflare R2
- **Vantagem:** Zero egress cost, S3-compatible, Workers para automação
- **Acesso:** S3 API + Workers
- **Limite:** 10GB grátis, sem custo de saída
- **Ideal para:** Escala, SaaS futuro

### 3.4 Backblaze B2
- **Vantagem:** Mais barato de todos, S3-compatible
- **Ideal para:** Armazenamento massivo de vídeos

### Recomendação por fase:
| Fase | Storage | Razão |
|------|---------|-------|
| MVP (agora) | **Google Drive** | Já conectado, zero setup |
| Fase 2 | **Supabase Storage** | APIs próprias, URLs diretas |
| Fase 3+ (SaaS) | **Cloudflare R2** | Escala, zero egress |

---

## 4. INTERFACES ABSTRATAS (cloud_storage.py)

O módulo de cloud storage será abstraído para suportar qualquer provider:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class AssetType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    EXPORT = "export"

class StorageProvider(Enum):
    GOOGLE_DRIVE = "google_drive"
    SUPABASE = "supabase"
    CLOUDFLARE_R2 = "cloudflare_r2"
    BACKBLAZE_B2 = "backblaze_b2"
    LOCAL = "local"  # fallback

@dataclass
class CloudAsset:
    """Representa um asset armazenado na cloud."""
    id: str
    project_id: str
    asset_type: AssetType
    filename: str
    cloud_url: str          # URL direta para acesso
    public_url: str = ""    # URL pública (se aplicável)
    size_bytes: int = 0
    mime_type: str = ""
    metadata: dict = None   # prompt usado, cena, etc.

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class CloudStorageBase(ABC):
    """Interface abstrata — qualquer provider implementa isto."""

    @abstractmethod
    async def upload(self, file_data: bytes, path: str,
                     mime_type: str = "") -> CloudAsset:
        """Upload de bytes para o cloud."""
        pass

    @abstractmethod
    async def upload_from_url(self, source_url: str, path: str) -> CloudAsset:
        """Download de uma URL e upload direto para o cloud (URL-to-cloud)."""
        pass

    @abstractmethod
    async def download(self, cloud_path: str) -> bytes:
        """Download de bytes do cloud."""
        pass

    @abstractmethod
    async def get_url(self, cloud_path: str) -> str:
        """Obter URL direta de acesso ao asset."""
        pass

    @abstractmethod
    async def list_assets(self, project_id: str,
                          asset_type: Optional[AssetType] = None) -> list:
        """Listar assets de um projeto."""
        pass

    @abstractmethod
    async def delete(self, cloud_path: str) -> bool:
        """Remover asset."""
        pass
```

---

## 5. PIPELINE ATUALIZADO (COM CLOUD)

### Estágio 4 (Geração de Imagem) — NOVO FLUXO:

```
1. Claude gera prompt de imagem
2. Claude chama API de geração (Upsampler/Higgsfield/Leonardo)
   → API retorna URL da imagem gerada
3. cloud_storage.upload_from_url(image_url, "/projects/{id}/images/cena_1.png")
   → Imagem guardada no cloud com metadados (prompt, cena, timestamp)
4. Asset registado no manifest.json do projeto
```

### Estágio 5 (Animação) — NOVO FLUXO:

```
1. Claude lê manifest.json → obtém URLs das imagens no cloud
2. Para cada imagem:
   a. Obtém cloud_url da imagem
   b. Chama API de animação (Kling API / Hailuo API / Higgsfield)
      → Passa a URL da imagem diretamente (muitas APIs aceitam URLs)
      → Ou faz download do cloud e upload via API
   c. API retorna URL do vídeo gerado
   d. cloud_storage.upload_from_url(video_url, "/projects/{id}/videos/cena_1.mp4")
3. Todos os clips registados no manifest.json
```

### Estágio 6+ (Pós-produção) — NOVO FLUXO:

```
1. Claude lê todos os assets do cloud (imagens + vídeos + áudio)
2. Gera timeline/script de edição
3. Se existir API de edição (CapCut API, Remotion):
   → Passa URLs dos assets diretamente
   → Recebe vídeo final montado
4. Vídeo final guardado em /projects/{id}/exports/
5. Utilizador acede via link do cloud
```

---

## 6. INTEGRAÇÃO COM O SISTEMA CIS

### 6.1 Novo módulo: AssetManager

```python
class AssetManager:
    """Gerencia todo o ciclo de vida dos assets de um projeto."""

    def __init__(self, storage: CloudStorageBase, project_id: str):
        self.storage = storage
        self.project_id = project_id
        self.manifest = {}

    async def store_generated_image(self, source_url: str, scene: str,
                                     prompt: str) -> CloudAsset:
        """Guarda imagem gerada e regista no manifest."""
        pass

    async def store_animated_video(self, source_url: str, scene: str,
                                    animation_prompt: str) -> CloudAsset:
        """Guarda vídeo animado e regista no manifest."""
        pass

    async def get_scene_assets(self, scene: str) -> dict:
        """Retorna todos os assets de uma cena (imagem + vídeo + áudio)."""
        pass

    async def get_project_manifest(self) -> dict:
        """Retorna manifest completo do projeto."""
        pass

    async def export_for_editing(self) -> dict:
        """Exporta URLs organizadas para editor de vídeo."""
        pass
```

### 6.2 Atualização do CISConfig

```python
@dataclass
class CloudConfig:
    provider: str = "google_drive"  # google_drive, supabase, r2, b2
    bucket_name: str = ""
    api_key: str = ""
    api_secret: str = ""
    base_path: str = "/cis-assets"
    public_access: bool = False
```

### 6.3 Atualização do Orchestrator

O orchestrator ganha um novo modo de pipeline:

```python
class PipelineMode(Enum):
    RESEARCH = "research"
    CREATE = "create"
    OPTIMIZE = "optimize"
    FULL = "full"
    PRODUCE = "produce"
    VIDEO_FULL = "video_full"  # NOVO: pipeline completo de vídeo
```

O modo `VIDEO_FULL` executa:
```
tema → prompts → geração de imagens (cloud) → animação (cloud) →
roteiro → timeline → montagem → export (cloud)
```

---

## 7. INTEGRAÇÃO MULTI-PROJETO

O sistema é preparado para ser um módulo reutilizável:

```
┌─────────────────────┐     ┌─────────────────────┐
│   PROJETO A (CIS)    │     │   PROJETO B (novo)   │
│                      │     │                      │
│  Bot Telegram        │     │  Interface Web?      │
│  Orchestrator        │     │  Dashboard?          │
│  Agentes IA          │     │  API REST?           │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────┐
│           MÓDULO COMPARTILHADO                    │
│                                                  │
│   cloud_storage.py    ← armazenamento            │
│   asset_manager.py    ← gestão de assets         │
│   video_pipeline.py   ← pipeline de vídeo        │
│   api_integrations.py ← APIs de IA               │
│                                                  │
│   Skill: viral-video-creator                     │
└──────────────────────────────────────────────────┘
```

### Estrutura de diretórios preparada:

```
aruivo pro X01/
├── core/                    ← módulos compartilhados (NOVO)
│   ├── cloud_storage.py     ← interface abstrata + providers
│   ├── asset_manager.py     ← gestão de assets por projeto
│   ├── video_pipeline.py    ← pipeline automatizado de vídeo
│   └── api_integrations.py  ← wrappers para APIs externas
├── .claude/skills/
│   └── viral-video-creator/
│       └── SKILL.md         ← atualizada com hooks para cloud
├── config.py                ← atualizada com CloudConfig
├── orchestrator.py          ← atualizada com VIDEO_FULL mode
└── ... (restante do CIS)
```

---

## 8. VARIÁVEIS DE AMBIENTE (NOVAS)

```env
# Cloud Storage
CLOUD_PROVIDER=google_drive          # google_drive | supabase | r2 | b2
CLOUD_BUCKET=cis-assets
CLOUD_API_KEY=
CLOUD_API_SECRET=

# Supabase (se usar)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# Cloudflare R2 (se usar)
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=

# APIs de Geração de Vídeo (acesso direto via API, sem browser)
KLING_API_KEY=
KLING_API_SECRET=
HAILUO_API_KEY=
UPSAMPLER_API_KEY=
```

---

## 9. CHECKLIST DE PREPARAÇÃO

- [x] CLOUD_ARCHITECTURE.md — este documento
- [ ] cloud_storage.py — interfaces abstratas + provider Google Drive
- [ ] asset_manager.py — gestão de assets por projeto
- [ ] config.py — atualizado com CloudConfig
- [ ] SKILL.md — atualizada com Estágio 4/5 cloud-ready
- [ ] BLUEPRINT.md — atualizado com seção de Cloud Architecture
- [ ] .env — novos slots de variáveis
- [ ] Manifest schema definido (manifest.json)

---

## 10. PRÓXIMOS PASSOS (quando o cloud storage estiver configurado)

1. **Escolher provider** — Google Drive para MVP (já conectado via MCP)
2. **Implementar GoogleDriveStorage** — extends CloudStorageBase
3. **Configurar APIs diretas** — Kling API, Hailuo API, Upsampler API
4. **Testar pipeline end-to-end** — prompt → imagem → cloud → vídeo → cloud
5. **Integrar com Projeto B** — módulo compartilhado
