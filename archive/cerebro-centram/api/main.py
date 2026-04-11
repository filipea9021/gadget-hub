"""
API REST — Cérebro Centram.

Expõe todas as skills e o orquestrador via HTTP.
Esta API é consumida pelo n8n Cloud, pelo dashboard web,
e por qualquer cliente que precise das skills.

Endpoints:
    POST /api/brain           → Cérebro Central (comando natural)
    POST /api/skills/{name}   → Executar skill específica
    GET  /api/status           → Status de todas as skills
    GET  /api/health           → Health check
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import brain, skills, status
from config.settings import Settings
from core.orchestrator import CerebroCentral


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o Cérebro Central ao arrancar a API."""
    settings = Settings()
    app.state.settings = settings
    app.state.cerebro = CerebroCentral(settings)
    yield


app = FastAPI(
    title="Cérebro Centram API",
    description=(
        "API REST do sistema autónomo de IA multi-agente. "
        "Pesquisa produtos, gera conteúdo, processa imagens, "
        "publica no Shopify e lança campanhas de marketing."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permite n8n, dashboard, e qualquer frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registar routers
app.include_router(brain.router, prefix="/api", tags=["Cérebro Central"])
app.include_router(skills.router, prefix="/api", tags=["Skills"])
app.include_router(status.router, prefix="/api", tags=["Sistema"])


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Redireciona para a documentação."""
    return {
        "mensagem": "Cérebro Centram API ativa",
        "docs": "/docs",
        "status": "/api/status",
    }
