"""
CIS Core — Asset Manager
Gerencia o ciclo de vida completo dos assets de um projeto de vídeo.

Responsabilidades:
- Criar e gerenciar projetos
- Guardar imagens geradas (direto da URL da API)
- Guardar vídeos animados (direto da URL da API)
- Manter manifest atualizado
- Fornecer URLs organizados para edição

Uso:
    from core.cloud_storage import get_storage_provider
    from core.asset_manager import AssetManager

    storage = get_storage_provider("google_drive", config)
    manager = AssetManager(storage)

    project = await manager.create_project("teclado_gamer", "Vídeo viral teclado mecânico")
    asset = await manager.store_image_from_url(
        project_id=project.project_id,
        source_url="https://images.upsampler.com/...",
        scene="cena_1",
        prompt="A mechanical gaming keyboard exploding..."
    )
"""

import uuid
import json
from typing import Optional, List, Dict
from datetime import datetime

from core.cloud_storage import (
    CloudStorageBase,
    CloudAsset,
    ProjectManifest,
    AssetType,
)


class AssetManager:
    """Gerencia todo o ciclo de vida dos assets de um projeto."""

    def __init__(self, storage: CloudStorageBase):
        self.storage = storage
        self._manifests: Dict[str, ProjectManifest] = {}

    # === PROJETOS ===

    async def create_project(self, name: str, description: str = "") -> ProjectManifest:
        """Cria um novo projeto e inicializa o manifest."""
        project_id = f"proj_{uuid.uuid4().hex[:8]}_{name.lower().replace(' ', '_')[:20]}"

        manifest = ProjectManifest(
            project_id=project_id,
            name=name,
            description=description,
        )

        # Guardar manifest no cloud
        manifest_path = f"projects/{project_id}/manifest.json"
        await self.storage.upload(
            manifest.to_json().encode("utf-8"),
            manifest_path,
            mime_type="application/json",
        )

        self._manifests[project_id] = manifest
        return manifest

    async def get_project(self, project_id: str) -> Optional[ProjectManifest]:
        """Carrega manifest de um projeto do cloud."""
        if project_id in self._manifests:
            return self._manifests[project_id]

        manifest_path = f"projects/{project_id}/manifest.json"
        try:
            data = await self.storage.download(manifest_path)
            manifest = ProjectManifest.from_dict(json.loads(data))
            self._manifests[project_id] = manifest
            return manifest
        except Exception:
            return None

    async def _save_manifest(self, project_id: str):
        """Persiste manifest atualizado no cloud."""
        manifest = self._manifests.get(project_id)
        if not manifest:
            return

        manifest.updated_at = datetime.utcnow().isoformat()
        manifest_path = f"projects/{project_id}/manifest.json"
        await self.storage.upload(
            manifest.to_json().encode("utf-8"),
            manifest_path,
            mime_type="application/json",
        )

    # === IMAGENS ===

    async def store_image_from_url(
        self,
        project_id: str,
        source_url: str,
        scene: str,
        prompt: str = "",
        model: str = "",
        variant: str = "principal",
        filename: str = "",
    ) -> CloudAsset:
        """
        Guarda uma imagem gerada diretamente a partir da URL da API.
        Zero downloads locais — URL → Cloud diretamente.

        Args:
            project_id: ID do projeto
            source_url: URL da imagem (ex: URL do Upsampler CDN)
            scene: identificador da cena (ex: "cena_1")
            prompt: prompt usado para gerar a imagem
            model: modelo usado (ex: "nano_banana_2")
            variant: "principal", "dinamica", "backup"
            filename: nome do ficheiro (auto-gerado se vazio)
        """
        if not filename:
            ext = "png"
            if "webp" in source_url:
                ext = "webp"
            elif "jpg" in source_url or "jpeg" in source_url:
                ext = "jpg"
            filename = f"{scene}_{variant}.{ext}"

        cloud_path = f"projects/{project_id}/images/{filename}"

        metadata = {
            "scene": scene,
            "prompt": prompt,
            "model": model,
            "variant": variant,
            "source_url": source_url,
            "stage": "image_generation",
        }

        asset = await self.storage.upload_from_url(
            source_url, cloud_path, metadata=metadata
        )
        asset.project_id = project_id
        asset.asset_type = AssetType.IMAGE
        asset.metadata = metadata

        # Atualizar manifest
        manifest = await self.get_project(project_id)
        if manifest:
            manifest.add_asset(asset)
            await self._save_manifest(project_id)

        return asset

    async def store_image_from_bytes(
        self,
        project_id: str,
        image_data: bytes,
        scene: str,
        prompt: str = "",
        model: str = "",
        mime_type: str = "image/png",
        filename: str = "",
    ) -> CloudAsset:
        """Guarda uma imagem a partir de bytes (para APIs que retornam bytes)."""
        if not filename:
            ext = mime_type.split("/")[-1] if "/" in mime_type else "png"
            filename = f"{scene}.{ext}"

        cloud_path = f"projects/{project_id}/images/{filename}"

        metadata = {
            "scene": scene,
            "prompt": prompt,
            "model": model,
            "stage": "image_generation",
        }

        asset = await self.storage.upload(
            image_data, cloud_path,
            mime_type=mime_type, metadata=metadata
        )
        asset.project_id = project_id
        asset.asset_type = AssetType.IMAGE
        asset.metadata = metadata

        manifest = await self.get_project(project_id)
        if manifest:
            manifest.add_asset(asset)
            await self._save_manifest(project_id)

        return asset

    # === VÍDEOS ===

    async def store_video_from_url(
        self,
        project_id: str,
        source_url: str,
        scene: str,
        animation_prompt: str = "",
        model: str = "",
        duration_seconds: float = 5.0,
        filename: str = "",
    ) -> CloudAsset:
        """
        Guarda um vídeo animado a partir da URL da API.
        URL → Cloud diretamente.
        """
        if not filename:
            filename = f"{scene}_animated.mp4"

        cloud_path = f"projects/{project_id}/videos/{filename}"

        metadata = {
            "scene": scene,
            "animation_prompt": animation_prompt,
            "model": model,
            "duration_seconds": duration_seconds,
            "stage": "animation",
        }

        asset = await self.storage.upload_from_url(
            source_url, cloud_path, metadata=metadata
        )
        asset.project_id = project_id
        asset.asset_type = AssetType.VIDEO
        asset.metadata = metadata

        manifest = await self.get_project(project_id)
        if manifest:
            manifest.add_asset(asset)
            await self._save_manifest(project_id)

        return asset

    # === ÁUDIO ===

    async def store_audio_from_url(
        self,
        project_id: str,
        source_url: str,
        audio_type: str = "voiceover",
        filename: str = "",
        metadata: dict = None,
    ) -> CloudAsset:
        """Guarda ficheiro de áudio (voiceover, música, SFX)."""
        if not filename:
            filename = f"{audio_type}.mp3"

        cloud_path = f"projects/{project_id}/audio/{filename}"
        meta = metadata or {}
        meta["audio_type"] = audio_type
        meta["stage"] = "audio"

        asset = await self.storage.upload_from_url(
            source_url, cloud_path, metadata=meta
        )
        asset.project_id = project_id
        asset.asset_type = AssetType.AUDIO
        asset.metadata = meta

        manifest = await self.get_project(project_id)
        if manifest:
            manifest.add_asset(asset)
            await self._save_manifest(project_id)

        return asset

    # === CONSULTAS ===

    async def get_scene_assets(self, project_id: str, scene: str) -> Dict[str, List[CloudAsset]]:
        """Retorna todos os assets de uma cena, organizados por tipo."""
        manifest = await self.get_project(project_id)
        if not manifest:
            return {}

        scene_assets = manifest.get_assets_by_scene(scene)
        result = {"images": [], "videos": [], "audio": []}
        for asset in scene_assets:
            if asset.asset_type == AssetType.IMAGE:
                result["images"].append(asset)
            elif asset.asset_type == AssetType.VIDEO:
                result["videos"].append(asset)
            elif asset.asset_type == AssetType.AUDIO:
                result["audio"].append(asset)

        return result

    async def get_all_images(self, project_id: str) -> List[CloudAsset]:
        """Retorna todas as imagens do projeto."""
        manifest = await self.get_project(project_id)
        return manifest.get_assets_by_type(AssetType.IMAGE) if manifest else []

    async def get_all_videos(self, project_id: str) -> List[CloudAsset]:
        """Retorna todos os vídeos do projeto."""
        manifest = await self.get_project(project_id)
        return manifest.get_assets_by_type(AssetType.VIDEO) if manifest else []

    async def export_timeline(self, project_id: str) -> Dict:
        """
        Exporta dados organizados para montar a timeline do vídeo.
        Retorna URLs de todos os assets organizados por cena e ordem.
        """
        manifest = await self.get_project(project_id)
        if not manifest:
            return {}

        scenes = {}
        for asset in manifest.assets:
            scene = asset.metadata.get("scene", "unknown")
            if scene not in scenes:
                scenes[scene] = {"images": [], "videos": [], "audio": []}

            url = await self.storage.get_url(asset.cloud_path)

            entry = {
                "id": asset.id,
                "url": url,
                "filename": asset.filename,
                "metadata": asset.metadata,
            }

            if asset.asset_type == AssetType.IMAGE:
                scenes[scene]["images"].append(entry)
            elif asset.asset_type == AssetType.VIDEO:
                scenes[scene]["videos"].append(entry)
            elif asset.asset_type == AssetType.AUDIO:
                scenes[scene]["audio"].append(entry)

        return {
            "project_id": project_id,
            "project_name": manifest.name,
            "scenes": scenes,
            "total_assets": len(manifest.assets),
            "pipeline_state": manifest.pipeline_state,
        }

    # === PIPELINE STATE ===

    async def update_pipeline_state(
        self, project_id: str, stage: int, data: dict = None
    ):
        """Atualiza o estado do pipeline no manifest."""
        manifest = await self.get_project(project_id)
        if manifest:
            manifest.pipeline_state["current_stage"] = stage
            manifest.pipeline_state["last_updated"] = datetime.utcnow().isoformat()
            if data:
                manifest.pipeline_state.update(data)
            await self._save_manifest(project_id)
