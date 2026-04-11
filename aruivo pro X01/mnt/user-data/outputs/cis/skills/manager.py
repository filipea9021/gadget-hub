"""
CIS — Skill Manager
Carrega, indexa e roteia para skills disponíveis.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SkillInfo:
    name: str
    description: str
    path: str
    category: str  # video, content, image, seo, library


SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")


class SkillManager:
    def __init__(self):
        self.skills: dict[str, SkillInfo] = {}
        self._load_skills()

    def _load_skills(self):
        """Carrega metadados de todas as skills disponíveis."""
        if not os.path.isdir(SKILLS_DIR):
            return
        for category in os.listdir(SKILLS_DIR):
            skill_md = os.path.join(SKILLS_DIR, category, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            name, desc = self._parse_frontmatter(skill_md)
            if name:
                self.skills[name] = SkillInfo(
                    name=name,
                    description=desc,
                    path=skill_md,
                    category=category,
                )

    def _parse_frontmatter(self, path: str) -> tuple[str, str]:
        """Extrai name e description do frontmatter YAML."""
        name = ""
        desc = ""
        in_frontmatter = False
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line == "---" and not in_frontmatter:
                    in_frontmatter = True
                    continue
                if line == "---" and in_frontmatter:
                    break
                if in_frontmatter:
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip()
        return name, desc

    def get_skill(self, name: str) -> Optional[SkillInfo]:
        return self.skills.get(name)

    def get_by_category(self, category: str) -> list[SkillInfo]:
        return [s for s in self.skills.values() if s.category == category]

    def find_relevant(self, keywords: list[str]) -> list[SkillInfo]:
        """Busca skills relevantes baseado em palavras-chave."""
        results = []
        for skill in self.skills.values():
            desc_lower = skill.description.lower()
            if any(kw.lower() in desc_lower for kw in keywords):
                results.append(skill)
        return results

    def read_skill(self, name: str) -> Optional[str]:
        """Lê conteúdo completo de uma skill."""
        skill = self.get_skill(name)
        if not skill:
            return None
        with open(skill.path, "r") as f:
            return f.read()

    def list_all(self) -> dict[str, list[str]]:
        """Lista todas as skills por categoria."""
        by_cat = {}
        for skill in self.skills.values():
            by_cat.setdefault(skill.category, []).append(skill.name)
        return by_cat


# Singleton
skill_manager = SkillManager()
