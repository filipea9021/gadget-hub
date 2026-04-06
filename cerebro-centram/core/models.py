"""
Modelos de dados compartilhados entre todas as skills.
Define a linguagem comum do sistema.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Task(BaseModel):
    """Uma tarefa que pode ser executada por uma skill."""
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    description: str
    skill: str  # qual skill deve executar
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def complete(self, result: dict[str, Any]) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error


class ProjectBrief(BaseModel):
    """Briefing de um projeto para a Skill Dev."""
    name: str
    description: str
    project_type: str = "landing_page"  # landing_page, api, fullstack, component
    tech_stack: list[str] = Field(default_factory=lambda: ["next.js", "tailwind", "typescript"])
    features: list[str] = Field(default_factory=list)
    style_preferences: Optional[str] = None
    reference_urls: list[str] = Field(default_factory=list)
    target_audience: Optional[str] = None


class GeneratedFile(BaseModel):
    """Um arquivo gerado pela Skill Dev."""
    path: str  # caminho relativo dentro do projeto
    content: str
    language: str  # extensão / tipo
    description: str


class ProjectOutput(BaseModel):
    """Output completo de um projeto gerado."""
    brief: ProjectBrief
    files: list[GeneratedFile] = Field(default_factory=list)
    structure: str = ""  # tree de diretórios
    setup_instructions: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
