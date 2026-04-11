"""
CIS Core — Cloud Storage Module
Interface abstrata + providers para armazenamento de assets na cloud.

Preparado para suportar múltiplos providers:
- Google Drive (MVP — via MCP ou API)
- Supabase Storage (Fase 2)
- Cloudflare R2 (Fase 3 / SaaS)
- Backblaze B2 (alternativa barata)
- Local (fallback para desenvolvimento)

Uso:
    storage = get_storage_provider("google_drive", config)
    asset = await storage.upload_from_url(image_url, "projects/abc/images/cena1.png")
    url = await storage.get_url(asset.cloud_path)
"""

import os
import uuid
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# === ENUMS ===

class AssetType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    EXPORT = "export"
    THUMBNAIL = "thumbnail"


class StorageProvider(Enum):
    GOOGLE_DRIVE = "google_drive"
    SUPABASE = "supabase"
    CLOUDFLARE_R2 = "cloudflare_r2"
    BACKBLAZE_B2 = "backblaze_b2"
    LOCAL = "local"


# === DATA CLASSES ===

@dataclass
class CloudAsset:
    """Representa um asset armazenado na cloud."""
    id: str
    project_id: str
    asset_type: AssetType
    filename: str
    cloud_path: str        # caminho completo no storage
    cloud_url: str         # URL direta para acesso (autenticada)
    public_url: str = ""   # URL pública (se disponível)
    size_bytes: int = 0
    mime_type: str = ""
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    # metadata típico: {"prompt": "...", "scene": "cena_1", "model": "nano_banana_2"}

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "asset_type": self.asset_type.value,
            "filename": self.filename,
            "cloud_path": self.cloud_path,
            "cloud_url": self.cloud_url,
            "public_url": self.public_url,
            "size_bytes": self.size_bytes,
            "mime_type": self.mime_type,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CloudAsset":
        data["asset_type"] = AssetType(data["asset_type"])
        return cls(**data)


@dataclass
class ProjectManifest:
    """Manifest de um projeto — regista todos os assets e metadata."""
    project_id: str
    name: str = ""
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    assets: List[CloudAsset] = field(default_factory=list)
    pipeline_state: Dict[str, Any] = field(default_factory=dict)
    # pipeline_state: {"stage": 5, "completed_scenes": ["cena_1", "cena_2"]}

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def add_asset(self, asset: CloudAsset):
        self.assets.append(asset)
        self.updated_at = datetime.utcnow().isoformat()

    def get_assets_by_type(self, asset_type: AssetType) -> List[CloudAsset]:
        return [a for a in self.assets if a.asset_type == asset_type]

    def get_assets_by_scene(self, scene: str) -> List[CloudAsset]:
        return [a for a in self.assets if a.metadata.get("scene") == scene]

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assets": [a.to_dict() for a in self.assets],
            "pipeline_state": self.pipeline_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectManifest":
        assets_data = data.pop("assets", [])
        manifest = cls(**data)
        manifest.assets = [CloudAsset.from_dict(a) for a in assets_data]
        return manifest

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# === INTERFACE ABSTRATA ===

class CloudStorageBase(ABC):
    """
    Interface abstrata para cloud storage.
    Qualquer provider (Google Drive, Supabase, R2, etc.) implementa isto.
    """

    def __init__(self, config: dict):
        self.config = config
        self.base_path = config.get("base_path", "/cis-assets")

    @abstractmethod
    async def upload(self, file_data: bytes, path: str,
                     mime_type: str = "", metadata: dict = None) -> CloudAsset:
        """
        Upload de bytes para o cloud.

        Args:
            file_data: conteúdo do ficheiro em bytes
            path: caminho relativo no storage (ex: "projects/abc/images/cena1.png")
            mime_type: tipo MIME (ex: "image/png")
            metadata: metadados adicionais

        Returns:
            CloudAsset com URLs de acesso
        """
        pass

    @abstractmethod
    async def upload_from_url(self, source_url: str, path: str,
                               metadata: dict = None) -> CloudAsset:
        """
        Download de uma URL externa e upload direto para o cloud.
        Este é o método chave para automação — elimina o intermediário local.

        Fluxo: URL externa → download em memória → upload para cloud

        Args:
            source_url: URL da imagem/vídeo de origem (ex: URL do Upsampler CDN)
            path: caminho destino no storage
            metadata: metadados adicionais

        Returns:
            CloudAsset com URLs de acesso
        """
        pass

    @abstractmethod
    async def download(self, cloud_path: str) -> bytes:
        """Download de bytes do cloud."""
        pass

    @abstractmethod
    async def get_url(self, cloud_path: str, expiry_seconds: int = 3600) -> str:
        """
        Obter URL de acesso ao asset.

        Args:
            cloud_path: caminho no storage
            expiry_seconds: tempo de validade do URL (se signed)

        Returns:
            URL de acesso (pode ser signed/temporário ou permanente)
        """
        pass

    @abstractmethod
    async def list_assets(self, prefix: str) -> List[dict]:
        """Listar ficheiros num diretório do storage."""
        pass

    @abstractmethod
    async def delete(self, cloud_path: str) -> bool:
        """Remover asset do storage."""
        pass

    @abstractmethod
    async def exists(self, cloud_path: str) -> bool:
        """Verificar se asset existe."""
        pass

    # --- Métodos de conveniência (não-abstratos) ---

    def _full_path(self, relative_path: str) -> str:
        """Constrói caminho completo com base_path."""
        return f"{self.base_path}/{relative_path}".replace("//", "/")

    def _guess_mime_type(self, filename: str) -> str:
        """Adivinha MIME type pelo nome do ficheiro."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mime_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif",
            "mp4": "video/mp4",
            "webm": "video/webm",
            "mov": "video/quicktime",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "json": "application/json",
            "md": "text/markdown",
        }
        return mime_map.get(ext, "application/octet-stream")


# === PROVIDER: LOCAL (fallback para dev) ===

class LocalStorage(CloudStorageBase):
    """
    Storage local — fallback para desenvolvimento e testes.
    Guarda ficheiros no disco local.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.root_dir = config.get("root_dir", "./cis-assets")
        os.makedirs(self.root_dir, exist_ok=True)

    async def upload(self, file_data: bytes, path: str,
                     mime_type: str = "", metadata: dict = None) -> CloudAsset:
        full_path = os.path.join(self.root_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_data)

        filename = os.path.basename(path)
        return CloudAsset(
            id="",
            project_id=path.split("/")[1] if "/" in path else "",
            asset_type=self._infer_asset_type(filename),
            filename=filename,
            cloud_path=path,
            cloud_url=f"file://{os.path.abspath(full_path)}",
            size_bytes=len(file_data),
            mime_type=mime_type or self._guess_mime_type(filename),
            metadata=metadata or {},
        )

    async def upload_from_url(self, source_url: str, path: str,
                               metadata: dict = None) -> CloudAsset:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(source_url, follow_redirects=True)
            response.raise_for_status()
            return await self.upload(
                response.content, path,
                mime_type=response.headers.get("content-type", ""),
                metadata=metadata,
            )

    async def download(self, cloud_path: str) -> bytes:
        full_path = os.path.join(self.root_dir, cloud_path)
        with open(full_path, "rb") as f:
            return f.read()

    async def get_url(self, cloud_path: str, expiry_seconds: int = 3600) -> str:
        full_path = os.path.join(self.root_dir, cloud_path)
        return f"file://{os.path.abspath(full_path)}"

    async def list_assets(self, prefix: str) -> List[dict]:
        dir_path = os.path.join(self.root_dir, prefix)
        if not os.path.exists(dir_path):
            return []
        results = []
        for f in os.listdir(dir_path):
            full = os.path.join(dir_path, f)
            if os.path.isfile(full):
                results.append({
                    "path": f"{prefix}/{f}",
                    "size": os.path.getsize(full),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(full)
                    ).isoformat(),
                })
        return results

    async def delete(self, cloud_path: str) -> bool:
        full_path = os.path.join(self.root_dir, cloud_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    async def exists(self, cloud_path: str) -> bool:
        return os.path.exists(os.path.join(self.root_dir, cloud_path))

    def _infer_asset_type(self, filename: str) -> AssetType:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in ("png", "jpg", "jpeg", "webp", "gif"):
            return AssetType.IMAGE
        elif ext in ("mp4", "webm", "mov", "avi"):
            return AssetType.VIDEO
        elif ext in ("mp3", "wav", "ogg", "flac"):
            return AssetType.AUDIO
        return AssetType.DOCUMENT


# === PROVIDER: GOOGLE DRIVE (placeholder — implementar quando configurado) ===

class GoogleDriveStorage(CloudStorageBase):
    """
    Google Drive storage via API.
    PLACEHOLDER — será implementado quando as credenciais estiverem configuradas.

    Pode usar:
    - Google Drive API v3 diretamente
    - MCP Google Drive connector (quando disponível no Cowork)
    - PyDrive2 library
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.folder_id = config.get("folder_id", "")
        # TODO: inicializar cliente Google Drive

    async def upload(self, file_data, path, mime_type="", metadata=None):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def upload_from_url(self, source_url, path, metadata=None):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def download(self, cloud_path):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def get_url(self, cloud_path, expiry_seconds=3600):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def list_assets(self, prefix):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def delete(self, cloud_path):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")

    async def exists(self, cloud_path):
        raise NotImplementedError("GoogleDriveStorage: aguardando configuração de credenciais")


# === PROVIDER: SUPABASE (placeholder) ===

class SupabaseStorage(CloudStorageBase):
    """
    Supabase Storage via API REST.
    PLACEHOLDER — será implementado na Fase 2.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.supabase_url = config.get("supabase_url", "")
        self.service_key = config.get("service_key", "")

    async def upload(self, file_data, path, mime_type="", metadata=None):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def upload_from_url(self, source_url, path, metadata=None):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def download(self, cloud_path):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def get_url(self, cloud_path, expiry_seconds=3600):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def list_assets(self, prefix):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def delete(self, cloud_path):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")

    async def exists(self, cloud_path):
        raise NotImplementedError("SupabaseStorage: aguardando configuração")


# === FACTORY ===

def get_storage_provider(provider: str = None, config: dict = None) -> CloudStorageBase:
    """
    Factory para obter o provider de storage configurado.

    Args:
        provider: "local", "google_drive", "supabase", "cloudflare_r2"
        config: configuração do provider

    Returns:
        Instância do provider
    """
    if config is None:
        config = {}

    provider = provider or os.getenv("CLOUD_PROVIDER", "local")

    providers = {
        "local": LocalStorage,
        "google_drive": GoogleDriveStorage,
        "supabase": SupabaseStorage,
        # "cloudflare_r2": CloudflareR2Storage,  # TODO
        # "backblaze_b2": BackblazeB2Storage,    # TODO
    }

    provider_class = providers.get(provider)
    if not provider_class:
        raise ValueError(
            f"Provider '{provider}' não suportado. "
            f"Opções: {list(providers.keys())}"
        )

    return provider_class(config)
