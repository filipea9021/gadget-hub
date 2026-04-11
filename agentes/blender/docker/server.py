"""
=====================================================
BLENDER RENDER SERVER — API REST
=====================================================
Recebe jobs do Agente Blender (Node.js), executa renders
no Blender headless, e retorna resultados.

Endpoints:
  GET  /api/health          → Status do servidor
  POST /api/jobs            → Submeter novo job de render
  GET  /api/jobs/{job_id}   → Verificar status de um job
  GET  /api/jobs            → Listar todos os jobs
  DELETE /api/jobs/{job_id} → Cancelar job

Execução:
  python3 server.py
  uvicorn server:app --host 0.0.0.0 --port 8585
=====================================================
"""

import asyncio
import json
import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =====================================================
# CONFIGURAÇÃO
# =====================================================

BLENDER_BIN = os.getenv("BLENDER_BIN", "blender")
SCRIPTS_DIR = Path(os.getenv("SCRIPTS_DIR", "/app/scripts"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/app/output"))
JOBS_DIR = Path(os.getenv("JOBS_DIR", "/app/jobs"))
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
API_KEY = os.getenv("BLENDER_API_KEY", None)
PORT = int(os.getenv("PORT", "8585"))

# Garantir diretórios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# MODELOS
# =====================================================

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RenderJobRequest(BaseModel):
    jobId: str
    product: dict
    template: str
    renders: list
    config: dict = {}


class JobInfo(BaseModel):
    id: str
    externalId: str
    status: JobStatus
    product: dict
    template: str
    renders: list = []
    animations: list = []
    error: Optional[str] = None
    renderTimeMs: int = 0
    createdAt: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None


# =====================================================
# JOB MANAGER
# =====================================================

class JobManager:
    """Gerencia fila e execução de jobs de render."""

    def __init__(self):
        self.jobs: dict[str, JobInfo] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active_count = 0
        self.stats = {
            "totalJobs": 0,
            "completedJobs": 0,
            "failedJobs": 0,
            "totalRenderTimeMs": 0
        }

    async def add_job(self, request: RenderJobRequest) -> JobInfo:
        """Adicionar novo job à fila."""
        internal_id = str(uuid.uuid4())[:8]

        job = JobInfo(
            id=internal_id,
            externalId=request.jobId,
            status=JobStatus.QUEUED,
            product=request.product,
            template=request.template,
            createdAt=datetime.now().isoformat()
        )

        self.jobs[internal_id] = job
        self.stats["totalJobs"] += 1

        # Salvar definição do job para o Blender
        job_file = JOBS_DIR / f"{internal_id}.json"
        with open(job_file, 'w') as f:
            json.dump({
                "jobId": internal_id,
                "product": request.product,
                "template": request.template,
                "renders": request.renders,
                "config": request.config
            }, f, indent=2)

        await self.queue.put(internal_id)
        return job

    async def process_queue(self):
        """Loop principal — processa jobs da fila."""
        while True:
            if self.active_count >= MAX_CONCURRENT_JOBS:
                await asyncio.sleep(1)
                continue

            try:
                job_id = await asyncio.wait_for(self.queue.get(), timeout=5)
            except asyncio.TimeoutError:
                continue

            self.active_count += 1
            asyncio.create_task(self._execute_job(job_id))

    async def _execute_job(self, job_id: str):
        """Executar um job no Blender."""
        job = self.jobs.get(job_id)
        if not job:
            self.active_count -= 1
            return

        job.status = JobStatus.PROCESSING
        job.startedAt = datetime.now().isoformat()
        start_time = time.time()

        try:
            job_file = str(JOBS_DIR / f"{job_id}.json")

            # Determinar script: cinematic ou standard
            with open(job_file, 'r') as f:
                job_data = json.load(f)

            is_cinematic = job_data.get('config', {}).get('cinematic', False)

            if is_cinematic:
                render_script = str(SCRIPTS_DIR / "cinematic_engine.py")
                # Extrair dados cinematicos de renders[0].cinematic para nivel raiz
                renders = job_data.get('renders', [])
                if renders and 'cinematic' in renders[0]:
                    cin_data = renders[0]['cinematic']
                    cin_data['productInfo'] = job_data.get('product', {})
                    cin_data['objectType'] = cin_data.get('objectType', 'product')
                    cin_data['productTemplate'] = self._detect_template(
                        job_data.get('product', {}).get('category', '')
                    )
                    job_data['cinematic'] = cin_data
                    job_data['outputFolder'] = renders[0].get(
                        'outputFolder', job_data.get('product', {}).get('sku', 'cinematic')
                    )
                    # Reescrever job file com dados reestruturados
                    with open(job_file, 'w') as f:
                        json.dump(job_data, f, indent=2)

                print(f"[SERVER] Job {job_id}: usando CINEMATIC engine")
            else:
                render_script = str(SCRIPTS_DIR / "render_engine.py")
                print(f"[SERVER] Job {job_id}: usando STANDARD engine")

            # Executar Blender headless (timeout maior para video)
            timeout = 1800 if is_cinematic else 600  # 30 min cinematic, 10 min standard
            process = await asyncio.create_subprocess_exec(
                BLENDER_BIN,
                "--background",
                "--python", render_script,
                "--", job_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(OUTPUT_DIR)
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            if process.returncode == 0:
                # Ler resultados
                result_file = job_file.replace('.json', '_result.json')
                if os.path.exists(result_file):
                    with open(result_file, 'r') as f:
                        results = json.load(f)

                    job.renders = results.get('renders', [])
                    job.animations = results.get('animations', [])
                    job.renderTimeMs = results.get('renderTimeMs', 0)
                    job.status = JobStatus.COMPLETED

                    self.stats["completedJobs"] += 1
                    self.stats["totalRenderTimeMs"] += job.renderTimeMs
                else:
                    job.status = JobStatus.FAILED
                    job.error = "Arquivo de resultado não encontrado"
                    self.stats["failedJobs"] += 1
            else:
                job.status = JobStatus.FAILED
                job.error = stderr.decode()[:500] if stderr else "Blender retornou erro"
                self.stats["failedJobs"] += 1

        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error = "Timeout: render excedeu 10 minutos"
            self.stats["failedJobs"] += 1

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)[:500]
            self.stats["failedJobs"] += 1

        finally:
            elapsed = int((time.time() - start_time) * 1000)
            if not job.renderTimeMs:
                job.renderTimeMs = elapsed
            job.completedAt = datetime.now().isoformat()
            self.active_count -= 1

    @staticmethod
    def _detect_template(category: str) -> str:
        """Detectar template de produto baseado na categoria."""
        templates = {
            'smartwatch': 'wearable_watch',
            'watch': 'wearable_watch',
            'smartphone': 'smartphone',
            'phone': 'smartphone',
            'earbuds': 'earbuds_tws',
            'headphones': 'headphones',
            'speaker': 'speaker_portable',
            'drone': 'drone',
            'tablet': 'tablet',
            'laptop': 'laptop',
        }
        cat_lower = category.lower()
        for key, template in templates.items():
            if key in cat_lower:
                return template
        return 'generic_product'

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Buscar job por ID interno ou externo."""
        if job_id in self.jobs:
            return self.jobs[job_id]
        # Buscar por ID externo
        for j in self.jobs.values():
            if j.externalId == job_id:
                return j
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancelar job."""
        job = self.get_job(job_id)
        if job and job.status in (JobStatus.QUEUED, JobStatus.PROCESSING):
            job.status = JobStatus.CANCELLED
            return True
        return False


# =====================================================
# API FastAPI
# =====================================================

app = FastAPI(
    title="Gadget Hub — Blender Render Server",
    version="1.0.0",
    description="API para renderização 3D de produtos via Blender headless"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

job_manager = JobManager()


@app.on_event("startup")
async def startup():
    """Iniciar processador de fila."""
    asyncio.create_task(job_manager.process_queue())
    print(f"[SERVER] Blender Render Server rodando na porta {PORT}")
    print(f"[SERVER] Max jobs simultâneos: {MAX_CONCURRENT_JOBS}")
    print(f"[SERVER] Output dir: {OUTPUT_DIR}")

    # Verificar Blender
    try:
        result = subprocess.run([BLENDER_BIN, "--version"], capture_output=True, text=True)
        version = result.stdout.strip().split('\n')[0] if result.stdout else "desconhecida"
        print(f"[SERVER] Blender: {version}")
    except FileNotFoundError:
        print("[SERVER] ⚠️ Blender não encontrado — modo demo ativo")


# --- Health ---
@app.get("/api/health")
async def health():
    """Status do servidor."""
    try:
        result = subprocess.run([BLENDER_BIN, "--version"], capture_output=True, text=True, timeout=5)
        blender_ok = result.returncode == 0
        blender_version = result.stdout.strip().split('\n')[0] if result.stdout else None
    except Exception:
        blender_ok = False
        blender_version = None

    return {
        "status": "ok",
        "blenderAvailable": blender_ok,
        "blenderVersion": blender_version,
        "maxConcurrentJobs": MAX_CONCURRENT_JOBS,
        "activeJobs": job_manager.active_count,
        "queuedJobs": job_manager.queue.qsize(),
        "stats": job_manager.stats,
        "timestamp": datetime.now().isoformat()
    }


# --- Submeter Job ---
@app.post("/api/jobs")
async def create_job(request: RenderJobRequest):
    """Submeter novo job de render."""
    job = await job_manager.add_job(request)
    return {
        "jobId": job.id,
        "externalId": job.externalId,
        "status": job.status,
        "message": f"Job enfileirado — posição na fila: {job_manager.queue.qsize()}"
    }


# --- Status do Job ---
@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Verificar status de um job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")

    return {
        "jobId": job.id,
        "externalId": job.externalId,
        "status": job.status,
        "product": job.product,
        "renders": job.renders,
        "animations": job.animations,
        "error": job.error,
        "renderTimeMs": job.renderTimeMs,
        "createdAt": job.createdAt,
        "startedAt": job.startedAt,
        "completedAt": job.completedAt
    }


# --- Listar Jobs ---
@app.get("/api/jobs")
async def list_jobs(status: Optional[str] = None, limit: int = 50):
    """Listar jobs."""
    jobs = list(job_manager.jobs.values())

    if status:
        jobs = [j for j in jobs if j.status == status]

    # Ordenar por data de criação (mais recente primeiro)
    jobs.sort(key=lambda j: j.createdAt, reverse=True)

    return {
        "total": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "externalId": j.externalId,
                "status": j.status,
                "product": j.product.get("name", "?"),
                "renderTimeMs": j.renderTimeMs,
                "createdAt": j.createdAt,
                "completedAt": j.completedAt
            }
            for j in jobs[:limit]
        ]
    }


# --- Cancelar Job ---
@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancelar um job."""
    success = job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job não encontrado ou não cancelável")
    return {"status": "cancelled", "jobId": job_id}


# --- Estatísticas ---
@app.get("/api/stats")
async def stats():
    """Estatísticas do servidor."""
    return {
        **job_manager.stats,
        "activeJobs": job_manager.active_count,
        "queuedJobs": job_manager.queue.qsize(),
        "avgRenderTimeMs": (
            job_manager.stats["totalRenderTimeMs"] // max(job_manager.stats["completedJobs"], 1)
        )
    }


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
